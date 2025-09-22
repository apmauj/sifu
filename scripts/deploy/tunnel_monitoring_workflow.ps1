<#
.SYNOPSIS
    Workflow de monitoreo programado para el túnel de SIFU

.DESCRIPTION
    Script para monitorear periódicamente el estado del túnel y alertar en caso de problemas:
    - Verifica que la API esté respondiendo
    - Verifica que los datos estén actualizados
    - Envía alertas en caso de problemas
    - Puede ejecutarse como tarea programada o desde CI/CD

.PARAMETER ApiUrl
    URL base de la API (default: detecta automáticamente desde logs)

.PARAMETER AlertWebhook
    Webhook para enviar alertas (Slack, Discord, etc.)

.PARAMETER MaxDataAge
    Edad máxima permitida para los datos en minutos (default: 30)

.PARAMETER CheckInterval
    Intervalo entre checks en minutos (default: 5)

.PARAMETER MaxRetries
    Número máximo de reintentos antes de alertar (default: 3)

.PARAMETER LogFile
    Archivo de log para guardar el historial (default: tunnel_monitoring.log)

.EXAMPLE
    ./tunnel_monitoring_workflow.ps1 -AlertWebhook "https://hooks.slack.com/..." -MaxDataAge 60

.EXAMPLE
    ./tunnel_monitoring_workflow.ps1 -ApiUrl "https://abc123.trycloudflare.com/api" -CheckInterval 10

.NOTES
    Este script está diseñado para ejecutarse como tarea programada o en un loop continuo.
    Para tarea programada, usar: -CheckInterval 0 (solo una ejecución)
#>

param(
    [string]$ApiUrl = "",
    [string]$AlertWebhook = "",
    [int]$MaxDataAge = 30,
    [int]$CheckInterval = 5,
    [int]$MaxRetries = 3,
    [string]$LogFile = "tunnel_monitoring.log"
)

# Configuración de colores para logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARN" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor Cyan }
    }
    
    # Guardar en archivo de log
    try {
        Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
    }
    catch {
        Write-Host "Warning: No se pudo escribir al archivo de log: $_" -ForegroundColor Yellow
    }
}

# Detectar URL del túnel automáticamente
function Get-TunnelUrlFromLogs {
    try {
        $logs = docker logs --tail 100 sifu-tunnel 2>&1
        $regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
        $match = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -First 1
        
        if ($match) {
            return $match.Matches[0].Value
        }
    }
    catch {
        Write-Log "Error al leer logs del túnel: $_" "ERROR"
    }
    
    return $null
}

# Verificar health check de la API
function Test-ApiHealth {
    param([string]$BaseUrl)
    
    try {
        $healthUrl = "$BaseUrl/health"
        Write-Log "Verificando health check en: $healthUrl"
        
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10 -ErrorAction Stop
        
        if ($response.overall_status -eq "healthy") {
            Write-Log "Health check: HEALTHY" "SUCCESS"
            return @{
                Status = "healthy"
                Details = $response
            }
        } elseif ($response.overall_status -eq "warning") {
            Write-Log "Health check: WARNING - $($response.message)" "WARN"
            return @{
                Status = "warning"
                Details = $response
            }
        } else {
            Write-Log "Health check: CRITICAL - $($response.message)" "ERROR"
            return @{
                Status = "critical"
                Details = $response
            }
        }
    }
    catch {
        Write-Log "Error en health check: $($_.Exception.Message)" "ERROR"
        return @{
            Status = "error"
            Details = $_.Exception.Message
        }
    }
}

