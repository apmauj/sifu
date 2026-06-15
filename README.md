# SIFU - Sistema de Índices Financieros del Uruguay

[![Deploy Frontend](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml)
[![Backend CI](https://github.com/apmauj/sifu/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/ci-backend.yml)

Sistema web para consulta de índices financieros y tasas de cambio en Uruguay.

## Arquitectura

| Componente | Hosting | Stack | Costo |
|---|---|---|---|
| Frontend | GitHub Pages | React + Vite | $0/mes |
| Backend | Render Free Tier | FastAPI + Python 3.12 | $0/mes |
| Database | Render (SQLite en /tmp) | SQLAlchemy | $0/mes |
| CI/CD | GitHub Actions | Tests + Deploy automático | $0/mes |

> **Nota**: El backend en Render Free Tier se hiberna tras 15 min de inactividad.
> El primer request puede tardar ~30s (cold start). El frontend muestra un overlay
> informativo mientras el backend despierta.

## Características

- **Backend**: FastAPI con Python 3.12, SQLite, scraping automático de INE/BHU/BCU/BROU
- **Frontend**: React con Vite, Tailwind CSS, soporte offline progresivo
- **Internacionalización**: ES, EN, PT
- **Monitoreo**: Dashboard protegido con TOTP 2FA (health, performance, alerts)
- **CI/CD**: Tests + lint + deploy automático en cada push a `master`

## Prerrequisitos

- Node.js 20+ (para desarrollo frontend y CI)
- Python 3.12+ (para desarrollo backend)
- Git

## Desarrollo Local

### Backend

```bash
# Desde la raíz del repo
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .\.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

El frontend en desarrollo apunta al backend local (`localhost:8000`) via proxy configurado en `vite.config.js`.

### Probar el build de Pages en local

Para reproducir GitHub Pages (base "/sifu/") en local:

```bash
npm --prefix frontend run build
npm --prefix frontend exec npx serve -s dist -l 5174
# Abrir: http://localhost:5174/sifu/
```

## Estructura del Proyecto

```text
.
├── main.py                    # FastAPI app (endpoints + lifespan + middleware)
├── render.yaml                # Configuración de Render
├── runtime.txt                # Versión de Python para Render
├── requirements.txt           # Dependencias Python
├── src/
│   ├── api/routers/           # Rutas modulares (ui, ur, exchange, brou, system)
│   ├── application/           # Lógica de aplicación (totp, alerts, bootstrap, config)
│   ├── domain/                # Modelos, servicios, procesadores Excel/BCU
│   ├── infrastructure/        # DB, auth, metrics, circuit breakers, rate limit
│   └── utils/                 # Constantes, error model
├── frontend/                  # React (Vite + Tailwind CSS)
│   ├── src/
│   │   ├── features/          # ui, ur, exchange, brou, monitoring, dashboard
│   │   └── shared/            # componentes, servicios, contexts, hooks, i18n
│   └── package.json
├── tests/                     # Tests backend (pytest)
├── .github/workflows/         # CI/CD GitHub Actions
└── docs/                      # Documentación adicional
```

## Endpoints API (Resumen)

Ver documentación interactiva en `/docs` (Swagger UI) o `/redoc`.

### Datos financieros:

- `GET /api/ui/latest` - Ultima UI
- `GET /api/ur/latest` - Ultima UR
- `GET /api/brou/current` - Cotizaciones BROU
- `GET /api/exchange-rate/latest` - Cotizaciones BCU/INE
- `GET /api/exchange-rate/currency/{code}` - Cotizacion por moneda
- `POST /api/refresh` - Forzar actualizacion

### Monitoreo (protegido con 2FA TOTP):

- `POST /api/monitoring/verify` - Verificar codigo TOTP de 6 digitos
- `GET /api/monitoring/status` - Dashboard de monitoreo (requiere sesion)
- `GET /api/monitoring/setup` - Generar QR para configurar autenticador (solo development)
- `GET /api/monitoring/metrics` - Metricas de autenticacion
- `DELETE /api/monitoring/session` - Cerrar sesion

### Sistema:

- `GET /api/health` - Health check
- `GET /api/health/advanced` - Chequeos detallados
- `GET /api/metrics` - Metricas de rendimiento

## Despliegue

### Frontend (GitHub Pages)

Se publica automaticamente en cada push a `master` que modifique `frontend/`.

- URL: <https://apmauj.github.io/sifu/>
- La URL del backend se configura via `VITE_PUBLIC_API_URL` (secret del repo)

### Backend (Render)

Render detecta `render.yaml` y despliega automaticamente en cada push a `master`.

- Free tier: 750 horas/mes, hiberna tras 15 min de inactividad
- Health check en `/api/health`
- Variables de entorno sensibles se configuran en Render Dashboard → Environment

#### Variables de entorno requeridas

| Variable | Descripcion | Ejemplo |
|---|---|---|
| `PYTHON_VERSION` | Version de Python | `3.12.4` |
| `PYTHONPATH` | Path del modulo | `/app` |
| `DATABASE_PATH` | Path DB SQLite | `/tmp/sifu_data.db` |
| `ENVIRONMENT` | Entorno de ejecucion | `production` |
| `ALLOW_ORIGINS` | Origins CORS | `https://apmauj.github.io` |
| `SCHEDULER_ENABLED` | Scheduler activo | `true` |

#### Variables de entorno recomendadas

| Variable | Descripcion |
|---|---|
| `MONITORING_TOTP_SECRET` | Secret TOTP para dashboard (si no se setea, se genera uno nuevo en cada deploy) |
| `JWT_SECRET_KEY` | Secret para JWT (auth features) |

### Keep-Alive

El backend en Render Free Tier hiberna tras 15 min de inactividad. Un workflow de GitHub Actions (`brou-health-monitor.yml`) hace ping periodicamente para mantenerlo despierto durante horario laboral (Lun-Vie 7-21 UY).

## Autenticacion 2FA (TOTP)

El acceso al dashboard de monitoreo esta protegido con autenticacion de dos factores (TOTP).

### Setup:

1. Setear `MONITORING_TOTP_SECRET` en Render Dashboard (generar con `python -c "import pyotp; print(pyotp.random_base32())"`)
2. En modo development, acceder a `http://localhost:8000/static/totp-setup.html` para escanear el QR
3. En produccion, usar el secret para configurar manualmente la app de autenticador

### Acceso:

1. Hacer click en el corazon del footer del sitio
2. Ingresar codigo de 6 digitos de la app de autenticador
3. Sesion valida por 1 hora (configurable via `MONITORING_SESSION_HOURS`)

Ver [docs/TOTP_SETUP.md](docs/TOTP_SETUP.md) para instrucciones detalladas.

## Internacionalizacion

Soporte para multiples idiomas (ES, EN, PT). Los archivos de traduccion se sirven desde `frontend/public/i18n` en produccion con fallbacks embebidos en `frontend/src/locales`.

## Testing

```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test

# Lint
cd frontend && npm run lint
```

## Calidad y CI

- **Backend CI**: pytest + ruff + verificacion de migraciones Alembic + check de mensajes duplicados
- **Frontend CI/CD**: ESLint + build + deploy a GitHub Pages
- **Security Audit**: pip-audit semanal
- **BROU Health Monitor**: keep-alive + verificacion de cotizaciones BROU

### Historial y Planificacion

- Para cambios completados y releases: ver `CHANGELOG.md`.
- Para planes operativos: ver `docs/` directory.

## Licencia

Este proyecto esta bajo la Licencia MIT. Ver el archivo `LICENSE` para mas detalles.

---

Desarrollado con amor para Uruguay
