# Changelog - 19 de Abril 2026

## Python 3.12 Baseline Promotion

Este documento registra la promoción del baseline oficial de Python para SIFU.

---

## ✅ Cambios incluidos

### Runtime y documentación
- `config/docker/Dockerfile`: base actualizada a `python:3.12-slim`.
- `README.md`: prerequisito local actualizado a Python `3.12+`.
- `docs/TECHNICAL_SUMMARY.md`: runtime actualizado a Python `3.12+`.

### CI/CD y seguridad backend
- `.github/workflows/ci-cd.yml`:
  - `Security Audit Backend` y `Backend Tests` ahora usan `actions/setup-python@v5` con `python-version: '3.12'`.
  - Se elimina dependencia implícita del `.venv` persistente del runner para jobs backend.
- `.github/workflows/security-audit.yml`:
  - `backend-pip-audit` usa `actions/setup-python@v5` con `python-version: '3.12'`.

### Compatibilidad validada
- Workflow manual de matriz (`3.11`, `3.12`) ejecutado en `master`:
  - Run: `24617141330`
  - Resultado: `success` en ambos jobs.

---

## ⚠️ Alcance de limpieza

- Este bump establece baseline oficial 3.12 para runtime/docs/CI backend.
- No elimina automáticamente todas las referencias históricas a versiones previas en documentación de contexto o notas de migración.

---

## 📏 Medición de impacto

Se añade guía de medición para cuantificar mejora en:
- performance (latencia y tiempos de job),
- estabilidad (pass rate, flakes),
- seguridad (pip-audit).

Ver: `docs/PYTHON_312_MEASUREMENT_PLAN.md`.

---

## 🔖 Release sugerido

Después del merge del PR de promoción a `master`, crear release `v1.3.0` con notas basadas en este changelog.
