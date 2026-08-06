import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CreateTaskPayload,
  Task,
  TaskStatus,
  UpdateTaskPayload,
} from '../models/task.model';

/**
 * Data layer for tasks.
 *
 * Owns the reactive UI state via Angular Signals and talks to the Django REST
 * API through HttpClient (RxJS for the async flow). Components read the exposed
 * read-only signals and call the CRUD methods; the service keeps the local
 * state in sync so the UI updates granularly.
 */
@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/tasks`;

  private readonly _tasks = signal<Task[]>([]);
  private readonly _expiring = signal<Task[]>([]);
  private readonly _loading = signal<boolean>(false);
  private readonly _error = signal<string | null>(null);

  readonly tasks = this._tasks.asReadonly();
  readonly expiring = this._expiring.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  readonly totalCount = computed(() => this._tasks().length);
  readonly pendingCount = computed(
    () => this._tasks().filter((t) => t.status === TaskStatus.Pendiente).length,
  );
  readonly completedCount = computed(
    () => this._tasks().filter((t) => t.status === TaskStatus.Completada).length,
  );
  readonly expiringCount = computed(() => this._expiring().length);

  loadTasks(status?: TaskStatus): Observable<Task[]> {
    this._loading.set(true);
    this._error.set(null);
    let params = new HttpParams();
    if (status) {
      params = params.set('status', status);
    }
    return this.http.get<Task[]>(`${this.baseUrl}/`, { params }).pipe(
      tap({
        next: (tasks) => {
          this._tasks.set(tasks);
          this._loading.set(false);
        },
        error: (err) => this.handleError(err),
      }),
    );
  }

  loadExpiring(windowHours: number = environment.expiringWindowHours): Observable<Task[]> {
    const params = new HttpParams().set('window_hours', windowHours);
    return this.http.get<Task[]>(`${this.baseUrl}/expiring/`, { params }).pipe(
      tap({
        next: (tasks) => this._expiring.set(tasks),
        error: (err) => this.handleError(err),
      }),
    );
  }

  createTask(payload: CreateTaskPayload): Observable<Task> {
    return this.http.post<Task>(`${this.baseUrl}/`, payload).pipe(
      tap({
        next: (task) => this._tasks.update((list) => [task, ...list]),
        error: (err) => this.handleError(err),
      }),
    );
  }

  updateTask(id: string, payload: UpdateTaskPayload): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${id}/`, payload).pipe(
      tap({
        next: (updated) => this.replaceInState(updated),
        error: (err) => this.handleError(err),
      }),
    );
  }

  changeStatus(id: string, status: TaskStatus): Observable<Task> {
    return this.http.patch<Task>(`${this.baseUrl}/${id}/status/`, { status }).pipe(
      tap({
        next: (updated) => this.replaceInState(updated),
        error: (err) => this.handleError(err),
      }),
    );
  }

  softDelete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}/`).pipe(
      tap({
        next: () => {
          this._tasks.update((list) => list.filter((t) => t.id !== id));
          this._expiring.update((list) => list.filter((t) => t.id !== id));
        },
        error: (err) => this.handleError(err),
      }),
    );
  }

  private replaceInState(updated: Task): void {
    const apply = (list: Task[]) =>
      list.map((t) => (t.id === updated.id ? updated : t));
    this._tasks.update(apply);
    this._expiring.update((list) =>
      list
        .map((t) => (t.id === updated.id ? updated : t))
        .filter((t) => t.is_expiring),
    );
  }

  private handleError(err: { message?: string }): void {
    this._loading.set(false);
    this._error.set(err?.message ?? 'Error desconocido.');
  }
}
