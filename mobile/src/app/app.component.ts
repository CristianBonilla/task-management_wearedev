import { Component } from '@angular/core';
import { IonApp, IonRouterOutlet } from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  add,
  alertCircleOutline,
  calendarOutline,
  checkmarkCircleOutline,
  checkmarkDoneOutline,
  closeOutline,
  createOutline,
  ellipseOutline,
  hourglassOutline,
  listOutline,
  playForwardOutline,
  refreshOutline,
  saveOutline,
  timeOutline,
  trashOutline,
} from 'ionicons/icons';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [IonApp, IonRouterOutlet],
  template: `
    <ion-app>
      <ion-router-outlet></ion-router-outlet>
    </ion-app>
  `,
})
export class AppComponent {
  constructor() {
    addIcons({
      add,
      'alert-circle-outline': alertCircleOutline,
      'calendar-outline': calendarOutline,
      'checkmark-circle-outline': checkmarkCircleOutline,
      'checkmark-done-outline': checkmarkDoneOutline,
      'close-outline': closeOutline,
      'create-outline': createOutline,
      'ellipse-outline': ellipseOutline,
      'hourglass-outline': hourglassOutline,
      'list-outline': listOutline,
      'play-forward-outline': playForwardOutline,
      'refresh-outline': refreshOutline,
      'save-outline': saveOutline,
      'time-outline': timeOutline,
      'trash-outline': trashOutline,
    });
  }
}
