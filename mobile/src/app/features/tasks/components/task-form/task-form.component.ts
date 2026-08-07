import { ChangeDetectionStrategy, Component, effect, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  IonButton,
  IonButtons,
  IonContent,
  IonDatetime,
  IonDatetimeButton,
  IonHeader,
  IonIcon,
  IonInput,
  IonItem,
  IonModal,
  IonSelect,
  IonSelectOption,
  IonTextarea,
  IonTitle,
  IonToolbar,
} from '@ionic/angular/standalone';

import {
  CreateTaskPayload,
  STATUS_LABELS,
  Task,
  TaskStatus,
} from '../../../../core/models/task.model';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-task-form',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonContent,
    IonItem,
    IonInput,
    IonTextarea,
    IonSelect,
    IonSelectOption,
    IonDatetime,
    IonDatetimeButton,
    IonModal,
    IonIcon,
  ],
  templateUrl: './task-form.component.html',
  styleUrl: './task-form.component.scss',
})
export class TaskFormComponent {
  private readonly fb = inject(FormBuilder);

  readonly task = input<Task | null>(null);
  readonly save = output<CreateTaskPayload>();
  readonly cancelForm = output<void>();

  protected readonly statuses = Object.values(TaskStatus);
  protected readonly labels = STATUS_LABELS;

  protected readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    status: [TaskStatus.Pendiente],
    due_date: [null as string | null],
  });

  constructor() {
    effect(() => {
      const current = this.task();
      if (current) {
        this.form.reset({
          title: current.title,
          description: current.description ?? '',
          status: current.status,
          due_date: current.due_date
            ? this.toLocalIso(new Date(current.due_date))
            : this.defaultDueDate(),
        });
      } else {
        this.form.reset({
          title: '',
          description: '',
          status: TaskStatus.Pendiente,
          due_date: this.defaultDueDate(),
        });
      }
    });
  }

  protected get isEdit(): boolean {
    return this.task() !== null;
  }

  private defaultDueDate(): string {
    const hours = environment.expiringWindowHours || 48;
    return this.toLocalIso(new Date(Date.now() + hours * 60 * 60 * 1000));
  }

  private toLocalIso(date: Date): string {
    const pad = (n: number) => String(n).padStart(2, '0');
    return (
      `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
      `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    );
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const raw = this.form.getRawValue();
    this.save.emit({
      title: raw.title.trim(),
      description: raw.description.trim(),
      status: raw.status,
      due_date: raw.due_date
        ? new Date(raw.due_date).toISOString()
        : this.defaultDueDate(),
    });
  }
}
