# PowerShell script to start SIFU server
Write-Host "Starting SIFU Server..." -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:SIFU_SKIP_BOOTSTRAP = "1"

# Activate virtual environment
& ".venv/Scripts/Activate.ps1"

# Start the server with error handling
try {
    Write-Host "Starting FastAPI server on port 8003..." -ForegroundColor Yellow
    uvicorn main:app --host 127.0.0.1 --port 8003 --log-level info --reload
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
