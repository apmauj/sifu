<#
.SYNOPSIS
    Script automatizado para actualización de túnel con validaciones completas

.DESCRIPTION
    Automatiza el flujo completo de actualización de túnel:
    1. Docker pull de la imagen más reciente del backend
    2. Recreación del backend con la nueva imagen
    3. Creación/actualización del túnel
    4. Validación de health check post-actualización
    5. Actualización del secret VITE_PUBLIC_API_URL en GitHub
    6. Opcional: disparo de redeploy del frontend

.PARAMETER Repo
    Repositorio de GitHub (default: apmauj/sifu)

.PARAMETER ImageTag
    Tag de la imagen Docker a usar (default: latest)

.PARAMETER TimeoutSeconds
    Timeout para esperar la URL del túnel (default: 120)

.PARAMETER TriggerDeploy
    Si se indica, dispara el workflow de deploy del frontend

.PARAMETER SkipIfUnchanged
    Si la URL no cambió, no actualiza el secret

.PARAMETER HealthCheckRetries
    Número de reintentos para health check (default: 5)

.PARAMETER HealthCheckInterval
    Intervalo entre health checks en segundos (default: 10)

.EXAMPLE
    ./automated_tunnel_update.ps1 -TriggerDeploy

.EXAMPLE
    ./automated_tunnel_update.ps1 -ImageTag "v1.2.3" -TimeoutSeconds 180

.NOTES
    Requisitos:
    - Docker y Docker Compose
    - GitHub CLI (gh) autenticado
    - Archivo docker-compose.tunnel.yml en el directorio raíz
    - Permisos para actualizar secrets en el repositorio
#>

param(
    [string]$Repo = 'apmauj/sifu',
    [string]$ImageTag = 'latest',
    [int]$TimeoutSeconds = 120,
    [switch]$TriggerDeploy,
    [switch]$SkipIfUnchanged,
    [int]$HealthCheckRetries = 5,
    [int]$HealthCheckInterval = 10
)

# Funciones de logging
function Write-Info($message) { 
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ℹ️  $message" -ForegroundColor Cyan 
}
function Write-Success($message) { 
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✅ $message" -ForegroundColor Green 
}
function Write-Warning($message) { 
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠️  $message" -ForegroundColor Yellow 
}
function Write-Error($message) { 
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ❌ $message" -ForegroundColor Red 
}

# Verificar prerrequisitos
function Test-Prerequisites {
    Write-Info "Verificando prerrequisitos..."
    
    # Verificar Docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker no está instalado o no está en PATH"
        exit 1
    }
    
    # Verificar Docker Compose
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose no está disponible"
        exit 1
    }
    
    # Verificar GitHub CLI si se va a actualizar secret
    if ($TriggerDeploy -or -not $SkipIfUnchanged) {
        if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
            Write-Error "GitHub CLI (gh) no está instalado o no está en PATH"
            exit 1
        }
        
        # Verificar autenticación de GitHub CLI
        gh auth status 1>$null 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "GitHub CLI no está autenticado. Ejecuta: gh auth login"
            Write-Info "Pasos para autenticar:"
            Write-Host "  1. gh auth login" -ForegroundColor DarkYellow
            Write-Host "  2. Selecciona GitHub.com -> HTTPS -> Login via browser" -ForegroundColor DarkYellow
            Write-Host "  3. Asegúrate de tener permisos para actualizar secrets en el repo" -ForegroundColor DarkYellow
            exit 1
        }
    }
    
    # Verificar archivo docker-compose.tunnel.yml
    if (-not (Test-Path './docker-compose.tunnel.yml')) {
        Write-Error "Archivo docker-compose.tunnel.yml no encontrado en el directorio actual"
        exit 1
    }
    
    Write-Success "Todos los prerrequisitos están satisfechos"
}

# Actualizar imagen del backend
function Update-BackendImage {
    param([string]$Tag)
    
    Write-Info "Actualizando imagen del backend (apmauj/sifu-backend:$Tag)..."
    
    try {
        $pullResult = docker pull "apmauj/sifu-backend:$Tag" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al hacer pull de la imagen: $pullResult"
            exit 1
        }
        Write-Success "Imagen actualizada exitosamente"
    }
    catch {
        Write-Error "Error inesperado al actualizar imagen: $_"
        exit 1
    }
}

