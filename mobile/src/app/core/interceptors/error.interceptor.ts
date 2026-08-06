import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { TimeoutError, catchError, throwError, timeout } from 'rxjs';

const REQUEST_TIMEOUT_MS = 15000;

export interface ApiError {
  status: number;
  message: string;
  details?: unknown;
}

/**
 * Centralized HTTP resilience: applies a request timeout, normalizes every
 * failure into a consistent {@link ApiError}, and logs it for diagnostics.
 * Understands the backend's RFC 7807 Problem Details payload.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    timeout(REQUEST_TIMEOUT_MS),
    catchError((error: unknown) => {
      const apiError = normalize(error);
      console.error(
        `[HTTP] ${req.method} ${req.urlWithParams} -> ${apiError.status}: ${apiError.message}`,
      );
      return throwError(() => apiError);
    }),
  );
};

function normalize(error: unknown): ApiError {
  if (error instanceof TimeoutError) {
    return { status: 0, message: 'La solicitud tardó demasiado. Revisa tu conexión.' };
  }

  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return { status: 0, message: 'No se pudo conectar con el servidor.' };
    }

    // RFC 7807 Problem Details returned by the backend.
    const problem = error.error as { detail?: string; title?: string } | null;
    const message =
      problem?.detail ??
      problem?.title ??
      defaultMessageFor(error.status);

    return { status: error.status, message, details: error.error };
  }

  return { status: -1, message: 'Ocurrió un error inesperado.' };
}

function defaultMessageFor(status: number): string {
  switch (status) {
    case 400:
    case 422:
      return 'Los datos enviados no son válidos.';
    case 404:
      return 'El recurso solicitado no existe.';
    case 500:
      return 'Error interno del servidor.';
    default:
      return `Error de red (${status}).`;
  }
}
