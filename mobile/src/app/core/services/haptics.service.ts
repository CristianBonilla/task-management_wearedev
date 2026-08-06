import { Injectable } from '@angular/core';
import { Haptics, ImpactStyle, NotificationType } from '@capacitor/haptics';

/**
 * Thin wrapper around @capacitor/haptics.
 *
 * Every call is guarded so it silently no-ops on platforms without haptics
 * support (e.g. the browser during development).
 */
@Injectable({ providedIn: 'root' })
export class HapticsService {
  async impact(style: ImpactStyle = ImpactStyle.Medium): Promise<void> {
    try {
      await Haptics.impact({ style });
    } catch {
      /* not supported on this platform */
    }
  }

  async success(): Promise<void> {
    try {
      await Haptics.notification({ type: NotificationType.Success });
    } catch {
      /* not supported */
    }
  }

  async warning(): Promise<void> {
    try {
      await Haptics.notification({ type: NotificationType.Warning });
    } catch {
      /* not supported */
    }
  }

  async selection(): Promise<void> {
    try {
      await Haptics.selectionStart();
      await Haptics.selectionEnd();
    } catch {
      /* not supported */
    }
  }
}
