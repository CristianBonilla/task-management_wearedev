# Task Management — Fullstack (Django REST + Ionic/Angular + PostgreSQL)

Solución Fullstack para la gestión de tareas con integración **real** vía API REST entre un backend Django (Clean/Hexagonal Architecture) y una app móvil híbrida Android (Ionic + Angular + Capacitor), con persistencia en PostgreSQL.

```text
task-management_wearedev/
├── backend/            # Django 5 + DRF (Clean/Hexagonal)
├── mobile/             # Ionic 8 + Angular 20 (Standalone + Signals) + Capacitor 8
├── scripts/            # Automatización del build Android (APK)
├── docker-compose.yml  # PostgreSQL + Backend (migraciones automáticas)
└── .env.example        # Variables centralizadas (backend + móvil)
```

---

## 1. Descripción general y decisiones de diseño

### Backend — Clean / Hexagonal Architecture

El backend separa el negocio de los detalles de framework en cuatro capas con dependencias apuntando siempre hacia el dominio (Dependency Inversion):

```text
backend/tasks/
├── domain/            # Núcleo puro (sin Django)
│   ├── entities/          # Entidad Task (dataclass) + invariantes de negocio
│   ├── value_objects/     # TaskStatus (PENDIENTE | COMPLETADA | POSPUESTA)
│   ├── exceptions/        # Errores de dominio con semántica HTTP + RFC 7807
│   └── repositories/      # Puerto TaskRepository (interfaz abstracta)
├── application/       # Casos de uso (orquestación)
│   ├── dtos/              # DTOs inmutables de entrada
│   └── use_cases/         # Create, Update, SoftDelete, List, Get, ChangeStatus, GetExpiring
├── infrastructure/    # Adaptadores concretos
│   ├── models/            # ORM Django + Custom Manager (soft delete)
│   ├── repositories/      # Implementación PostgreSQL del puerto
│   ├── mappers/           # ORM ⇄ entidad de dominio
│   ├── schemas/           # Serializers DRF (validación de I/O)
│   └── migrations/
├── presentation/      # Entrega HTTP
│   ├── views.py           # ViewSet REST (delgado)
│   ├── container.py       # Inyección de dependencias (composition root)
│   ├── identity.py        # Resolución de `created_by`
│   └── exception_handler.py  # Manejador global RFC 7807
└── shared/utils/      # Utilidades transversales (utcnow)
```

**Beneficio:** el dominio y los casos de uso se prueban sin base de datos ni Django (ver `tasks/tests/`), y PostgreSQL/DRF son intercambiables sin tocar el negocio.

### Frontend móvil — Angular 20 (Standalone + Signals)

- **Standalone Components** (sin NgModules), arranque con `bootstrapApplication`.
- **Angular Signals** para el estado reactivo y granular (`signal`, `computed`), complementado con **RxJS** para el flujo HTTP.
- **Data layer desacoplada:** `TaskService` centraliza el estado y consume la API con `HttpClient`.
- Separación por capas: `core/` (modelos, servicios, interceptor) y `features/tasks/` (páginas y componentes).

### Patrones de resiliencia aplicados

| Patrón | Dónde | Detalle |
|--------|-------|---------|
| **RFC 7807 Problem Details** | Backend `exception_handler.py` | Todo error (dominio, validación, 404, 500) devuelve `application/problem+json` con formato uniforme. |
| **Global Exception Handler** | Backend (DRF `EXCEPTION_HANDLER`) | Traduce excepciones de dominio a códigos HTTP sin acoplar el dominio a HTTP. |
| **HTTP Interceptor** | Móvil `error.interceptor.ts` | Timeout de 15 s, normalización de errores y logging centralizado. |
| **Healthcheck + depends_on** | `docker-compose.yml` | El backend espera a que PostgreSQL esté *healthy* antes de migrar. |
| **Soft delete** | Backend (Custom Manager) | Nunca se borra físicamente; se preserva la auditoría. |

---

## 2. Requisitos de sistema

| Herramienta | Versión recomendada | Notas |
|-------------|---------------------|-------|
| **Python** | 3.12+ | Type hints avanzados, dataclasses |
| **Django / DRF** | 5.1 / 3.15 | |
| **PostgreSQL** | 16+ | Driver `psycopg` 3 |
| **Node.js** | 24 (o 20.19+/22.12+) | |
| **Angular** | 20.3 | Standalone + Signals |
| **Ionic** | 8 | |
| **Capacitor** | 8 | `@capacitor/haptics`, `@capacitor/android` |
| **Java JDK** | 17+ | Solo para compilar la APK |
| **Android SDK** | Platform 34+ | Solo para compilar la APK |
| **Docker / Compose** | 24+ / v2 | Opcional (ejecución con un comando) |

---

## 3. Ejecución del Backend

### Opción A — Docker Compose (recomendada, un solo comando)

Levanta PostgreSQL (con volumen persistente) y el backend, que **aplica migraciones automáticamente** al iniciar.

```bash
cp .env.example .env
docker compose up --build
```

- API disponible en `http://localhost:8000/api/`
- PostgreSQL expuesto en `localhost:5432`

### Opción B — Local (sin Docker)

**1) Levantar PostgreSQL** (local o con un contenedor sólo para la BD):

```bash
docker run --name taskdb -e POSTGRES_DB=taskdb -e POSTGRES_USER=taskuser \
  -e POSTGRES_PASSWORD=taskpass -p 5432:5432 -d postgres:16-alpine
```

**2) Configurar variables y entorno:**

