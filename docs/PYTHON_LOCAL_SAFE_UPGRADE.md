# Python Local Safe Upgrade Guide

## Goal
Keep local development aligned with the current Python 3.12 baseline using a single `.venv`.

## Current recommendation
- Use `.venv` on Python 3.12 as the primary local environment.
- The previous fallback stages with `.venv311-safe` and `.venv312-safe` are closed and can be removed.

## 1) Check installed Python interpreters (Windows)

```powershell
py -0p
```

Look for a stable 3.12 installation path.

## 2) Create `.venv` on Python 3.12

```powershell
.\scripts\setup\new_python_venv.ps1 \
  -PythonExe "C:\Path\To\Python312\python.exe" \
  -VenvPath ".venv" \
  -InstallDependencies
```

This recreates `.venv` with Python 3.12.

## 3) Validate basic compatibility

```powershell
\.\.venv\Scripts\Activate.ps1
python --version
pytest -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto
```

## 4) If validation fails
- Recreate `.venv` with Python 3.12 and rerun dependency install + tests.
- Keep failures documented and fix incrementally (deps/tests).

## 5) Promote 3.12 locally only when green
- Once compatibility passes, keep `.venv` as the only active local environment.

## 6) Cleanup old fallback environment
If old fallback environments still exist locally, it is safe to remove them:

```powershell
Remove-Item -Recurse -Force .venv311-safe
Remove-Item -Recurse -Force .venv312-safe
```

## CI alignment
CI and runtime are already aligned on Python 3.12 baseline.
