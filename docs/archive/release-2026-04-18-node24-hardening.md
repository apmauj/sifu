# Changelog - 18 de Abril 2026

## Node 24 Migration, CI Stabilization, and Workflow Hardening

Este documento resume los cambios incluidos en la rama `chore/node24-actions-migration-plan` para cerrar la migración de workflows a runtime Node 24 y estabilizar pipelines.

---

## ✅ Cambios de Infraestructura y CI/CD

### Migración de Actions a majors vigentes
Se actualizaron acciones oficiales en workflows activos:

- `actions/checkout`: `v4` -> `v6`
- `actions/upload-artifact`: `v4` -> `v7`
- `actions/deploy-pages`: `v4` -> `v5`
- `actions/github-script`: `v7` -> `v9`

### Opt-in explícito a Node 24
Se añadió `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` en workflows clave para validar comportamiento antes del corte definitivo de Node 20.

Workflows cubiertos:
- `.github/workflows/ci-cd.yml`
- `.github/workflows/security-audit.yml`
- `.github/workflows/update-tunnel.yml`
- `.github/workflows/frontend-backend-link-check.yml`
- `.github/workflows/brou-health-monitor.yml`

### Hardening adicional en CI

- Build frontend determinístico en CI (`npm ci` desde lockfile).
- Ajustes anti-loop en recuperación de túnel/redeploy.
- Corrección de backend tests async en CI:
  - Se eliminó bloqueo de autoload de plugins.
  - Se forzó `--asyncio-mode=auto`.
  - Se excluyó `tests/demo` del comando de regresión.

---

## ✅ Estado de Validación

Evidencia principal:
- CI/CD exitoso (Node24 batch): https://github.com/apmauj/sifu/actions/runs/24614408796
- Security Audit exitoso (Node24 batch): https://github.com/apmauj/sifu/actions/runs/24614409346

Resultado:
- Workflows críticos (`CI/CD` y `Security Audit`) en verde con SHA de la rama de migración.
- Sin warnings activos de deprecación Node 20 en la validación final de esta tanda.

---

## 📝 Documentación Actualizada

- `docs/ROADMAP_NODE24_ACTIONS.md`
- `docs/WORKFLOW_RELEVAMIENTO_NODE24.md`
- `NEXT_SESSION.md`
- `docs/NEXT_SESSION.MD`
- `README.md` (prerrequisito Node actualizado a 24+)

---

## 🔖 Versionado y Release

Se prepara bump de versión para siguiente release:

- `frontend/package.json`: `1.0.0` -> `1.1.0`
- `package.json` (root): `0.0.0` -> `1.1.0`

Además, se define requisito mínimo de runtime local:

- Node.js `>=24` en manifests de frontend y root.

Recomendación de release post-merge:
- Crear release/tag `v1.1.0` en GitHub con notas basadas en este changelog.

---

## ⚠️ Ajustes Operativos Recomendados (Post-merge)

Para cerrar certificación operativa completa de Node24 en workflows no frecuentes:

1. Ejecutar manualmente `update-tunnel.yml`.
2. Ejecutar manualmente `frontend-backend-link-check.yml` (con variable habilitante).
3. Ejecutar manualmente `brou-health-monitor.yml`.

---

Fecha: 2026-04-18
Rama: `chore/node24-actions-migration-plan`
