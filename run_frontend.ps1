# Script para iniciar el frontend de SIFU
# Sistema de Índices Financieros del Uruguay

Write-Host "⚛️  Iniciando SIFU Frontend" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Verificar si existe el directorio frontend
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: No se encuentra el directorio 'frontend'" -ForegroundColor Red
    exit 1
}

# Cambiar al directorio frontend
Set-Location frontend

Write-Host "📁 Directorio: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🚀 Iniciando servidor de desarrollo..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Hot Reload: Activado" -ForegroundColor White
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor de desarrollo
npm run dev 