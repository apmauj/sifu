# Roadmap - Node 24 Migration for GitHub Actions

Fecha: 2026-04-18
Rama de trabajo: chore/node24-actions-migration-plan
Prioridad: P0

## 1. Objetivo
Eliminar dependencia operativa de Node 20 en workflows de GitHub Actions y validar ejecucion estable con Node 24 antes de los cambios forzados del runner.

Objetivo complementario de arquitectura:
- Aprovechar la migracion para reducir complejidad, duplicaciones y riesgos operativos en workflows.

Referencia de relevamiento:
- `docs/WORKFLOW_RELEVAMIENTO_NODE24.md`

## 2. Alcance
Workflows objetivo:
- CI/CD
- Security Audit
- Update Cloudflare Tunnel
- Frontend-Backend Link Check
- BROU Health Monitor

## 3. Plan por fases

### Fase A - Inventario y baseline
1. Listar todas las acciones JavaScript usadas por workflow. ✅
2. Identificar versiones actuales y compatibilidad con Node 24. ✅
3. Guardar baseline de estado actual (warning/fallos). ✅

### Fase B - Actualizacion de acciones
1. Actualizar `actions/checkout` y `actions/upload-artifact` a versiones recomendadas. ✅
2. Revisar otras acciones de terceros y fijar tags/SHAs estables. ✅ (actions oficiales actualizadas a majors vigentes)
3. Mantener cambios atomicos por workflow para trazabilidad. ✅

### Avance Fase 1 (implementado en esta rama)
1. CI/CD frontend build ahora usa instalacion deterministica con lockfile (`npm ci`) en lugar de `npm install`.
2. Recovery de tunel en monitor de enlace ya no dispara deploy automaticamente por defecto.
3. `update-tunnel.yml` ahora parte con defaults conservadores (`trigger_deploy=false`, `skip_if_unchanged=true`).
4. Script de update de tunel evita redeploy cuando la URL no cambio, salvo override explicito (`-ForceDeployOnUnchanged`).
5. Actions oficiales actualizadas a majors vigentes (checkout v6, upload-artifact v7, deploy-pages v5, github-script v9).
6. Workflows principales y monitores configurados con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` para validacion anticipada.

Estado: completado para CI/CD y Security Audit, con validacion remota en verde.

### Fase C - Validacion forzada Node 24
1. Ejecutar pruebas con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`. ✅
2. Validar jobs de seguridad, tests y despliegue. ✅ (Security Audit y CI/CD en verde)
3. Corregir incompatibilidades detectadas. ✅ (fix backend async tests en CI)

### Fase D - Cierre y merge
1. Confirmar cero warnings de Node 20 en workflows criticos. ✅
2. Confirmar pipelines en verde con SHA de rama. ✅
3. Documentar cambios y decisiones. ✅
4. Merge a `master`. ⏳ Pendiente (abrir PR y aprobar)

## 4. Criterios de aceptacion
- 0 warnings de deprecacion Node 20 en jobs criticos.
- CI/CD en verde sin regressions funcionales.
- Security Audit en verde con politicas actuales.
- Update Tunnel y Link Check ejecutan sin errores de runtime por acciones.

## 5. Riesgos y mitigaciones
- Riesgo: cambio de version rompe comportamiento de action.
  Mitigacion: actualizar por etapas y validar cada workflow.
- Riesgo: runner self-hosted desactualizado.
  Mitigacion: verificar version del runner antes de fase C.
- Riesgo: flakiness por red/tunnel oculta resultado.
  Mitigacion: reintentos controlados y validaciones separadas por dominio.

## 6. Entregables
- PR de migracion Node 24 en Actions. ⏳ En preparacion
- Evidencia de runs exitosos.
- Actualizacion de `NEXT_SESSION.md`, `docs/NEXT_SESSION.MD` y consolidacion del historial en `../CHANGELOG.md`.

## 7. Ajustes Extra Detectados y Resueltos
- Falla en backend tests por `async def` sin plugin activo en CI: se removio `PYTEST_DISABLE_PLUGIN_AUTOLOAD` y se fijo `--asyncio-mode=auto`.
- Falsos fallos por tests de demostracion: backend CI ignora `tests/demo` para no contaminar regresion real.
- Warnings de scripts PowerShell en Problems: renombrado de simbolos y limpieza de variables no usadas para reducir ruido operativo.

## 8. Ajustes Extra Recomendados (Post-merge)
- Correr validacion manual de `update-tunnel.yml`, `frontend-backend-link-check.yml` y `brou-health-monitor.yml` en un entorno controlado para certificar runtime Node 24 en workflows no frecuentes.
- Evaluar pinning por SHA en acciones criticas (supply chain hardening) en una iteracion dedicada.
