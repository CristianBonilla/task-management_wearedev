import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import {
  IonIcon,
  IonItem,
  IonItemOption,
  IonItemOptions,
  IonItemSliding,
  IonLabel,
} from '@ionic/angular/standalone';

import { Task, TaskStatus } from '../../../../core/models/task.model';
import { StatusBadgeComponent } from '../status-badge/status-badge.component';

@Component({
  selector: 'app-task-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    DatePipe,
    IonItemSliding,
    IonItem,
    IonItemOptions,
    IonItemOption,
    IonLabel,
    IonIcon,
    StatusBadgeComponent,
  ],
  templateUrl: './task-card.component.html',
  styleUrl: './task-card.component.scss',
})
export class TaskCardComponent {
  readonly task = input.required<Task>();

  readonly complete = output<Task>();
  readonly postpone = output<Task>();
  readonly remove = output<Task>();
  readonly edit = output<Task>();

  protected readonly TaskStatus = TaskStatus;

  onComplete(sliding: IonItemSliding): void {
    void sliding.close();
    this.complete.emit(this.task());
  }

  onPostpone(sliding: IonItemSliding): void {
    void sliding.close();
    this.postpone.emit(this.task());
  }

  onDelete(sliding: IonItemSliding): void {
    void sliding.close();
    this.remove.emit(this.task());
  }
}
