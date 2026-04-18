# Relevamiento Arquitectonico de Workflows (Salto Node 20 -> 24)

Fecha: 2026-04-18
Rama: chore/node24-actions-migration-plan

## Objetivo

Revisar cada workflow con criterio de arquitectura de infraestructura y confiabilidad operativa:

- Si aporta valor real al sistema.
- Si se superpone con otros workflows.
- Si conviene refactorizar, consolidar o deprecar.
- Como aprovechar el salto a Node 24 para mejorar mantenibilidad y resiliencia.

## Inventario Actual

1. `.github/workflows/ci-cd.yml`
2. `.github/workflows/security-audit.yml`
3. `.github/workflows/update-tunnel.yml`
4. `.github/workflows/frontend-backend-link-check.yml`
5. `.github/workflows/brou-health-monitor.yml`

### Inventario de Actions JavaScript detectadas (estado actual)

- `actions/checkout@v4`
- `actions/upload-artifact@v4`
- `actions/deploy-pages@v4`
- `actions/github-script@v7`

Observacion:
- El warning de Node 20 impacta principalmente a acciones JavaScript cuya version interna aun no este migrada por sus maintainers.
- El salto a Node 24 debe incluir validacion de compatibilidad de estas majors y actualizacion controlada donde haya nuevas majors estables.

## Diagnostico Ejecutivo

### 1) CI/CD

Valor: alto. Es el pipeline principal de calidad y despliegue.

Fortalezas:
- Estructura por jobs clara (security, tests, build, deploy, summary).
- Guard de tunel para evitar deploy frontend con URL rota.
- Separacion backend/frontend razonable.

Problemas detectados:
- Duplica controles de seguridad con `security-audit.yml`.
- Build frontend elimina `package-lock.json` e instala con `npm install` (no deterministico).
- Acoplamiento fuerte al entorno self-hosted para tareas que podrian ejecutarse en hosted.

Decision recomendada: mantener y refactorizar.

### 2) Security Audit

Valor: medio-alto. Aporta vigilancia independiente (scheduled + manual).

Fortalezas:
- Corre en `windows-latest`, desacoplando parte de la salud del runner local.
- Tiene umbral configurable en backend.
- Publica artefactos utiles para trazabilidad.

Problemas detectados:
- Solapa parcialmente con security jobs de `ci-cd.yml`.
- Misma logica en dos workflows eleva costo de mantenimiento.

Decision recomendada: mantener, pero simplificar alcance.

### 3) Update Cloudflare Tunnel

Valor: alto en escenario de quick tunnel dinamico.

Fortalezas:
- Encapsula recuperacion automatica del tunel y update de secret.
- Reusa script con retries y fallback.

Problemas detectados:
- Dependencia de `GH_PAT` para operaciones sensibles.
- Riesgo de cascada de ejecuciones al disparar deploy luego de recuperar tunel.

Decision recomendada: mantener y endurecer con guardas anti-loop.

### 4) Frontend-Backend Link Check

Valor: medio. Buen objetivo operacional, pero implementacion muy monolitica.

Fortalezas:
- Detecta degradaciones reales de integracion.
- Tiene auto-recovery del tunel y gestion de issues.

Problemas detectados:
- Mezcla demasiadas responsabilidades (sintetico, recovery, governance de issues, CORS, endpoints).
- Usa `Start-Sleep` largos y retries extensos dentro de un mismo job.
- Genera complejidad operativa y ruido de mantenimiento.

Decision recomendada: refactor fuerte en 2 workflows separados.

### 5) BROU Health Monitor

Valor: medio. Monitorea una capacidad de negocio especifica.

Fortalezas:
- Verifica frescura de datos y no solo disponibilidad HTTP.
- Mecanismo de apertura/cierre de issue con threshold de fallos.

Problemas detectados:
- Duplica patron de issue lifecycle con `frontend-backend-link-check.yml`.
- Parte de esta validacion podria migrar a metricas internas del backend.

Decision recomendada: mantener, pero con estandarizacion del patron de observabilidad.

## Respuesta a la pregunta clave: "estos workflows tienen sentido real?"

Si, pero no todos con el nivel actual de separacion de responsabilidades.

Clasificacion propuesta:

- Mantener: `ci-cd.yml`, `update-tunnel.yml`
- Mantener con simplificacion: `security-audit.yml`, `brou-health-monitor.yml`
- Rework profundo: `frontend-backend-link-check.yml`

No recomiendo deprecar completamente ninguno en esta etapa porque cada uno cubre un riesgo real. Si recomiendo consolidar y redefinir fronteras de responsabilidad para bajar complejidad.

## Oportunidad del salto a Node 24

Node 24 no mejora por si solo la arquitectura, pero si habilita limpiar deuda tecnica en Actions JavaScript:

