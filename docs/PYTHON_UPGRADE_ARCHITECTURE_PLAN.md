# Plan de Arquitectura - Upgrade de Python

Fecha: 2026-04-18
Rama: chore/python-upgrade-architecture-plan

## 1. Estado Actual (evidencia)

### Local (developer machine)
- Entorno virtual local: Python 3.11.0b4 (beta)
- Ruta: .venv/Scripts/python.exe
- pip local: 22.0.4

Implicancia:
- El entorno local no es una release final de Python 3.11.
- Hay riesgo de diferencias respecto a producción y CI por usar beta + pip antiguo.

### CI/CD remoto (self-hosted)
- Los workflows no fijan python-version con actions/setup-python.
- Se activa un .venv preexistente del runner (estado mutable).
- Evidencia en logs y workflows: instalación sobre .venv/Scripts/Activate.ps1.

Implicancia:
- El runtime Python en CI no está pinneado por workflow.
- Hay riesgo de drift (cambios silenciosos por estado del runner).

### Producción / imagen backend
- Base image actual: python:3.11-slim
- Archivo: config/docker/Dockerfile

Implicancia:
- El baseline real de ejecución en backend está en Python 3.11.

### Código y compatibilidad mínima efectiva
- El código usa type hints con operador | (PEP 604), por ejemplo dict | None.
- Esa sintaxis requiere Python >= 3.10.

Conclusión de estado:
- README previo (3.9+) estaba desalineado.
- El baseline efectivo real hoy es Python 3.11.

## 2. Recomendación de Target

Recomendación principal:
- Baseline operativo inmediato: Python 3.11.x estable y pinneado.
- Target de evolución: Python 3.12.x como versión principal del repo.

Razonamiento:
- 3.12 ofrece mejoras de performance y typing con bajo riesgo relativo.
- 3.13 puede tener mayor riesgo de compatibilidad de ecosistema en algunas dependencias.
- 3.12 permite modernizar sin asumir riesgo de frontera.

## 3. Riesgos Arquitectónicos a Resolver

1. Drift de runtime en CI
- Sin setup-python, el pipeline depende del estado del host.

2. Inconsistencia local vs CI vs contenedor
- Local (beta), CI (implícito), Docker (3.11) no están formalmente unificados.

3. Falta de contrato de versión en el repo
- No existe requires-python central ni archivo de versión estándar (.python-version o equivalente).

4. Dependencias nativas / wheels
- Upgrade a 3.12 requiere validar wheels para pandas, cryptography, lxml, grpcio, etc.

## 4. Plan Propuesto por Fases

### Fase 0 - Normalización (rápida, bajo riesgo)
Objetivo: alinear documentación y declarar baseline actual.

Tareas:
- README con Python 3.11+ (aplicado en esta rama).
- Documentar estado y decisión en este plan.

Criterio de salida:
- Mensaje único de baseline: 3.11 en docs y runtime actual.

### Fase 1 - Reproducibilidad de CI y dev (recomendada inmediata)
Objetivo: eliminar drift de versión.

Tareas:
- Introducir setup explícito de Python en workflows (3.11.x estable).
- Crear archivo de versión para desarrollo (ejemplo: .python-version con 3.11.x estable).
- Actualizar bootstrap local para detectar/advertir versiones beta o menores al baseline.
- Subir pip a versión reciente en flujo local/CI.

Criterio de salida:
- CI y dev usan Python pinneado y reproducible.

### Fase 2 - Validación cruzada 3.11 + 3.12
Objetivo: probar compatibilidad antes del corte.

Tareas:
- Agregar job/matriz opcional en CI para 3.12 (no bloqueante al inicio).
- Ejecutar tests backend completos + smoke de bootstrap excel.
- Ejecutar pip-audit y validación de importaciones clave en 3.12.

Criterio de salida:
- Suite verde en 3.11 y 3.12 con issues conocidos acotados.

### Fase 3 - Promoción a 3.12
Objetivo: mover baseline oficial.

Tareas:
- Cambiar Dockerfile backend a python:3.12-slim.
- Cambiar baseline docs y scripts a 3.12+.
- Hacer obligatorio el job 3.12 en CI.
- Mantener 3.11 temporalmente como compatibilidad de transición (si aplica).

Criterio de salida:
- Producción + CI + desarrollo alineados en 3.12.

### Fase 4 - Limpieza y optimización
Objetivo: consolidar el upgrade.

Tareas:
- Retirar compatibilidad transicional 3.11 cuando sea seguro.
- Evaluar mejoras de código aprovechando 3.12 (sin romper APIs públicas).
- Actualizar guía de contribución y troubleshooting.

Criterio de salida:
- Un único baseline sin deuda de transición.

## 5. Validaciones Técnicas Recomendadas

Checklist mínimo previo a promover 3.12:
- Backend tests: pytest completo (incluyendo async y endpoints críticos).
- Seguridad: pip-audit sin nuevas vulnerabilidades críticas.
- Build imagen Docker y arranque de app en contenedor.
- Smoke APIs: /api/health, /api/ui/latest, /api/ur/latest, /api/exchange-rate/current, /api/brou/current.
- Frontend smoke: carga de paneles y llamadas API principales.

## 6. Entregables sugeridos para siguientes PRs

PR A (hardening runtime):
- Pin de Python en workflows + archivo de versión local + mejoras bootstrap.

PR B (compat matrix):
- Job 3.12 paralelo no bloqueante + reporte de compatibilidad.

PR C (promoción):
- Docker a 3.12 + baseline docs/scripts 3.12+ + job 3.12 obligatorio.

## 7. Nota sobre semver en frontend (incluido en esta rama)

En esta rama se incorpora visibilidad de semver en el footer junto a SHA/date de build:
- Fuente de versión: frontend/package.json
- Render en UI: BuildInfoFooter

Esto mejora trazabilidad entre release GitHub (v1.2.0) y versión visible en la app.
