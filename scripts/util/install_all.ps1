Param(
  [switch]$Dev,
  [switch]$Excel
)

Write-Host "Activating venv if present..." -ForegroundColor Cyan
if (Test-Path .venv/Scripts/Activate.ps1) { . .venv/Scripts/Activate.ps1 }

Write-Host "Upgrading pip" -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "Installing core requirements" -ForegroundColor Cyan
python -m pip install -r requirements-core.txt

if ($Excel) {
  Write-Host "Installing Excel (pandas) extras" -ForegroundColor Cyan
  python -m pip install -r requirements-excel.txt
}

if ($Dev) {
  Write-Host "Installing dev requirements" -ForegroundColor Cyan
  python -m pip install -r requirements-dev.txt
}

Write-Host "Done." -ForegroundColor Green