# Verificar frescura de los datos
function Test-DataFreshness {
    param([string]$BaseUrl, [int]$MaxAgeMinutes)
    
    try {
        # Verificar datos UI (más críticos)
        $uiUrl = "$BaseUrl/ui/latest"
        Write-Log "Verificando frescura de datos UI en: $uiUrl"
        
        $uiResponse = Invoke-RestMethod -Uri $uiUrl -TimeoutSec 10 -ErrorAction Stop
        
        if ($uiResponse.data -and $uiResponse.data.date) {
            $dataDate = [DateTime]::Parse($uiResponse.data.date)
            $ageMinutes = (Get-Date) - $dataDate | Select-Object -ExpandProperty TotalMinutes
            
            Write-Log "Datos UI - Fecha: $($uiResponse.data.date), Edad: $([Math]::Round($ageMinutes, 1)) minutos"
            
            if ($ageMinutes -le $MaxAgeMinutes) {
                Write-Log "Datos UI: FRESCOS" "SUCCESS"
                return @{
                    Status = "fresh"
                    AgeMinutes = $ageMinutes
                    DataDate = $uiResponse.data.date
                }
            } else {
                Write-Log "Datos UI: ANTIGUOS ($([Math]::Round($ageMinutes, 1)) minutos > $MaxAgeMinutes)" "ERROR"
                return @{
                    Status = "stale"
                    AgeMinutes = $ageMinutes
                    DataDate = $uiResponse.data.date
                }
            }
        } else {
            Write-Log "Datos UI: NO DISPONIBLES" "ERROR"
            return @{
                Status = "unavailable"
                Details = "No se encontraron datos en la respuesta"
            }
        }
    }
    catch {
        Write-Log "Error al verificar frescura de datos: $($_.Exception.Message)" "ERROR"
        return @{
            Status = "error"
            Details = $_.Exception.Message
        }
    }
}

# Verificar métricas del sistema
function Test-SystemMetrics {
    param([string]$BaseUrl)
    
    try {
        $metricsUrl = "$BaseUrl/metrics"
        Write-Log "Verificando métricas del sistema en: $metricsUrl"
        
        $metricsResponse = Invoke-RestMethod -Uri $metricsUrl -TimeoutSec 10 -ErrorAction Stop
        
        $issues = @()
        
        # Verificar métricas críticas
        if ($metricsResponse.ui_freshness -and $metricsResponse.ui_freshness.ui_gap_detected -eq $true) {
            $issues += "Gap detectado en datos UI"
        }
        
        if ($metricsResponse.cache_status -and $metricsResponse.cache_status.brou_cache_age_seconds -gt 3600) {
            $issues += "Caché BROU muy antiguo ($($metricsResponse.cache_status.brou_cache_age_seconds) segundos)"
        }
        
        if ($metricsResponse.system -and $metricsResponse.system.memory_usage_percent -gt 90) {
            $issues += "Uso de memoria alto ($($metricsResponse.system.memory_usage_percent)%)"
        }
        
        if ($issues.Count -eq 0) {
            Write-Log "Métricas del sistema: OK" "SUCCESS"
            return @{
                Status = "ok"
                Details = $metricsResponse
            }
        } else {
            Write-Log "Métricas del sistema: PROBLEMAS - $($issues -join ', ')" "WARN"
            return @{
                Status = "issues"
                Details = $metricsResponse
                Issues = $issues
            }
        }
    }
    catch {
        Write-Log "Error al verificar métricas: $($_.Exception.Message)" "ERROR"
        return @{
            Status = "error"
            Details = $_.Exception.Message
        }
    }
}

# Enviar alerta
function Send-Alert {
    param(
        [string]$Message,
        [string]$Level = "ERROR",
        [hashtable]$Details = @{}
    )
    
    if (-not $AlertWebhook) {
        Write-Log "No se configuró webhook para alertas, saltando envío" "WARN"
        return
    }
    
    try {
        $alertPayload = @{
            text = "🚨 **SIFU Tunnel Alert - $Level**"
            attachments = @(
                @{
                    color = switch ($Level) {
                        "ERROR" { "danger" }
                        "WARN" { "warning" }
                        default { "good" }
                    }
                    fields = @(
                        @{
                            title = "Mensaje"
                            value = $Message
                            short = $false
                        },
                        @{
                            title = "Timestamp"
                            value = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
                            short = $true
                        },
                        @{
                            title = "API URL"
                            value = $ApiUrl
                            short = $true
                        }
                    )
                }
            )
        }
        
        # Agregar detalles adicionales si existen
        if ($Details.Count -gt 0) {
            $alertPayload.attachments[0].fields += @{
                title = "Detalles"
                value = ($Details | ConvertTo-Json -Depth 2)
                short = $false
            }
        }
        
        $jsonPayload = $alertPayload | ConvertTo-Json -Depth 3
        $response = Invoke-RestMethod -Uri $AlertWebhook -Method Post -Body $jsonPayload -ContentType "application/json" -TimeoutSec 10
        
        Write-Log "Alerta enviada exitosamente" "SUCCESS"
    }
    catch {
        Write-Log "Error al enviar alerta: $($_.Exception.Message)" "ERROR"
    }
}

