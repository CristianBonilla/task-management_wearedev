import { Injectable } from '@angular/core';

/**
 * Simulated active-user pattern.
 *
 * The technical test allows assignment/ownership to be simulated with a fixed
 * "current user" instead of a full authentication flow. This service is the
 * single, documented source of that identity so the rest of the app never
 * hard-codes it. Swapping this for a real JWT/auth session later only requires
 * changing this provider.
 */
export const CURRENT_USER_ID = 1;

@Injectable({ providedIn: 'root' })
export class UserService {
  readonly currentUserId = CURRENT_USER_ID;
  readonly currentUserName = 'system';
}
