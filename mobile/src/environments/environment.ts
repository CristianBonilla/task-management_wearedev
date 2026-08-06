export const environment = {
  production: false,
  // Django REST API base URL.
  // - Web / iOS simulator: http://localhost:8000/api
  // - Android emulator: use http://10.0.2.2:8000/api (see README)
  apiBaseUrl: 'http://localhost:8000/api',
  // Window (in hours) used to flag tasks as "expiring soon". Must match backend.
  expiringWindowHours: 48,
};