# Función principal de monitoreo
function Start-Monitoring {
    param([string]$BaseUrl)
    
    Write-Log "Iniciando monitoreo de túnel SIFU"
    Write-Log "API URL: $BaseUrl"
    Write-Log "Edad máxima de datos: $MaxDataAge minutos"
    Write-Log "Intervalo de verificación: $CheckInterval minutos"
    
    $consecutiveFailures = 0
    $lastSuccessfulCheck = Get-Date
    
    while ($true) {
        $checkStart = Get-Date
        Write-Log "=== Iniciando verificación ==="
        
        $allChecksPassed = $true
        
        # 1. Health Check
        $healthResult = Test-ApiHealth -BaseUrl $BaseUrl
        if ($healthResult.Status -in @("critical", "error")) {
            $allChecksPassed = $false
        }
        
        # 2. Frescura de datos
        $dataResult = Test-DataFreshness -BaseUrl $BaseUrl -MaxAgeMinutes $MaxDataAge
        if ($dataResult.Status -in @("stale", "unavailable", "error")) {
            $allChecksPassed = $false
        }
        
        # 3. Métricas del sistema
        $metricsResult = Test-SystemMetrics -BaseUrl $BaseUrl
        if ($metricsResult.Status -in @("error")) {
            $allChecksPassed = $false
        }
        
        # Evaluar resultados
        if ($allChecksPassed) {
            $consecutiveFailures = 0
            $lastSuccessfulCheck = Get-Date
            Write-Log "✅ Todas las verificaciones pasaron" "SUCCESS"
        } else {
            $consecutiveFailures++
            Write-Log "❌ Algunas verificaciones fallaron (fallos consecutivos: $consecutiveFailures)" "ERROR"
            
            # Enviar alerta si se supera el umbral
            if ($consecutiveFailures -ge $MaxRetries) {
                $alertMessage = "El túnel de SIFU ha fallado $consecutiveFailures verificaciones consecutivas"
                $alertDetails = @{
                    HealthCheck = $healthResult
                    DataFreshness = $dataResult
                    SystemMetrics = $metricsResult
                    LastSuccessfulCheck = $lastSuccessfulCheck
                }
                
                Send-Alert -Message $alertMessage -Level "ERROR" -Details $alertDetails
                
                # Resetear contador después de enviar alerta
                $consecutiveFailures = 0
            }
        }
        
        $checkDuration = (Get-Date) - $checkStart
        Write-Log "Verificación completada en $($checkDuration.TotalSeconds.ToString('F1')) segundos"
        
        # Si CheckInterval es 0, solo ejecutar una vez
        if ($CheckInterval -eq 0) {
            Write-Log "Modo de ejecución única, finalizando"
            break
        }
        
        # Esperar antes del siguiente check
        Write-Log "Esperando $CheckInterval minutos hasta la próxima verificación..."
        Start-Sleep -Seconds ($CheckInterval * 60)
    }
    
    Write-Log "Monitoreo finalizado"
}

# Función principal
function Main {
    Write-Host "🔍 SIFU - Monitoreo de Túnel" -ForegroundColor Magenta
    Write-Host "=" * 50 -ForegroundColor Magenta
    
    # Determinar URL de la API
    if (-not $ApiUrl) {
        Write-Log "Detectando URL del túnel automáticamente..."
        $tunnelUrl = Get-TunnelUrlFromLogs
        
        if (-not $tunnelUrl) {
            Write-Log "No se pudo detectar la URL del túnel automáticamente" "ERROR"
            Write-Log "Asegúrate de que el túnel esté ejecutándose o proporciona la URL con -ApiUrl" "ERROR"
            exit 1
        }
        
        $ApiUrl = "$tunnelUrl/api"
        Write-Log "URL del túnel detectada: $tunnelUrl" "SUCCESS"
    }
    
    Write-Log "URL de la API: $ApiUrl"
    
    # Verificar conectividad inicial
    try {
        $testResponse = Invoke-RestMethod -Uri "$ApiUrl/health/simple" -TimeoutSec 10 -ErrorAction Stop
        Write-Log "Conectividad inicial: OK" "SUCCESS"
    }
    catch {
        Write-Log "No se puede conectar a la API: $($_.Exception.Message)" "ERROR"
        exit 1
    }
    
    # Iniciar monitoreo
    Start-Monitoring -BaseUrl $ApiUrl
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Log "Error crítico durante la ejecución: $_" "ERROR"
    exit 1
}