- Eliminar warnings de deprecacion Node 20.
- Adoptar majors recientes de actions oficiales cuando correspondan.
- Unificar baseline de runtime para acciones JS y reducir variabilidad.

Mejora real esperada: menos riesgo operativo futuro y mejor soporte/seguridad, mas que ganancia de performance perceptible en tiempos de pipeline.

### Politica recomendada para Actions en Node 24

1. Priorizar acciones oficiales y majors soportadas.
2. Donde aplique, fijar commit SHA ademas del tag para reducir riesgo de supply chain.
3. Incorporar un control recurrente (Dependabot o revision mensual) sobre nuevas majors de actions.
4. Evitar acciones de terceros sin mantenimiento activo para pasos criticos.

## Arquitectura Objetivo Recomendada (v2)

### A. Pipeline de calidad (CI) separado de pipeline de release/deploy

Objetivo:
- PR y push validan calidad (lint, test, seguridad) de forma deterministica.
- Deploy solo cuando calidad ya paso.

Propuesta:
1. `ci.yml` (PR + push): lint/test/audits, sin despliegues.
2. `release.yml` (push a master o dispatch): build/publish/deploy con gates claros.

Beneficio:
- Menos acoplamiento entre validaciones y operaciones de recuperacion.

### B. Operacion de tunel como reconciliador, no como side effect difuso

Objetivo:
- Un solo workflow responsable de converger estado del tunel y secret.

Propuesta:
- Mantener `update-tunnel.yml` como "source of truth" para reconciliacion.
- Cualquier otro workflow solo solicita reconciliacion via `workflow_call` o `repository_dispatch`, sin logica duplicada.

Beneficio:
- Menos loops, menos ramificaciones y menor MTTR.

### C. Monitoreo sintetico y auto-healing desacoplados

Objetivo:
- Separar deteccion de incidente de accion correctiva.

Propuesta:
1. `synthetic-check.yml`: solo verifica disponibilidad e integra evidencias.
2. `auto-heal.yml`: decide si ejecuta recovery segun umbrales, cooldown y politicas.

Beneficio:
- Simplifica debugging y evita workflows gigantes.

### D. Patron comun para "issue lifecycle"

Objetivo:
- Evitar logica duplicada para abrir/cerrar issues en monitores.

Propuesta:
- Extraer logica a accion compuesta local en `.github/actions/issue-lifecycle`.

Beneficio:
- Menor duplicacion, menos bugs por divergencia.

## Riesgos y Mitigaciones

1. Riesgo: loops de ejecucion entre recovery y deploy.
Mitigacion: bandera de cooldown + deduplicacion por huella de evento + no auto-disparar deploy en cada recuperacion.

2. Riesgo: dependencia excesiva de quick tunnel dinamico.
Mitigacion: evaluar tunel nombrado estable (Cloudflare Tunnel gestionado) como estrategia objetivo.

3. Riesgo: drift entre runner self-hosted y hosted.
Mitigacion: definir matriz explicita de que corre en hosted vs self-hosted y por que.

4. Riesgo: falsos positivos de seguridad por parsing/schemas variables.
Mitigacion: mantener parser robusto y contrato de salida testeado con fixtures.

## Plan de Ejecucion Propuesto (inmediato)

Fase 1 (corta, baja friccion)
1. Completar migracion de actions a versiones compatibles con Node 24.
2. Eliminar `npm install` no deterministico en build frontend y volver a lockfile reproducible.
3. Definir politica de triggers para evitar ejecuciones redundantes.

Fase 2 (rework estructural)
1. Particionar `frontend-backend-link-check.yml` en deteccion y healing.
2. Estandarizar issue lifecycle en accion compuesta.
3. Reducir duplicacion entre `ci-cd.yml` y `security-audit.yml`.

Fase 3 (evolucion de plataforma)
1. Evaluar migracion de quick tunnel a tunel nombrado estable.
2. Introducir metricas de SLO simples (disponibilidad endpoint y frescura BROU).

## Criterios de Exito

- Cero warnings de deprecacion Node 20 en Actions.
- Menos workflows con responsabilidad mezclada.
- Menos re-ejecuciones innecesarias por push.
- Reduccion de tiempo medio de diagnostico de fallos.
- Menor duplicacion de logica entre workflows.

## Conclusiones

El analisis confirma que la base actual es util, pero esta entrando en una zona de complejidad accidental. El salto a Node 24 es una oportunidad ideal para hacer hardening y simplificacion estructural, no solo upgrade de versiones.

Recomendacion final: avanzar con Node 24 + rework incremental de arquitectura de workflows en esta misma rama, cerrando primero reproducibilidad y anti-loop, y luego particionando monolitos operativos.