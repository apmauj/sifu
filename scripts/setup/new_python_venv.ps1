param(
    [string]$PythonExe,
    [string]$VenvPath = ".venv312-safe",
    [switch]$InstallDependencies
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    Write-Host "PythonExe is required. Example:" -ForegroundColor Yellow
    Write-Host "  .\\scripts\\setup\\new_python_venv.ps1 -PythonExe C:\\Python312\\python.exe -VenvPath .venv312-safe -InstallDependencies" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $PythonExe)) {
    Write-Host "Python executable not found: $PythonExe" -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $PythonExe" -ForegroundColor Cyan
& $PythonExe --version

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath" -ForegroundColor Cyan
    & $PythonExe -m venv $VenvPath
} else {
    Write-Host "Virtual environment already exists at $VenvPath" -ForegroundColor Yellow
}

$venvPython = Join-Path $VenvPath "Scripts/python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Could not locate venv python at $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host "Upgrading pip/setuptools/wheel in $VenvPath" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip setuptools wheel

if ($InstallDependencies) {
    Write-Host "Installing project dependencies in $VenvPath" -ForegroundColor Cyan
    & $venvPython -m pip install -r requirements.txt -r requirements-dev.txt
}

Write-Host "Done." -ForegroundColor Green
Write-Host "To activate: .\\$VenvPath\\Scripts\\Activate.ps1" -ForegroundColor Green
