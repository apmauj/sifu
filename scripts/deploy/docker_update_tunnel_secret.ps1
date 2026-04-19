# Script para actualizar el secret VITE_PUBLIC_API_URL en GitHub
# con la URL del tunnel de Cloudflare

Write-Host "🔍 Buscando URL del tunnel en los logs..." -ForegroundColor Cyan

# Obtener la URL del tunnel desde los logs del contenedor
$tunnelUrl = docker logs sifu-tunnel 2>&1 | Select-String "https://.*trycloudflare.com" | Select-Object -Last 1 | ForEach-Object { $_.Line -replace '.*(https://[^ ]+).*', '$1' }

if (-not $tunnelUrl) {
    Write-Host "❌ No se pudo encontrar la URL del tunnel en los logs" -ForegroundColor Red
    exit 1
}

Write-Host "🌐 URL del tunnel encontrada: $tunnelUrl" -ForegroundColor Green

# Construir la URL completa de la API
$apiUrl = "$tunnelUrl/api"
Write-Host "🔗 URL de la API: $apiUrl" -ForegroundColor Green

# Verificar que la API esté respondiendo
Write-Host "🩺 Verificando que la API esté funcionando..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$tunnelUrl/api/health/simple" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "⚠️ API respondió con código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error al verificar la API: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Actualizar el secret en GitHub
Write-Host "🔄 Actualizando secret VITE_PUBLIC_API_URL en GitHub..." -ForegroundColor Yellow

# Nota: Requiere que el usuario esté autenticado con GitHub CLI
# y tenga permisos para actualizar secrets en el repositorio
try {
    # Usar GitHub CLI para actualizar el secret
    $apiUrl | gh secret set VITE_PUBLIC_API_URL --repo apmauj/sifu

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Secret actualizado exitosamente" -ForegroundColor Green
        Write-Host "📝 Nuevo valor: $apiUrl" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor White
        Write-Host "💡 El frontend se redeployará automáticamente con la nueva URL" -ForegroundColor Cyan
        Write-Host "🔄 Monitorea el progreso en: https://github.com/apmauj/sifu/actions" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Error al actualizar el secret" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error al ejecutar gh secret set: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "" -ForegroundColor White
    Write-Host "🔧 Solución alternativa:" -ForegroundColor Yellow
    Write-Host "1. Ve a https://github.com/apmauj/sifu/settings/secrets/actions" -ForegroundColor White
    Write-Host "2. Actualiza el secret VITE_PUBLIC_API_URL con el valor:" -ForegroundColor White
    Write-Host "   $apiUrl" -ForegroundColor Cyan
    exit 1
}