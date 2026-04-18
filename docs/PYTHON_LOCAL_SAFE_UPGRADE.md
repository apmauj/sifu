# Python Local Safe Upgrade Guide

## Goal
Migrate local development runtime safely toward Python 3.12 without breaking the current environment.

## Current recommendation
- Keep `.venv` on stable Python 3.11 while compatibility work progresses.
- Validate Python 3.12 in a parallel environment (`.venv312-safe`).

## 1) Check installed Python interpreters (Windows)

```powershell
py -0p
```

Look for a stable 3.12 installation path.

## 2) Create a parallel venv (non-destructive)

```powershell
.\scripts\setup\new_python_venv.ps1 \
  -PythonExe "C:\Path\To\Python312\python.exe" \
  -VenvPath ".venv312-safe" \
  -InstallDependencies
```

This does not modify your existing `.venv`.

## 3) Validate basic compatibility

```powershell
.\.venv312-safe\Scripts\Activate.ps1
python --version
pytest -q --maxfail=1 --disable-warnings --tb=short --ignore=tests/demo --asyncio-mode=auto
```

## 4) If validation fails
- Keep using `.venv` (3.11 stable).
- Report failing dependency/test and keep 3.12 as experimental.

## 5) Promote 3.12 locally only when green
- Once compatibility passes, recreate `.venv` from Python 3.12 and rerun full checks.
- Keep a fallback environment (`.venv311-safe`) until CI and Docker are aligned.

## CI alignment
Use the manual workflow `Python Compatibility Check` to test 3.11/3.12 in GitHub Actions before promoting baseline.
