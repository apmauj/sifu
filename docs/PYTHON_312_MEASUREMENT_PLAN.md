# Python 3.12 Impact Measurement Plan

## Objetivo
Medir de forma objetiva el impacto del salto de baseline Python 3.11 -> 3.12.

## Métricas recomendadas

### 1) CI throughput
- Duración total de run `CI/CD`.
- Duración de jobs backend:
  - `Security Audit Backend`
  - `Backend Tests`

Fuente:
- GitHub Actions (`createdAt`, `startedAt`, `completedAt`).

Comparación mínima sugerida:
- Últimos 5 runs en baseline previo vs primeros 5 runs en baseline 3.12.

### 2) Estabilidad
- Pass rate backend en CI.
- Cantidad de retries/reruns.
- Fallos intermitentes (flakes) observados en tests backend.

### 3) Seguridad
- Conteo de vulnerabilidades por severidad en `pip-audit`.
- Cambios en paquetes bloqueados o con wheels nativos.

### 4) Performance local (smoke)
- Tiempo de ejecución de suite backend rápida:
  - `pytest -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto`
- Tiempo de build frontend:
  - `npm --prefix frontend run -s build`

## Protocolo de medición (simple)

1. Fijar entorno:
- Misma máquina/runner.
- Sin otras cargas pesadas.

2. Ejecutar 3 repeticiones por escenario.

3. Usar mediana (no promedio) para reducir ruido.

4. Registrar resultados en tabla comparativa.

## Plantilla de reporte

| Métrica | Baseline previo | Python 3.12 | Delta |
|---|---:|---:|---:|
| CI/CD total (mediana) |  |  |  |
| Backend Tests (mediana) |  |  |  |
| Security Audit Backend (mediana) |  |  |  |
| Pass rate backend |  |  |  |
| High/Critical en pip-audit |  |  |  |

## Criterio de éxito sugerido

- Sin regresión de estabilidad (pass rate >= baseline previo).
- Sin aumento de vulnerabilidades High/Critical.
- Sin degradación significativa de tiempos CI (>10%) en jobs backend.

## Nota

El objetivo principal del bump es seguridad de soporte y reproducibilidad de runtime.
Las mejoras de performance pueden existir, pero deben considerarse beneficio secundario y medirse con datos.
