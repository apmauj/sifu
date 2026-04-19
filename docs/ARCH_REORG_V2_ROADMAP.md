# SIFU - Roadmap de Re-Arquitectura V2

Fecha: 2026-04-19
Rama base: develop
Rama programa: chore/arch-reorg-v2
Estado: Completado (Fase 4 cerrada)

## 1. Contexto y decision

La rama historica `chore/arch-reorg-plan` contenia una buena intencion tecnica, pero quedo obsoleta por:

- Desfase alto contra la linea principal.
- Arquitectura actual consolidada en `src/` (hexagonal), no en la antigua carpeta `backend/`.
- Alto costo de merge directo y riesgo de regresion.

Decision:

- No revivir ni mergear la rama historica.
- Ejecutar una re-arquitectura incremental sobre el estado actual de `develop`.
- Mantener compatibilidad de API y despliegue durante todo el programa.

## 2. Objetivos del programa

1. Consolidar limites entre capas (`api`, `application`, `domain`, `infrastructure`, `utils`).
2. Reducir acoplamiento y deuda de importaciones cruzadas.
3. Unificar patrones de validacion, seguridad y observabilidad.
4. Mejorar mantenibilidad sin romper endpoints ni CI/CD.
5. Completar la limpieza de artefactos transicionales en forma segura.

## 3. No objetivos

1. No se cambiara el contrato publico de endpoints salvo necesidad justificada.
2. No se realizara una migracion masiva de carpetas tipo "big-bang".
3. No se reemplazaran librerias principales sin RFC tecnica previa.

## 4. Estrategia de ramas y PRs

Modelo recomendado:

1. Rama programa: `chore/arch-reorg-v2`.
2. Subramas por fase:
- `feat/arch-v2-phase0-guardrails`
- `feat/arch-v2-phase1-boundaries`
- `feat/arch-v2-phase2-module-split`
- `feat/arch-v2-phase3-observability-data`
- `feat/arch-v2-phase4-cleanup`
3. Cada subrama abre PR contra `chore/arch-reorg-v2`.
4. `chore/arch-reorg-v2` se mergea a `develop` al cerrar hitos estables.
5. Evitar PRs gigantes: tamano objetivo <= 500 lineas netas por PR (cuando sea posible).

## 5. Fases

## Fase 0 - Guardrails y baseline (1-2 dias)

Objetivo:
- Definir reglas para que la arquitectura no vuelva a degradarse.

Entregables:
1. ADR breve de limites entre capas (dependencias permitidas/prohibidas).
2. Inventario de modulos criticos y puntos de alto acoplamiento.
3. Check automatizado simple en CI (por ejemplo, validar imports prohibidos entre capas).
4. Baseline de metricas iniciales (tiempo tests backend/frontend, cantidad de violaciones de capas, modulos mas largos).

Criterio de salida:
- Reglas visibles + check ejecutable en CI + baseline versionado.

## Fase 1 - Fronteras de capas (2-4 dias)

Objetivo:
- Corregir acoplamientos de alto impacto entre capas.

Entregables:
1. Normalizar imports en routers y servicios hacia capas correctas.
2. Eliminar atajos de acceso a infraestructura desde capa inadecuada.
3. Mantener shims necesarios de compatibilidad, pero registrar deuda restante.

Criterio de salida:
- Violaciones de capas prioritarias resueltas sin romper tests.

## Fase 2 - Modularizacion dirigida por dominio (3-6 dias)

Objetivo:
- Reducir archivos monoliticos y clarificar ownership por feature.

Entregables:
1. Separacion de servicios grandes por feature (UI/UR/Exchange/BROU) donde aplique.
2. Extraccion de utilidades compartidas de validacion/transformacion.
3. Tests focalizados actualizados por modulo.

Criterio de salida:
- Menor complejidad ciclomatica y mejor navegabilidad por dominio.

## Fase 3 - Datos, seguridad y observabilidad (2-4 dias)

Objetivo:
- Unificar comportamiento transversal y reducir duplicacion.

Entregables:
1. Convenciones de logging y eventos de seguridad consolidadas.
2. Homogeneizacion de validadores y manejo de errores reutilizable.
3. Reglas claras para acceso a datos y puntos de cache.

Criterio de salida:
- Menos duplicacion y trazabilidad operacional mejorada.

## Fase 4 - Cleanup y cierre (1-3 dias)

Objetivo:
- Cerrar deuda transicional de forma segura.

Entregables:
1. Eliminar shims o compatibilidad residual no usada.
2. Actualizar documentacion principal de arquitectura.
3. Checklist final de compatibilidad y operacion.

Criterio de salida:
- Arquitectura consistente, documentada y validada en CI.

## 6. Criterios de exito global

1. Cero regresiones funcionales en endpoints criticos.
2. CI/CD estable durante toda la ejecucion.
3. Reduccion medible de acoplamiento y complejidad en modulos objetivo.
4. Menor costo de onboard y mantenimiento (documentado).