```bash
cd backend
cp .env.example .env      # ajusta DATABASE_URL a @localhost si es necesario
python -m venv .venv
# Windows: .\.venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

> Para ejecución local, en `.env` usa `DATABASE_URL=postgres://taskuser:taskpass@localhost:5432/taskdb`.

**3) Migraciones y servidor de desarrollo:**

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**Pruebas del backend** (dominio + casos de uso, sin base de datos):

```bash
pytest
```

### Variables mínimas del backend

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `postgres://taskuser:taskpass@db:5432/taskdb` | Conexión a PostgreSQL (host `db` en Docker, `localhost` en local) |
| `DJANGO_SECRET_KEY` | `change-me` | Clave secreta de Django |
| `DJANGO_DEBUG` | `True` | Modo debug |
| `DJANGO_ALLOWED_HOSTS` | `*` | Hosts permitidos |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8100,...` | Orígenes permitidos para la app |
| `EXPIRING_WINDOW_HOURS` | `48` | Ventana de "próximas a vencer" |
| `DEFAULT_TASK_OWNER` | `system` | Usuario fijo para auditoría |

---

## 4. Ejecución de la App

**1) Instalar dependencias:**

```bash
cd mobile
npm install
```

**2) Configurar la URL de la API** en `mobile/src/environments/environment.ts` (`API_BASE_URL`):

- Navegador / simulador iOS: `http://localhost:8000/api`
- **Emulador Android:** `http://10.0.2.2:8000/api` (el `localhost` del emulador es el propio dispositivo virtual)

**3) Servir en el navegador (desarrollo):**

```bash
ionic serve
# o:  npm start   →   http://localhost:8100
```

### Compilación nativa Android y generación de la APK

Requiere **JDK 17+** y **Android SDK** (`ANDROID_HOME` configurado).

**Automático (script):**

```bash
# Linux / macOS
npm run android:apk         # scripts/build-android.sh

# Windows (PowerShell)
npm run android:apk:win     # scripts/build-android.ps1
```

**Manual (paso a paso con Capacitor CLI + Gradle):**

```bash
cd mobile
npm run build                       # build web (Angular) -> www/
npx cap add android                 # añade la plataforma (solo la primera vez)
npx cap sync android                # copia web + plugins nativos
npx cap build android               # build gestionado por Capacitor
# o directamente con Gradle:
cd android && ./gradlew assembleDebug   # Windows: .\gradlew.bat assembleDebug
```

**Ubicación de la APK generada:**

```text
mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 5. Criterios técnicos

### 5.1 Regla "Próximas a vencer (48 horas)"

Una tarea se considera **próxima a vencer** cuando su fecha de vencimiento cae dentro de una ventana hacia adelante de 48 horas y **no** está completada.

### 5.2 Estrategia de Soft Delete

Se descarta el borrado físico y se marca lógicamente cada tarea con `is_deleted` (booleano) y `deleted_at` (timestamp).

- **Por qué:** preserva la **auditoría** y la integridad histórica; permite recuperación y trazabilidad.
- **Cómo:** un **Custom Manager** (`AliveTaskManager`) excluye las eliminadas por defecto en *todas* las consultas (`TaskModel.objects`), mientras `all_objects` permite acceso total cuando se necesita persistir el propio soft-delete. Así, "excluir eliminadas por defecto" es una garantía a nivel de ORM, no una condición repetida en cada consulta.

### 5.3 Asignación de usuarios

Se eligió la **opción (b): usuario actual fijo simulado**, justificada por el alcance de la prueba (autenticación opcional) y para mantener el MVP ejecutable sin fricción:

- **Backend:** `created_by` se resuelve en `presentation/identity.py`. Si hay una petición autenticada (JWT — SimpleJWT está cableado y listo para producción), se usa ese usuario; si no, se usa `DEFAULT_TASK_OWNER` (`system`). La migración a autenticación real no requiere tocar el dominio.
- **Móvil:** patrón de usuario activo estático desacoplado en `UserService` (`CURRENT_USER_ID = 1`), como única fuente documentada de la identidad simulada.

### 5.4 Catálogo de endpoints REST

Base: `/api/tasks/`

| Método | Ruta | Descripción | Body (JSON) | Respuesta |
|--------|------|-------------|-------------|-----------|
| `GET` | `/api/tasks/` | Lista tareas (excluye eliminadas). Filtro opcional `?status=PENDIENTE\|COMPLETADA\|POSPUESTA` | — | `200` lista de tareas |
| `POST` | `/api/tasks/` | Crea una tarea | `{ title, description?, status?, due_date? }` | `201` tarea creada |
| `GET` | `/api/tasks/{id}/` | Detalle de una tarea | — | `200` / `404` |
| `PATCH` | `/api/tasks/{id}/` | Actualización parcial | `{ title?, description?, status?, due_date? }` | `200` / `404` / `422` |
| `DELETE` | `/api/tasks/{id}/` | Borrado **lógico** (soft delete) | — | `204` |
| `PATCH` | `/api/tasks/{id}/status/` | Cambia el estado | `{ status }` | `200` / `422` |
| `GET` | `/api/tasks/expiring/` | Tareas próximas a vencer. Ventana opcional `?window_hours=48` | — | `200` lista |

**Modelo de tarea (respuesta):**

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "PENDIENTE | COMPLETADA | POSPUESTA",
  "due_date": "ISO-8601 | null",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "created_by": "string",
  "is_expiring": true
}
```

**Formato de error:**

```json
{
  "type": "https://api.taskmanager/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The task is invalid.",
  "instance": "/api/tasks/",
  "errors": { "title": ["Title must not be empty."] }
}
```
