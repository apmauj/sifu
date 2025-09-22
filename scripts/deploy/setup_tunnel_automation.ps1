<#
.SYNOPSIS
    Script de configuración para la automatización de túnel de SIFU

.DESCRIPTION
    Configura y prepara el entorno para usar los scripts de automatización de túnel:
    - Crea tareas programadas para monitoreo
    - Configura variables de entorno
    - Establece permisos necesarios
    - Crea archivos de configuración

.PARAMETER SetupMonitoring
    Configurar tarea programada para monitoreo

.PARAMETER MonitoringInterval
    Intervalo de monitoreo en minutos (default: 10)

.PARAMETER AlertWebhook
    Webhook para alertas (Slack, Discord, etc.)

.PARAMETER MaxDataAge
    Edad máxima de datos en minutos (default: 30)

.EXAMPLE
    ./setup_tunnel_automation.ps1 -SetupMonitoring -AlertWebhook "https://hooks.slack.com/..."

.EXAMPLE
    ./setup_tunnel_automation.ps1 -SetupMonitoring -MonitoringInterval 5 -MaxDataAge 60
#>

param(
    [switch]$SetupMonitoring,
    [int]$MonitoringInterval = 10,
    [string]$AlertWebhook = "",
    [int]$MaxDataAge = 30
)

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

# Verificar si se está ejecutando como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Crear archivo de configuración
function New-ConfigFile {
    param(
        [string]$ConfigPath,
        [hashtable]$Config
    )
    
    try {
        $configJson = $Config | ConvertTo-Json -Depth 3
        $configJson | Out-File -FilePath $ConfigPath -Encoding UTF8 -Force
        Write-Success "Archivo de configuración creado: $ConfigPath"
    }
    catch {
        Write-Error "Error al crear archivo de configuración: $_"
        return $false
    }
    return $true
}

# Configurar tarea programada para monitoreo
function Set-MonitoringTask {
    param(
        [int]$IntervalMinutes,
        [string]$WebhookUrl,
        [int]$MaxAgeMinutes
    )
    
    if (-not (Test-Administrator)) {
        Write-Error "Se requieren permisos de administrador para crear tareas programadas"
        Write-Info "Ejecuta PowerShell como administrador y vuelve a intentar"
        return $false
    }
    
    try {
        $scriptPath = Join-Path $PSScriptRoot "tunnel_monitoring_workflow.ps1"
        $taskName = "SIFU-Tunnel-Monitoring"
        
        # Crear comando de la tarea
        $taskCommand = "powershell.exe"
        $taskArguments = "-ExecutionPolicy Bypass -File `"$scriptPath`" -CheckInterval 0 -MaxDataAge $MaxAgeMinutes"
        
        if ($WebhookUrl) {
            $taskArguments += " -AlertWebhook `"$WebhookUrl`""
        }
        
        # Eliminar tarea existente si existe
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Info "Tarea existente eliminada"
        }
        
        # Crear acción de la tarea
        $action = New-ScheduledTaskAction -Execute $taskCommand -Argument $taskArguments
        
        # Crear trigger (cada X minutos)
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 365)
        
        # Configurar opciones de la tarea
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
        
        # Crear y registrar la tarea
        $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Description "Monitoreo automático del túnel SIFU - Verifica cada $IntervalMinutes minutos"
        
        Register-ScheduledTask -TaskName $taskName -InputObject $task -User "SYSTEM" -Force | Out-Null
        
        Write-Success "Tarea programada creada: $taskName"
        Write-Info "Intervalo: $IntervalMinutes minutos"
        Write-Info "Webhook: $(if($WebhookUrl) { $WebhookUrl } else { 'No configurado' })"
        Write-Info "Edad máxima de datos: $MaxAgeMinutes minutos"
        
        return $true
    }
    catch {
        Write-Error "Error al crear tarea programada: $_"
        return $false
    }
}

# Crear archivos de configuración
function New-ConfigurationFiles {
    Write-Info "Creando archivos de configuración..."
    
    # Configuración del túnel
    $tunnelConfig = @{
        DefaultImageTag = "latest"
        TimeoutSeconds = 120
        HealthCheckRetries = 5
        HealthCheckInterval = 10
        AutoTriggerDeploy = $false
    }
    
    $tunnelConfigPath = Join-Path $PSScriptRoot "tunnel_config.json"
    if (New-ConfigFile -ConfigPath $tunnelConfigPath -Config $tunnelConfig) {
        Write-Info "Configuración del túnel: $tunnelConfigPath"
    }
    
    # Configuración de monitoreo
    $monitoringConfig = @{
        CheckInterval = $MonitoringInterval
        MaxDataAge = $MaxDataAge
        MaxRetries = 3
        AlertWebhook = $AlertWebhook
        LogFile = "tunnel_monitoring.log"
        EnableAlerts = [bool]$AlertWebhook
    }
    
    $monitoringConfigPath = Join-Path $PSScriptRoot "monitoring_config.json"
    if (New-ConfigFile -ConfigPath $monitoringConfigPath -Config $monitoringConfig) {
        Write-Info "Configuración de monitoreo: $monitoringConfigPath"
    }
    
    return $true
}

