import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { IonSkeletonText } from '@ionic/angular/standalone';

@Component({
  selector: 'app-task-skeleton',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [IonSkeletonText],
  template: `
    @for (item of placeholders(); track item) {
      <div class="skeleton-card">
        <div class="row">
          <ion-skeleton-text [animated]="true" class="title"></ion-skeleton-text>
          <ion-skeleton-text [animated]="true" class="badge"></ion-skeleton-text>
        </div>
        <ion-skeleton-text [animated]="true" class="line"></ion-skeleton-text>
        <ion-skeleton-text [animated]="true" class="line short"></ion-skeleton-text>
        <ion-skeleton-text [animated]="true" class="footer"></ion-skeleton-text>
      </div>
    }
  `,
  styleUrl: './task-skeleton.component.scss',
})
export class TaskSkeletonComponent {
  readonly count = input<number>(4);
  placeholders(): number[] {
    return Array.from({ length: this.count() }, (_, i) => i);
  }
}