# Recrear backend con nueva imagen
function Restart-Backend {
    Write-Info "Recreando backend con la nueva imagen..."
    
    try {
        # Parar y remover contenedor existente
        docker compose -f docker-compose.tunnel.yml down backend 2>$null | Out-Null
        
        # Levantar con la nueva imagen
        $composeResult = docker compose -f docker-compose.tunnel.yml up -d backend 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al recrear backend: $composeResult"
            exit 1
        }
        
        Write-Success "Backend recreado exitosamente"
        
        # Esperar a que el backend esté listo
        Write-Info "Esperando a que el backend esté listo..."
        $ready = $false
        for ($i = 0; $i -lt 30; $i++) {
            try {
                $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction Stop
                if ($healthResponse.status -eq 'ok') {
                    $ready = $true
                    break
                }
            }
            catch {
                # Backend aún no está listo, continuar esperando
            }
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline -ForegroundColor DarkGray
        }
        Write-Host ""
        
        if ($ready) {
            Write-Success "Backend está listo y respondiendo"
        } else {
            Write-Warning "Backend no respondió en el tiempo esperado, pero continuando..."
        }
    }
    catch {
        Write-Error "Error inesperado al recrear backend: $_"
        exit 1
    }
}

# Crear/actualizar túnel
function Start-Tunnel {
    Write-Info "Iniciando túnel..."
    
    try {
        # Recrear túnel
        $tunnelResult = docker compose -f docker-compose.tunnel.yml up -d --force-recreate --remove-orphans tunnel 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al iniciar túnel: $tunnelResult"
            exit 1
        }
        
        Write-Success "Túnel iniciado"
    }
    catch {
        Write-Error "Error inesperado al iniciar túnel: $_"
        exit 1
    }
}

# Obtener URL del túnel
function Get-TunnelUrl {
    param([int]$Timeout)
    
    Write-Info "Obteniendo URL del túnel (timeout: $Timeout segundos)..."
    
    $regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
    $startTime = Get-Date
    $tunnelUrl = $null
    
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($Timeout)) {
        try {
            $logs = docker logs --tail 50 sifu-tunnel 2>&1
            $match = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -First 1
            
            if ($match) {
                $tunnelUrl = $match.Matches[0].Value
                break
            }
        }
        catch {
            # Error al leer logs, continuar intentando
        }
        
        Start-Sleep -Seconds 2
        Write-Host "." -NoNewline -ForegroundColor DarkGray
    }
    Write-Host ""
    
    if (-not $tunnelUrl) {
        Write-Error "No se pudo obtener URL del túnel en el tiempo especificado"
        Write-Info "Últimos logs del túnel:"
        docker logs --tail 100 sifu-tunnel
        exit 1
    }
    
    Write-Success "URL del túnel obtenida: $tunnelUrl"
    return $tunnelUrl
}

# Validar health check post-actualización
function Test-HealthCheck {
    param(
        [string]$TunnelUrl,
        [int]$Retries,
        [int]$Interval
    )
    
    Write-Info "Validando health check del sistema ($Retries reintentos, intervalo: $Interval segundos)..."
    
    $apiUrl = "$TunnelUrl/api"
    $healthEndpoint = "$apiUrl/health"
    $success = $false
    
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            Write-Info "Health check intento $i/$Retries..."
            
            # Health check simple
            $simpleHealth = Invoke-RestMethod -Uri "$healthEndpoint/simple" -TimeoutSec 10 -ErrorAction Stop
            if ($simpleHealth.status -eq 'ok') {
                Write-Success "Health check simple: OK"
                
                # Health check avanzado
                $advancedHealth = Invoke-RestMethod -Uri "$healthEndpoint" -TimeoutSec 15 -ErrorAction Stop
                if ($advancedHealth.overall_status -eq 'healthy') {
                    Write-Success "Health check avanzado: HEALTHY"
                    $success = $true
                    break
                } else {
                    Write-Warning "Health check avanzado: $($advancedHealth.overall_status)"
                    Write-Info "Detalles: $($advancedHealth | ConvertTo-Json -Depth 2)"
                }
            } else {
                Write-Warning "Health check simple: $($simpleHealth.status)"
            }
        }
        catch {
            Write-Warning "Error en health check intento $i`: $($_.Exception.Message)"
        }
        
        if ($i -lt $Retries) {
            Write-Info "Esperando $Interval segundos antes del siguiente intento..."
            Start-Sleep -Seconds $Interval
        }
    }
    
    if (-not $success) {
        Write-Error "Health check falló después de $Retries intentos"
        Write-Info "Logs del backend:"
        docker logs --tail 50 sifu-backend
        return $false
    }
    
    Write-Success "Health check completado exitosamente"
    return $true
}

# Actualizar secret en GitHub
function Update-GitHubSecret {
    param(
        [string]$SecretValue,
        [string]$Repository
    )
    
    Write-Info "Actualizando secret VITE_PUBLIC_API_URL en GitHub..."
    
    try {
        $secretResult = Write-Output $SecretValue | gh secret set VITE_PUBLIC_API_URL -R $Repository 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Error al actualizar secret: $secretResult"
            exit 1
        }
        Write-Success "Secret actualizado exitosamente"
        Write-Info "Nuevo valor: $SecretValue"
    }
    catch {
        Write-Error "Error inesperado al actualizar secret: $_"
        exit 1
    }
}

