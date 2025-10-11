# Script para ejecutar el contenedor backend con TOTP configurado
# Uso: .\docker-run-backend.ps1

# Verificar que MONITORING_TOTP_SECRET esté configurado
if (-not $env:MONITORING_TOTP_SECRET) {
    Write-Host "⚠️  MONITORING_TOTP_SECRET no está configurado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Genera uno con:" -ForegroundColor Cyan
    Write-Host "python -c `"import pyotp; print(pyotp.random_base32())`"" -ForegroundColor White
    Write-Host ""
    Write-Host "Luego ejecuta:" -ForegroundColor Cyan
    Write-Host "`$env:MONITORING_TOTP_SECRET = 'TU_SECRET_AQUI'" -ForegroundColor White
    Write-Host ".\docker-run-backend.ps1" -ForegroundColor White
    exit 1
}

# Configurar session hours (default: 1)
$sessionHours = if ($env:MONITORING_SESSION_HOURS) { $env:MONITORING_SESSION_HOURS } else { "1" }

Write-Host "🐳 Iniciando contenedor backend con TOTP..." -ForegroundColor Green
Write-Host "Secret: $($env:MONITORING_TOTP_SECRET.Substring(0, 8))..." -ForegroundColor Gray
Write-Host "Session duration: $sessionHours hour(s)" -ForegroundColor Gray

# Ejecutar contenedor
docker run -d `
    --name sifu-backend-prod `
    -p 8000:8000 `
    -v ui_data:/app/data `
    -e PYTHONPATH=/app `
    -e PYTHONUNBUFFERED=1 `
    -e DATABASE_PATH=/app/data/ui_data.db `
    -e ENVIRONMENT=production `
    -e MONITORING_TOTP_SECRET="$env:MONITORING_TOTP_SECRET" `
    -e MONITORING_SESSION_HOURS="$sessionHours" `
    --restart unless-stopped `
    apmauj/sifu-backend:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Contenedor iniciado correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verificar salud:" -ForegroundColor Cyan
    Write-Host "curl http://localhost:8000/api/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Configurar authenticator app:" -ForegroundColor Cyan
    Write-Host "1. Cambia ENVIRONMENT=development temporalmente" -ForegroundColor White
    Write-Host "2. Visita http://localhost:8000/api/monitoring/setup" -ForegroundColor White
    Write-Host "3. Escanea el QR con Google Authenticator" -ForegroundColor White
    Write-Host "4. Vuelve a ENVIRONMENT=production" -ForegroundColor White
} else {
    Write-Host "❌ Error iniciando contenedor" -ForegroundColor Red
    exit 1
}
