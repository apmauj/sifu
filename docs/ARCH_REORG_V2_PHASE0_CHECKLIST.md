# Arch Reorg V2 - Fase 0 Checklist

Fecha inicio: 2026-04-19
Rama programa: chore/arch-reorg-v2
Objetivo fase: guardrails y baseline

## Checklist

1. ADR de fronteras entre capas
- [x] Definir dependencias permitidas entre `src/api`, `src/application`, `src/domain`, `src/infrastructure`, `src/utils`.
- [x] Definir dependencias prohibidas y excepciones temporales.
- [x] Aprobar ADR en PR.

2. Baseline tecnico
- [x] Medir tiempos de test backend/frontend (referencia inicial).
- [x] Identificar top 10 modulos por tamano/complejidad percibida.
- [x] Inventariar imports cruzados que violen limites de capas.

3. Guardrails automatizados
- [x] Crear script de chequeo de imports por capas (modo reporte).
- [x] Integrar script a CI como warning (sin bloquear).
- [x] Generar reporte en artefacto de CI.

4. Plan de ejecucion fase 1
- [x] Priorizar 5-10 violaciones de capas de mayor impacto.
- [x] Definir PRs chicos para correccion incremental.
- [x] Acordar regla de tamano maximo de PR.

## Definition of Done - Fase 0

- ADR aprobado y versionado.
- Baseline medible publicado en el repo.
- Chequeo automatico corriendo en CI.
- Backlog de Fase 1 priorizado y listo para ejecutar.