# Disparar workflow de deploy
function Invoke-DeployWorkflow {
    param([string]$Repository)
    
    Write-Info "Disparando workflow de deploy del frontend..."
    
    try {
        $workflowResult = gh workflow run .github/workflows/ci-cd.yml -R $Repository -f force_frontend_deploy=true 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Error al disparar workflow: $workflowResult"
            return $false
        }
        Write-Success "Workflow disparado exitosamente"
        Write-Info "Monitorea el progreso en: https://github.com/$Repository/actions"
        return $true
    }
    catch {
        Write-Warning "Error inesperado al disparar workflow: $_"
        return $false
    }
}

# Guardar estado para comparaciones futuras
function Save-TunnelState {
    param([string]$ApiUrl)
    
    $stateFile = Join-Path $PSScriptRoot '..' '..' '.tunnel_last_url.txt'
    try {
        $ApiUrl | Out-File -FilePath $stateFile -Encoding UTF8 -Force
        Write-Info "Estado guardado en: $stateFile"
    }
    catch {
        Write-Warning "No se pudo guardar estado: $_"
    }
}

# Función principal
function Main {
    Write-Host "🚀 SIFU - Actualización Automatizada de Túnel" -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Magenta
    
    # Verificar prerrequisitos
    Test-Prerequisites
    
    # Leer estado anterior
    $stateFile = Join-Path $PSScriptRoot '..' '..' '.tunnel_last_url.txt'
    $previousUrl = $null
    try {
        $previousUrl = (Get-Content $stateFile -ErrorAction SilentlyContinue).Trim()
    }
    catch {
        # Archivo no existe o no se puede leer, continuar
    }
    
    # Actualizar imagen del backend
    Update-BackendImage -Tag $ImageTag
    
    # Recrear backend
    Restart-Backend
    
    # Iniciar túnel
    Start-Tunnel
    
    # Obtener URL del túnel
    $tunnelUrl = Get-TunnelUrl -Timeout $TimeoutSeconds
    $apiUrl = "$tunnelUrl/api"
    
    # Verificar si la URL cambió
    if ($SkipIfUnchanged -and $previousUrl -and $previousUrl -eq $apiUrl) {
        Write-Info "URL no ha cambiado ($apiUrl). Saltando actualización de secret."
        
        if ($TriggerDeploy) {
            Write-Info "Disparando deploy aunque la URL no cambió (porque -TriggerDeploy fue especificado)"
            $deploySuccess = Invoke-DeployWorkflow -Repository $Repo
            if (-not $deploySuccess) {
                Write-Warning "No se pudo disparar el workflow de deploy"
            }
        } else {
            Write-Info "No hay nada que hacer (URL sin cambios y no se solicitó deploy)"
            exit 0
        }
    } else {
        # Validar health check
        $healthOk = Test-HealthCheck -TunnelUrl $tunnelUrl -Retries $HealthCheckRetries -Interval $HealthCheckInterval
        
        if (-not $healthOk) {
            Write-Error "Health check falló. No se actualizará el secret."
            exit 1
        }
        
        # Actualizar secret en GitHub
        Update-GitHubSecret -SecretValue $apiUrl -Repository $Repo
        
        # Guardar estado
        Save-TunnelState -ApiUrl $apiUrl
        
        # Disparar workflow si se solicita
        if ($TriggerDeploy) {
            $deploySuccess = Invoke-DeployWorkflow -Repository $Repo
            if (-not $deploySuccess) {
                Write-Warning "No se pudo disparar el workflow de deploy, pero el secret fue actualizado"
            }
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Actualización completada exitosamente!" -ForegroundColor Green
    Write-Host "📋 Resumen:" -ForegroundColor Cyan
    Write-Host "   • Backend actualizado: apmauj/sifu-backend:$ImageTag" -ForegroundColor White
    Write-Host "   • Túnel URL: $tunnelUrl" -ForegroundColor White
    Write-Host "   • API URL: $apiUrl" -ForegroundColor White
    if ($TriggerDeploy) {
        Write-Host "   • Workflow de deploy: Disparado" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "🔗 URLs útiles:" -ForegroundColor Cyan
    Write-Host "   • Health check: $apiUrl/health" -ForegroundColor White
    Write-Host "   • Frontend: https://apmauj.github.io/sifu/" -ForegroundColor White
    Write-Host "   • GitHub Actions: https://github.com/$Repo/actions" -ForegroundColor White
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Error "Error crítico durante la ejecución: $_"
    exit 1
}