## 7. Riesgos y mitigaciones

Riesgo 1: Refactor sin valor real.
- Mitigacion: cada fase debe mostrar metrica antes/despues.

Riesgo 2: PRs demasiado grandes.
- Mitigacion: subramas por fase y PRs pequenos.

Riesgo 3: Regresion de compatibilidad.
- Mitigacion: mantener tests, smoke de endpoints y estrategia de rollback por fase.

Riesgo 4: Deriva de arquitectura futura.
- Mitigacion: guardrails automatizados y reglas explicitas de dependencias.

## 8. Plan de ejecucion inmediato (kickoff)

Semana 1:

1. Ejecutar Fase 0 completa.
2. Abrir PR de Fase 0 hacia `chore/arch-reorg-v2`.
3. Iniciar Fase 1 con primer lote de imports criticos.

Backlog inicial sugerido:

1. Crear ADR de fronteras de capas.
2. Crear script de chequeo de imports prohibidos.
3. Integrar script en workflow de CI (modo warning al inicio, luego blocking).
4. Generar reporte baseline de acoplamiento y archivos objetivo.

## 9. Gobierno del programa

Cadencia:
- Revision tecnica corta por fase (15-30 min).

Definition of Done por PR:
1. Tests relevantes en verde.
2. Sin cambios de contrato API no documentados.
3. Documentacion actualizada si cambia una decision de arquitectura.
4. Diff legible y acotado.

Responsables:
- Owner tecnico: equipo backend.
- Revision cruzada: al menos 1 reviewer con foco en arquitectura.

## 10. Estado actual

- Fase 0 completada (ADR, guardrails y baseline integrados en CI).
- Fase 1 completada (fronteras principales corregidas por PRs pequenos).
- Fase 2 completada e integrada en `develop` y `master`.
- Fase 3 completada e integrada en `develop` y `master`.
- Fase 4 completada en `feat/arch-v2-phase4-cleanup`.
- Primer corte Fase 4 aplicado: migracion de imports internos para usar servicios directos (`ui_service`, `ur_service`, `exchange_rate_service`) en lugar del modulo de compatibilidad `src/domain/services.py`.
- Segundo corte Fase 4 aplicado: `src/application/bootstrap.py` deja de depender de helpers de conteo en `src/domain/services.py`.
- Tercer corte Fase 4 aplicado: `src/domain/services.py` elimina duplicacion de helpers de conteo y mantiene compatibilidad via re-export desde `src/application/bootstrap.py`.
- Cuarto corte Fase 4 aplicado: ruta de deprecacion para aliases legacy de UR (`año/mes/valor`) con warnings opt-in via variable de entorno `SIFU_LEGACY_ALIAS_WARNINGS=1`, sin romper compatibilidad por defecto.
- Quinto corte Fase 4 aplicado: inicio de migracion de tests de integracion UR a claves canonicas (`year/month/value`) en secciones de modelos/workflow, manteniendo una verificacion de compatibilidad legacy.
- Sexto corte Fase 4 aplicado: migracion completa de `tests/integration/test_ur.py` a claves canonicas (`year/month/value`) en fixtures, tests de servicio y assertions de API, manteniendo una verificacion legacy puntual.
- Septimo corte Fase 4 aplicado (`v1.4.0` hardening): workflow `backend-tests` ejecuta con `SIFU_LEGACY_ALIAS_WARNINGS=1` y agrega guardia anti-regresion para bloquear nuevas referencias legacy fuera de allowlist.
- Octavo corte Fase 4 aplicado (`v1.5.0`): aliases legacy `año/mes/valor` removidos de `URValue` y `URRecord`; tests legacy retirados; guardia CI endurecida para no permitir referencias legacy.
- Cierre formal completado: PR #24 con CI/CD y Security Audit en verde.

## 11. Plan de retiro de aliases UR (versionado)

Objetivo:
- Retirar aliases legacy `año/mes/valor` sin ruptura abrupta para consumidores.

Versionado propuesto:
1. `v1.3.x` (actual): compatibilidad completa + warnings opt-in con `SIFU_LEGACY_ALIAS_WARNINGS=1`.
2. `v1.4.0`: mantener compatibilidad, pero habilitar warnings en CI de backend para evitar nuevas regresiones hacia aliases legacy.
3. `v1.5.0`: remover aliases legacy en modelos/record y actualizar tests restantes a canónico.

Checklist ejecutable:
1. Ver `docs/UR_ALIAS_RETIREMENT_CHECKLIST.md` y completar fase `v1.4.0`.
2. Ejecutar suite focalizada UR + suite backend principal con warnings deprecados activos.
3. Confirmar que no quedan referencias legacy en tests de integración y docs API.
4. Ejecutar corte final `v1.5.0` eliminando aliases y tests de compatibilidad.
