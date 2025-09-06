# Copilot Workspace Instructions (SIFU)

Concise rules so AI assistants produce changes consistent with this repo.

## 1. Arquitectura / Dominio
- Backend: FastAPI en `main.py` (todos los endpoints) + lógica agregada en `services.py` y procesadores (`brou_processor.py`, `excel_processor.py`, `exchange_rate_*`).
- Datos: PostgreSQL (en dev puede ser sqlite para tests) vía SQLAlchemy (`database.py`, modelos simples). Cachés en memoria para BCU/BROU (`bcu_cache`, `brou_cache`) protegidos por `_cache_lock`.
- Frontend: React + Vite en `frontend/` con paneles modulares (UI, UR, Exchange, BROU, Dashboard). Uso de i18n; no introducir dependencias pesadas.
- Deploy: GitHub Pages para frontend; backend se publica como imagen Docker (workflow unificado `ci-cd.yml`). Variable crítica de build: secret `VITE_PUBLIC_API_URL` normalizado a `.../api`.

## 2. Flujo de CI/CD
- Único workflow: `.github/workflows/ci-cd.yml` con jobs: security (pip-audit, npm audit), tests backend/frontend, `tunnel-guard`, build imagen, build+deploy frontend, summary.
- Build frontend condicionado a: push a `master` o dispatch con `force_frontend_deploy=true` y guard (`tunnel-guard`). Override manual: `override_tunnel_guard=true`.
- Imagen backend taggeada: `latest`, fecha (`YYYY-MM-DD` y `YYYYMMDD`), SHA.

## 3. Patrones Backend
- Respuestas: usar modelos/estructuras ya centralizadas (mensajes y textos en `constants.py`). No hardcodear mensajes repetidos; si faltan, añadir constante nueva siguiendo convención `MSG_*`.
- Health / métricas: endpoints `/api/health/*`, `/api/metrics*`, y avanzado en `health_checks.py`. Al añadir checks usar `HealthChecker.add_check` para caching de 30s.
- Caché BROU/BCU: actualizar vía `_update_brou_cache()` y `_update_bcu_cache()`; no acceder directamente a variables globales sin `_cache_lock`.
- Endpoints largos: mantener estilo actual (docstring claro, validaciones con `InputValidator` y `SecurityValidator`). Reusar servicios (`UIService`, `URService`, `ExchangeRateService`).
- Jobs pesados: usar patrón job async (ver `exchange_rate_refresh_async` + `JobManager`). Si agregas uno, seguir status keys (`pending|running|success|error`).

## 4. Patrones Frontend
- API base viene de `import.meta.env.VITE_PUBLIC_API_URL`; siempre añadir `/api` normalizado del backend (el build ya lo hace). Para nuevas llamadas crear servicio en `frontend/src/services/` siguiendo estilo existente.
- Estado y polling: ver `App.jsx` (poll de jobs). Reusar hooks (`useHourlySyncedUpdate`). Evitar duplicar lógica de formateo de fechas (hay utilidades en tests / helpers).
- I18n: llamar `t(key)` con fallback; para nuevo texto crear key en archivos de locales (o fallback español si imprescindible), no hardcodear cadenas largas.
- No romper retro‑compat: `/api/brou/current` debe seguir aceptando respuesta lista simple si no `full=true`.

## 5. Seguridad / Validación
- Validaciones de entrada vía `InputValidator` y `SecurityValidator` (inyección). Siempre validar rango/formatos en endpoints nuevos antes de queries.
- Rate limiting y circuit breaker ya aplicados por middlewares; no duplicar lógica en endpoints.

## 6. Testing
- Backend tests: `pytest` con flag `SIFU_SKIP_BOOTSTRAP=1` para rapidez. Añadir tests nuevos en `tests/` siguiendo estilo (uso de `TestClient`).
- Frontend tests (Jest + RTL) ya robustos contra errores de fecha; reutilizar helpers en `frontend/src/test/setup.jsx`.
- Evitar introducir sleeps largos; preferir polling loops con timeouts cortos (ver patrón en `App.jsx` para jobs).

## 7. Mensajes y Constantes
- Centralización: si devuelves texto al usuario/cliente, busca en `constants.py` primero. Si creas uno nuevo, mantener prefijo (`MSG_...`) y agrupar semánticamente.
- No duplicar strings de error genéricas: preferir reutilizar las ya definidas.

## 8. Scripts & Automatización
- PowerShell deployment scripts en `scripts/deploy/` despachan workflows y gestionan túnel (`update_tunnel_secret.ps1`). Mantener idempotencia y chequeos de `gh auth status`.
- Si agregas script: usar funciones helper `Info/Err` coherentes.

## 9. Túnel Dinámico
- Guard en CI (`tunnel-guard`) bloquea build frontend si el secret apunta a URL caída (`*.trycloudflare.com`). Para forzar: `override_tunnel_guard=true` en dispatch.
- Al actualizar túnel, script escribe `.tunnel_last_url.txt`. No commitear (ignorados en `.gitignore`).

## 10. Estilo / Lint
- Python: Ruff + tipado ligero (evitar cambiar firmas existentes salvo necesidad). Prever `pragma: no cover` solo en paths realmente no testeables.
- JS/React: Mantener componentes funcionales, evitar libs de estado adicionales. Seguir convención de paneles (`*Panel.jsx`).

## 11. Extensiones / Dependencias
- Evitar agregar dependencias grandes sin justificar (impacto en CI y bundle Pages). Para scraping/BROU ya existe lógica propia; no introducir frameworks de scraping.
- Cualquier nueva dependencia Python: añadir a `requirements.txt` y (si dev-only) a `requirements-dev.txt`.

## 12. Cambios en API
- Mantener compatibilidad: no eliminar campos existentes sin deprecación. Para expandir respuestas usar flags (`?full=true`) como en BROU.
- Documentar nuevos endpoints con tag adecuado y docstring estilo actual.

## 13. Build Metadata Frontend
- El workflow exporta `VITE_APP_BUILD_SHA` (SHA completo) y `VITE_APP_BUILD_DATE` (run id/number). Usar estos para mostrar en footer si se extiende.

## 14. Pull Requests
- Incluir: breve descripción, impacto en endpoints, notas de migración si aplica. Verificar que CI (security + tests) esté verde.

## 15. Logs (.log / .txt)
- Todo archivo generado `.log` o `.txt` debe residir en `logs/` (el core ya redirige nombres simples vía `secure_logging.py`).
- Al agregar nuevos handlers o scripts que escriban archivos de texto, prefix: `logs/` (ej: `logs/sifu_extra.log`, `logs/export_YYYYMMDD.txt`).
- Si el nombre se pasa sin ruta y termina en `.log` o `.txt`, confirmar que no se requiere fuera de `logs/`; si sí, documentar la excepción en el PR.
- No versionar artefactos de runtime: mantener ignorados en `.gitignore` (solo agregar patrones si aparece necesidad de exclusión específica).

Si una regla parece faltar o un patrón no se deduce del código, abstenerse y preguntar en PR en lugar de inventar.
