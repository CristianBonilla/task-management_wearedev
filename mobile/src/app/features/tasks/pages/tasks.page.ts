import { ChangeDetectionStrategy, Component, OnInit, computed, inject, signal } from '@angular/core';
import {
  IonContent,
  IonFab,
  IonFabButton,
  IonHeader,
  IonIcon,
  IonLabel,
  IonModal,
  IonRefresher,
  IonRefresherContent,
  IonSegment,
  IonSegmentButton,
  IonTitle,
  IonToolbar,
  ToastController,
} from '@ionic/angular/standalone';
import { ImpactStyle } from '@capacitor/haptics';
import { forkJoin } from 'rxjs';

import {
  CreateTaskPayload,
  Task,
  TaskFilter,
  TaskStatus,
} from '../../../core/models/task.model';
import { HapticsService } from '../../../core/services/haptics.service';
import { TaskService } from '../../../core/services/task.service';
import { TaskCardComponent } from '../components/task-card/task-card.component';
import { TaskFormComponent } from '../components/task-form/task-form.component';
import { TaskSkeletonComponent } from '../components/task-skeleton/task-skeleton.component';

@Component({
  selector: 'app-tasks',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonSegment,
    IonSegmentButton,
    IonLabel,
    IonRefresher,
    IonRefresherContent,
    IonFab,
    IonFabButton,
    IonIcon,
    IonModal,
    TaskCardComponent,
    TaskFormComponent,
    TaskSkeletonComponent,
  ],
  templateUrl: './tasks.page.html',
  styleUrl: './tasks.page.scss',
})
export class TasksPage implements OnInit {
  private readonly taskService = inject(TaskService);
  private readonly haptics = inject(HapticsService);
  private readonly toastCtrl = inject(ToastController);

  readonly tasks = this.taskService.tasks;
  readonly expiring = this.taskService.expiring;
  readonly loading = this.taskService.loading;
  readonly pendingCount = this.taskService.pendingCount;
  readonly completedCount = this.taskService.completedCount;
  readonly expiringCount = this.taskService.expiringCount;

  readonly filter = signal<TaskFilter>('all');
  readonly isModalOpen = signal(false);
  readonly editingTask = signal<Task | null>(null);

  readonly modalBreakpoints = [0, 0.5, 0.8];

  readonly visibleTasks = computed<Task[]>(() => {
    const filter = this.filter();
    if (filter === 'expiring') {
      return this.expiring();
    }
    const all = this.tasks();
    switch (filter) {
      case 'pending':
        return all.filter((t) => t.status === TaskStatus.Pendiente);
      case 'completed':
        return all.filter((t) => t.status === TaskStatus.Completada);
      default:
        return all;
    }
  });

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.taskService.loadTasks().subscribe({ error: () => this.notify('No se pudieron cargar las tareas.', 'danger') });
    this.taskService.loadExpiring().subscribe();
  }

  handleRefresh(event: CustomEvent): void {
    void this.haptics.impact(ImpactStyle.Light);
    forkJoin([this.taskService.loadTasks(), this.taskService.loadExpiring()]).subscribe({
      next: () => (event.target as HTMLIonRefresherElement).complete(),
      error: () => {
        (event.target as HTMLIonRefresherElement).complete();
        this.notify('No se pudo actualizar.', 'danger');
      },
    });
  }

  onFilterChange(value: string | number | undefined): void {
    void this.haptics.selection();
    this.filter.set((value as TaskFilter) ?? 'all');
  }

  trackById(_index: number, task: Task): string {
    return task.id;
  }

  openCreate(): void {
    this.editingTask.set(null);
    this.isModalOpen.set(true);
  }

  openEdit(task: Task): void {
    this.editingTask.set(task);
    this.isModalOpen.set(true);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
    this.editingTask.set(null);
  }

  onSave(payload: CreateTaskPayload): void {
    const editing = this.editingTask();
    const request$ = editing
      ? this.taskService.updateTask(editing.id, payload)
      : this.taskService.createTask(payload);

    request$.subscribe({
      next: () => {
        void this.haptics.success();
        this.taskService.loadExpiring().subscribe();
        this.closeModal();
        this.notify(editing ? 'Tarea actualizada.' : 'Tarea creada.', 'success');
      },
      error: (err: { message?: string }) => this.notify(err?.message ?? 'No se pudo guardar.', 'danger'),
    });
  }

  onComplete(task: Task): void {
    this.taskService.changeStatus(task.id, TaskStatus.Completada).subscribe({
      next: () => {
        void this.haptics.success();
        this.taskService.loadExpiring().subscribe();
      },
      error: (err: { message?: string }) => this.notify(err?.message ?? 'No se pudo completar.', 'danger'),
    });
  }

  onPostpone(task: Task): void {
    this.taskService.changeStatus(task.id, TaskStatus.Pospuesta).subscribe({
      next: () => void this.haptics.impact(),
      error: (err: { message?: string }) => this.notify(err?.message ?? 'No se pudo posponer.', 'danger'),
    });
  }

  onDelete(task: Task): void {
    this.taskService.softDelete(task.id).subscribe({
      next: () => {
        void this.haptics.warning();
        this.notify('Tarea eliminada.', 'medium');
      },
      error: (err: { message?: string }) => this.notify(err?.message ?? 'No se pudo eliminar.', 'danger'),
    });
  }

  private async notify(message: string, color: 'success' | 'danger' | 'medium'): Promise<void> {
    const toast = await this.toastCtrl.create({
      message,
      color,
      duration: 2200,
      position: 'top',
      cssClass: 'app-toast',
    });
    await toast.present();
  }
}
