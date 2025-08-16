# Script para iniciar el backend de SIFU
# Sistema de Índices Financieros del Uruguay

Write-Host "🐍 Iniciando SIFU Backend" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green

# Verificar si Python está instalado
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar si existe el archivo main.py
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: No se encuentra el archivo 'main.py'" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Directorio: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🚀 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL: http://localhost:8000" -ForegroundColor White
Write-Host "📖 API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "🔧 Auto-reload: Activado" -ForegroundColor White
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor FastAPI
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 