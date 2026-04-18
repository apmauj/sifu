# NEXT SESSION PLAN

## P0 - Primera Pendiente: Migración Node 24 en Actions

Meta: eliminar riesgo por deprecación de Node 20 en runners y dejar los workflows listos para Node 24.

Checklist de ejecución:
- [x] Revisar todos los workflows en `.github/workflows/` y listar acciones JS usadas.
- [x] Actualizar versiones de acciones a variantes compatibles con Node 24.
- [x] Ejecutar corrida de validación con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`.
- [x] Confirmar `CI/CD` y `Security Audit` en verde sin warning de deprecación.
- [x] Registrar evidencias y lecciones en roadmap de migración.

Pendientes de cierre operativo (post-checklist):
- [ ] Ejecutar `update-tunnel.yml` en rama y verificar runtime Node 24 en flujo de recuperación.
- [ ] Ejecutar `frontend-backend-link-check.yml` de forma manual con variable habilitante para validar rama.
- [ ] Ejecutar `brou-health-monitor.yml` manualmente y confirmar issue lifecycle bajo Node 24.
- [ ] Abrir y mergear PR `chore/node24-actions-migration-plan` a `master`.

Fecha de preparación: 2025-08-14
Contexto actual: Se añadieron cachés en memoria (BCU/BROU), bootstrap automático en `startup_event`, endpoints de /current sirven desde cache, se eliminó el botón de refresh manual en el frontend y se añadieron tests de caché (aún no ejecutados por bloqueo de dependencias en Python 3.13). `pandas` y `pydantic-core` no instalan wheels precompilados en 3.13 (requieren toolchain). Excel processors fueron endurecidos para funcionar sin pandas (modo degradado), pero para datos reales se necesita pandas.

---
## 1. Objetivos Inmediatos (Próxima Sesión)
1. Entorno estable:
   - Crear / usar venv con Python 3.11 (recomendado) y reinstalar dependencias completas para ejecutar toda la suite.
   - Separar requirements en: `requirements-core.txt`, `requirements-excel.txt` (pandas / openpyxl) y `requirements-dev.txt` (pytest, etc.).
2. Tests:
   - Ajustar tests nuevos de caché para no necesitar pandas / bootstrap completo (mock de funciones internas si hace falta).
   - Añadir tests para: `force_refresh=true` (BCU/BROU) confirmando que se invalida la caché (ya existe uno básico, validar con entorno estable).
   - Test startup bootstrap: simular BD vacía y verificar que se llama a `exchange_rate_excel_processor.refresh_data` (mock). 
3. Documentación:
   - Actualizar `README.md` y `docs/EXCHANGE_RATES_MODULE.md` con: a) caché horario, b) eliminación de refresh manual, c) endpoints `?force_refresh=true`.
   - Añadir sección "Operación" describiendo flujo de actualización automática / histórico vs actual.
4. Observabilidad / Logs:
   - Unificar prefijos de log: `[Bootstrap]`, `[CacheRefresher]`, `[Scheduler]`, `[BCU Cache]`, `[BROU Cache]`.
   - Añadir contador de fallos consecutivos para caché y exponerlo en `/api/health` (opcional).
5. Hardening backend:
   - Mover la lógica de bootstrap de tablas vacías a una función `perform_bootstrap()` invocable en tests.
   - Manejar caso: bootstrap histórico falla → marcar bandera en memoria para reintento diferido (timer de 10 min) sin bloquear arranque.
6. Frontend:
   - Sustituir i18n keys obsoletas de refresh manual en locales (limpieza).
   - Añadir badge visual "AUTO" o tooltip en panel BCU/BROU indicando actualización automática y hora del último update (ya se muestra hora, falta copy i18n). 
7. Calidad / Types:
   - Agregar tipo estructurado para caché (`CachePayload = dict[str, Any]` o @dataclass) y reducir repetición.
   - Considerar TTL configurable vía env: `CACHE_REFRESH_SECONDS=3600`.
8. Seguridad:
   - Limitar acceso a `force_refresh=true` con header secreto opcional (para evitar abuso) o rate limit ligero.

---
## 2. Backlog Prioritario (Después de lo Inmediato)
- Endpoint de estado consolidado `/api/system/status` (combina health, recuentos, timestamps de cache, jobs activos).
- Métricas Prometheus simples (si se añade `prometheus_client`).
- Persistir última actualización de cachés (tabla `cache_metadata`) si se quiere mostrar tras reinicios.
- Reemplazar loop manual de caché por APScheduler job si se desea uniformidad (el loop actual convive con APScheduler opcional).
- Estrategia de retry exponencial para fallos de BCU/BROU (actual ahora es best-effort).
- Integrar test de performance rápido (tiempos de respuesta endpoints críticos).
- Pipeline CI: ejecutar subset sin pandas + job separado con pandas (Python 3.11 matrix).

---
## 3. Riesgos / Bloqueos
| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Python 3.13 sin wheels (pydantic-core/pandas) | Test suite incompleta | Usar Python 3.11 para desarrollo y CI principal |
| Cache loop y APScheduler duplican responsabilidad | Confusión / doble refresh | Consolidar en un solo mecanismo (prefer APScheduler) |
| Bootstrap histórico lento o falla silenciosa | App arranca sin datos | Reintentos escalonados + flag de estado en health |
| Falta de auth en `force_refresh` | Posible abuso | Añadir API key header o rate limit |
| Excel parsing sin pandas (modo degradado) | Datos desactualizados | Registrar warning visible y alerta en dashboard |

---
## 4. Decisiones Tomadas (Resumen)
- Se elimina botón manual de refresh; actualizaciones son programadas + caché horario.
- Caché en memoria simple (dict + timestamp) aceptada como primer paso (sin Redis todavía).
- Excel processors permiten degradación si pandas no está (pero se recomienda pandas para producción).
- Job largo histórico: patrón 202 + polling conservado para usos administrativos futuros.

---
## 5. Propuesta de Estructura de Requirements
```
requirements-core.txt      # fastapi, sqlalchemy, pydantic, requests, etc.
requirements-excel.txt     # pandas, openpyxl, xlrd (solo cuando se haga bootstrap real)
requirements-dev.txt       # pytest, pytest-cov, black, flake8, mypy
```
En producción: instalar core + excel. En CI rápida (lint/tests rápidos): solo core + dev (mock de pandas). Pipeline nightly: incluye excel.

---
## 6. Pasos Concretos (Checklist Ejecutable)
[ ] Crear `requirements-core.txt` y mover dependencias mínimas.
[ ] Crear `requirements-excel.txt` con pandas>=2.2,<2.3, openpyxl, xlrd.
[ ] Ajustar `requirements.txt` para incluir (comentado) referencia a ambos.
[ ] Añadir script `scripts/install-all.sh` (y .ps1) para instalar conjuntos.
[ ] Extraer bootstrap a `bootstrap.py` con función `perform_bootstrap()` y usarla en `startup_event`.
[ ] Añadir tests de bootstrap con BD temporal vacía (sqlite :memory: si posible o archivo temporal).
[ ] Añadir TTL configurable para caché (env var + fallback 3600).
[ ] Añadir endpoint `/api/cache/info` (opcional) mostrando edad y próximo refresh estimado.
[ ] Limpiar i18n claves obsoletas de refresh manual.
[ ] Actualizar docs (README + módulo) con arquitectura actualizada.
[ ] Verificar cobertura cambios nuevos (añadir tests a paquete `tests/`).

---
## 7. Ejemplo de Código Futuro (TTL Caché)
```python
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3300"))  # 55m default
# En endpoint:
age = (datetime.utcnow() - cached['updated_at']).total_seconds()
stale = age > CACHE_TTL_SECONDS
```

---
## 8. Notas Técnicas
- Uso actual de `exchange_rate_excel_processor.refresh_data(None)` en bootstrap: revisar porque la firma espera `db: Session`. Mejor crear sesión local o ajustar firma para gestionar `None` internamente.
- El loop `cache_refresher_loop` no cancela en shutdown explícitamente; opcional añadir bandera global o usar `asyncio.TaskGroup` (Python 3.11+).
- Considerar consolidar logs en JSON para futura ingesta (no urgente).

---
## 9. Cierre
Avance mayor logrado: automatización y eliminación de interacción manual peligrosa. Próximo foco: estabilizar entorno (Python 3.11), robustecer pruebas y limpiar dependencias / documentación para mantener claridad operativa.

---
Fin del plan.
