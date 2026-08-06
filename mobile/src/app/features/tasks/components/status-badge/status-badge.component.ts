import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { STATUS_LABELS, TaskStatus } from '../../../../core/models/task.model';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<span class="badge" [class]="status()">{{ label() }}</span>`,
  styleUrl: './status-badge.component.scss',
})
export class StatusBadgeComponent {
  readonly status = input.required<TaskStatus>();
  readonly label = computed(() => STATUS_LABELS[this.status()]);
}
