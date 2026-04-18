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
2. Identificar versiones actuales y compatibilidad con Node 24.
3. Guardar baseline de estado actual (warning/fallos).

### Fase B - Actualizacion de acciones
1. Actualizar `actions/checkout` y `actions/upload-artifact` a versiones recomendadas.
2. Revisar otras acciones de terceros y fijar tags/SHAs estables.
3. Mantener cambios atomicos por workflow para trazabilidad.

### Avance Fase 1 (implementado en esta rama)
1. CI/CD frontend build ahora usa instalacion deterministica con lockfile (`npm ci`) en lugar de `npm install`.
2. Recovery de tunel en monitor de enlace ya no dispara deploy automaticamente por defecto.
3. `update-tunnel.yml` ahora parte con defaults conservadores (`trigger_deploy=false`, `skip_if_unchanged=true`).
4. Script de update de tunel evita redeploy cuando la URL no cambio, salvo override explicito (`-ForceDeployOnUnchanged`).

Estado: en curso (Fase 1 tecnica iniciada y aplicada parcialmente).

### Fase C - Validacion forzada Node 24
1. Ejecutar pruebas con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`.
2. Validar jobs de seguridad, tests y despliegue.
3. Corregir incompatibilidades detectadas.

### Fase D - Cierre y merge
1. Confirmar cero warnings de Node 20 en workflows criticos.
2. Confirmar pipelines en verde con SHA de rama.
3. Documentar cambios y decisiones.
4. Merge a `master`.

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
- PR de migracion Node 24 en Actions.
- Evidencia de runs exitosos.
- Actualizacion de `NEXT_SESSION.md` y `docs/NEXT_SESSION.MD`.
