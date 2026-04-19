# Arch Reorg V2 - Baseline Tecnico (Fase 0)

Fecha: 2026-04-19
Rama: feat/arch-v2-phase0-guardrails

## 1. Alcance del baseline

Este baseline captura el estado inicial de arquitectura para medir mejoras de re-arquitectura incremental V2.

Mediciones incluidas:

1. Tamano actual del backend en src/.
2. Top modulos por lineas.
3. Violaciones de dependencias entre capas segun ADR-0001.
4. Tiempos de referencia de tests backend/frontend.

## 2. Tamano actual en src/

- Archivos Python en src/: 46
- Lineas totales en src/: 9247

## 3. Top modulos por tamano (lineas)

1. src/domain/excel_processor.py: 1117
2. src/infrastructure/health_checks.py: 570
3. src/domain/services.py: 494
4. src/utils/constants.py: 393
5. src/infrastructure/database_optimizer.py: 382
6. src/domain/brou_processor.py: 377
7. src/api/routers/exchange.py: 322
8. src/application/alerts.py: 321
9. src/application/secure_logging.py: 317
10. src/application/simple_totp.py: 283
11. src/infrastructure/circuit_breaker.py: 282
12. src/application/config_validator.py: 277

## 4. Baseline de guardrail de capas

Script:
- scripts/architecture/check_layer_imports.ps1

Modo de ejecucion en Fase 0:
- warn (no bloqueante)

Resultado baseline:
- Violaciones detectadas: 0
- Archivos escaneados: 46

Reporte JSON (CI/local):
- logs/architecture/layer_violations.json

## 5. Baseline de tiempos de tests (referencia inicial)

Fecha de medicion: 2026-04-19

Comandos medidos:

1. Backend
- `C:/Users/apmauj/repos/sifu/.venv/Scripts/python.exe -m pytest tests -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto`
- Tiempo observado: 26.77 s

2. Frontend
- `cd frontend && npm test -- --run --reporter=verbose`
- Tiempo observado: 28.04 s

Nota:
- Son tiempos de referencia inicial para comparar mejoras/regresiones por fase.

## 6. Implicancias para Fase 1

1. El layout de capas actual esta sano respecto a imports directos por capa.
2. Fase 1 puede enfocarse en consolidacion de limites funcionales y modularizacion (no en corregir violaciones masivas de imports).
3. El guardrail queda activo para prevenir regresiones futuras.

## 7. Referencias

- ADR: docs/adr/ADR-0001-layer-boundaries.md
- Checklist Fase 0: docs/ARCH_REORG_V2_PHASE0_CHECKLIST.md
- Backlog Fase 1: docs/ARCH_REORG_V2_PHASE1_BACKLOG.md
- Roadmap V2: docs/ARCH_REORG_V2_ROADMAP.md
