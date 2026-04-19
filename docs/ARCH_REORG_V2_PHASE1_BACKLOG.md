# Arch Reorg V2 - Backlog Priorizado Fase 1

Fecha: 2026-04-19
Rama: feat/arch-v2-phase0-guardrails
Objetivo: consolidar fronteras funcionales y modularizacion incremental sin romper compatibilidad

## Regla de tamano de PR

- Objetivo: <= 500 lineas netas por PR cuando sea posible.
- Si una tarea supera ese umbral, dividir en 2 o mas PRs secuenciales.

## Prioridades (P1-P10)

1. P1 - Modularizar `src/domain/services.py` por dominio
- Extraer servicios UI/UR/Exchange/BROU en modulos dedicados.
- Mantener un punto de import compatible durante transicion.

2. P2 - Reducir peso de `src/domain/excel_processor.py`
- Separar parsing comun y transformaciones por tipo de dataset.
- Preservar contratos usados por endpoints actuales.

3. P3 - Delimitar responsabilidades en `src/infrastructure/health_checks.py`
- Separar checks de infraestructura, datos externos y cache.
- Mantener registro con `HealthChecker.add_check` y cache 30s.

4. P4 - Consolidar validaciones de entrada
- Reforzar uso central de `InputValidator` y `SecurityValidator`.
- Eliminar validaciones duplicadas en rutas/servicios.

5. P5 - Endurecer convenciones de mensajes
- Verificar uso de constantes `MSG_*` de `constants.py`.
- Detectar y eliminar hardcodes de errores repetidos.

6. P6 - Normalizar rutas de import legacy
- Reducir imports legacy en favor de `src/...` en codigo interno.
- Mantener compatibilidad externa donde sea necesario.

7. P7 - Estandarizar logging operacional
- Revisar escritura de `.log/.txt` bajo `logs/`.
- Documentar excepciones justificadas si aparecen.

8. P8 - Validacion de limites de capa en CI (progresivo)
- Mantener guardrail en modo `warn` durante primeras correcciones.
- Preparar criterio para pasar a modo `fail`.

9. P9 - Cobertura de tests en modulos extraidos
- Agregar/ajustar tests unitarios en cada extraction PR.
- Evitar caida de cobertura efectiva en areas criticas.

10. P10 - Documentacion de arquitectura actualizada por lote
- Actualizar docs relevantes al cerrar cada lote significativo.
- Mantener trazabilidad de decisiones en ADRs.

## Plan de PRs pequenos sugerido

1. PR A: split inicial de `services.py` (UI/UR).
2. PR B: split de `services.py` (Exchange/BROU) + compat shim interno.
3. PR C: primer corte de `excel_processor.py`.
4. PR D: primer corte de `health_checks.py`.
5. PR E: consolidacion de validaciones + limpieza de hardcodes.