# Crear script de ejemplo para uso manual
function New-ExampleScripts {
    Write-Info "Creando scripts de ejemplo..."
    
    # Script de actualización manual
    $updateScript = @'
# Ejemplo de uso del script de actualización de túnel
# Ejecutar desde el directorio raíz del proyecto SIFU

# Actualización básica
.\scripts\deploy\automated_tunnel_update.ps1

# Actualización con deploy automático
.\scripts\deploy\automated_tunnel_update.ps1 -TriggerDeploy

# Actualización con imagen específica
.\scripts\deploy\automated_tunnel_update.ps1 -ImageTag "v1.2.3" -TriggerDeploy

# Monitoreo manual (una sola verificación)
.\scripts\deploy\tunnel_monitoring_workflow.ps1 -CheckInterval 0

# Monitoreo continuo con alertas
.\scripts\deploy\tunnel_monitoring_workflow.ps1 -AlertWebhook "https://hooks.slack.com/..." -CheckInterval 5
'@
    
    $updateScriptPath = Join-Path $PSScriptRoot "ejemplos_uso.ps1"
    $updateScript | Out-File -FilePath $updateScriptPath -Encoding UTF8 -Force
    Write-Success "Script de ejemplos creado: $updateScriptPath"
    
    # Script de prueba de conectividad
    $testScript = @'
# Script de prueba de conectividad del túnel
# Verifica que todos los endpoints estén funcionando

param(
    [string]$ApiUrl = ""
)

if (-not $ApiUrl) {
    Write-Host "Detectando URL del túnel..."
    $logs = docker logs --tail 100 sifu-tunnel 2>&1
    $regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
    $match = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -First 1
    
    if ($match) {
        $ApiUrl = "$($match.Matches[0].Value)/api"
    } else {
        Write-Host "No se pudo detectar la URL del túnel" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Probando conectividad en: $ApiUrl" -ForegroundColor Cyan

# Endpoints a probar
$endpoints = @(
    "/health/simple",
    "/health",
    "/ui/latest",
    "/metrics",
    "/brou/current",
    "/exchange/latest"
)

foreach ($endpoint in $endpoints) {
    $url = "$ApiUrl$endpoint"
    try {
        $response = Invoke-RestMethod -Uri $url -TimeoutSec 10
        Write-Host "✅ $endpoint" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $endpoint - $($_.Exception.Message)" -ForegroundColor Red
    }
}
'@
    
    $testScriptPath = Join-Path $PSScriptRoot "test_connectivity.ps1"
    $testScript | Out-File -FilePath $testScriptPath -Encoding UTF8 -Force
    Write-Success "Script de prueba creado: $testScriptPath"
}

# Función principal
function Main {
    Write-Host "🔧 SIFU - Configuración de Automatización de Túnel" -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Magenta
    
    # Verificar prerrequisitos
    Write-Info "Verificando prerrequisitos..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker no está instalado o no está en PATH"
        exit 1
    }
    
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Warning "GitHub CLI (gh) no está instalado. Algunas funciones no estarán disponibles."
    }
    
    # Crear archivos de configuración
    New-ConfigurationFiles
    
    # Crear scripts de ejemplo
    New-ExampleScripts
    
    # Configurar monitoreo si se solicita
    if ($SetupMonitoring) {
        Write-Info "Configurando tarea programada de monitoreo..."
        
        if (Set-MonitoringTask -IntervalMinutes $MonitoringInterval -WebhookUrl $AlertWebhook -MaxAgeMinutes $MaxDataAge) {
            Write-Success "Configuración de monitoreo completada"
        } else {
            Write-Warning "No se pudo configurar el monitoreo automático"
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Configuración completada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Revisar archivos de configuración en: $PSScriptRoot" -ForegroundColor White
    Write-Host "2. Probar conectividad: .\scripts\deploy\test_connectivity.ps1" -ForegroundColor White
    Write-Host "3. Actualizar túnel: .\scripts\deploy\automated_tunnel_update.ps1 -TriggerDeploy" -ForegroundColor White
    
    if ($SetupMonitoring) {
        Write-Host "4. Monitoreo automático configurado (cada $MonitoringInterval minutos)" -ForegroundColor White
    } else {
        Write-Host "4. Para configurar monitoreo automático, ejecuta:" -ForegroundColor White
        Write-Host "   .\scripts\deploy\setup_tunnel_automation.ps1 -SetupMonitoring" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "📚 Documentación:" -ForegroundColor Cyan
    Write-Host "• Ejemplos de uso: .\scripts\deploy\ejemplos_uso.ps1" -ForegroundColor White
    Write-Host "• Configuración: .\scripts\deploy\*.json" -ForegroundColor White
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Error "Error crítico durante la configuración: $_"
    exit 1
}
