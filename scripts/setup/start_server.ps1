# PowerShell script to start SIFU server
Write-Host "Starting SIFU Server..." -ForegroundColor Green
Write-Host ""

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$venvActivate = Join-Path $repoRoot '.venv\Scripts\Activate.ps1'

# Set environment variables
$env:SIFU_SKIP_BOOTSTRAP = "1"

# Activate virtual environment
& $venvActivate

# Start the server with error handling
try {
    Write-Host "Starting FastAPI server on port 8003..." -ForegroundColor Yellow
    Push-Location $repoRoot
    uvicorn main:app --host 127.0.0.1 --port 8003 --log-level info --reload
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
} finally {
    Pop-Location
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
