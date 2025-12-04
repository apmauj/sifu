<#
Automatiza:
  1. Reinicia contenedor cloudflared (sifu-tunnel) usando docker-compose.tunnel.yml si existe
  2. Extrae nueva URL trycloudflare de los logs
  3. Actualiza secret VITE_PUBLIC_API_URL en GitHub (gh CLI)
  4. Opcional: dispara redeploy frontend

Uso:
  ./docker_update_tunnel_secret.ps1 -Repo apmauj/sifu -TriggerDeploy

Requisitos:
  - gh autenticado
  - docker compose
  - servicio 'tunnel' definido (docker-compose.tunnel.yml)
#>
param(
  [string]$Repo = 'apmauj/sifu',
  [int]$TimeoutSeconds = 90,
  [int]$RetryCount = 3,
  [int]$RetryDelaySeconds = 5,
  [double]$BackoffFactor = 2,
  [int]$MaxRetryDelaySeconds = 40,
  [switch]$JsonLogs,
  [switch]$TriggerDeploy,
  [switch]$SkipIfUnchanged
)

function Info($m){ if($JsonLogs){ Write-JsonLog -Level 'INFO' -Message $m } else { Write-Host "[INFO] $m" -ForegroundColor Cyan } }
function Err($m){ if($JsonLogs){ Write-JsonLog -Level 'ERROR' -Message $m } else { Write-Host "[ERROR] $m" -ForegroundColor Red } }
function Write-JsonLog {
  param(
    [string]$Level,
    [string]$Message,
    [string]$Event,
    [int]$Attempt,
    [string]$Url
  )
  $obj = [ordered]@{ ts = (Get-Date).ToString('o'); level = $Level; message = $Message }
  if($Event){ $obj.event = $Event }
  if($Attempt){ $obj.attempt = $Attempt }
  if($Url){ $obj.url = $Url }
  $obj | ConvertTo-Json -Compress | Write-Host
}

function Ensure-BackendRunning {
  param(
    [string]$ComposeFile = 'config/docker/docker-compose.tunnel.yml',
    [string]$BackendService = 'sifu-backend'
  )

  $containerId = docker ps -a --filter "name=^/$BackendService$" --format '{{.ID}}'

  if([string]::IsNullOrWhiteSpace($containerId)){
    Info "Contenedor $BackendService no existe. Creándolo mediante docker compose..."
    docker compose -f $ComposeFile up -d $BackendService | Out-Null
    if($LASTEXITCODE -ne 0){ Err "No se pudo crear $BackendService vía docker compose"; exit 1 }
    return
  }

  $status = docker inspect -f '{{.State.Status}}' $BackendService 2>$null
  if($LASTEXITCODE -ne 0){ Err "No se pudo inspeccionar $BackendService"; exit 1 }

  if($status -ne 'running'){
    Info "Backend $BackendService está en estado '$status'. Intentando iniciarlo..."
    docker start $BackendService | Out-Null
    if($LASTEXITCODE -ne 0){ Err "No se pudo iniciar $BackendService"; exit 1 }
  }
}

if(-not (Get-Command gh -ErrorAction SilentlyContinue)){ Err 'gh CLI no encontrado'; exit 1 }

# Verificar autenticación gh antes de continuar (para evitar fallo tardío)
gh auth status 1>$null 2>$null
if($LASTEXITCODE -ne 0){
  Err 'gh no está autenticado. Ejecuta: gh auth login'
  Write-Host "Pasos sugeridos:" -ForegroundColor Yellow
  Write-Host "  1) gh auth login" -ForegroundColor DarkYellow
  Write-Host "     - GitHub.com -> HTTPS -> Y (git) -> Login via browser" -ForegroundColor DarkYellow
  Write-Host "  2) Scope mínimo PAT (si usas token manual): repo, workflow" -ForegroundColor DarkYellow
  Write-Host "  3) Reintenta: ./docker_update_tunnel_secret.ps1 -TriggerDeploy" -ForegroundColor DarkYellow
  Write-Host "Alternativa: exporta GH_TOKEN (PAT con scopes repo, workflow) y reintenta" -ForegroundColor DarkYellow
  exit 1
}

# 1. Intentar obtener URL con reintentos (problemas intermitentes Cloudflare Quick Tunnel)
if(-not (Test-Path './config/docker/docker-compose.tunnel.yml')){ Err 'config/docker/docker-compose.tunnel.yml no encontrado'; exit 1 }

$regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
$url = $null

for($attempt=1; $attempt -le $RetryCount -and -not $url; $attempt++){
  if($attempt -gt 1){ Info "Reintento $attempt/$RetryCount (reiniciando contenedor túnel)" }
  Info 'Levantando túnel con config/docker/docker-compose.tunnel.yml'
  $existingTunnel = docker ps -aq --filter "name=^/sifu-tunnel$"
  if($existingTunnel){
    Info 'Deteniendo túnel previo para evitar conflictos'
    docker rm -f sifu-tunnel | Out-Null
  }
  docker compose -f config/docker/docker-compose.tunnel.yml up -d --no-deps --force-recreate --remove-orphans tunnel | Out-Null
  if($LASTEXITCODE -ne 0){
    Err 'docker compose falló al recrear el servicio tunnel. Reintentando...'
    continue
  }
  $start = Get-Date
  while((Get-Date)-$start -lt [TimeSpan]::FromSeconds($TimeoutSeconds)){
    $logs = docker logs --tail 160 sifu-tunnel 2>&1
    if($logs -match 'Error unmarshaling QuickTunnel response'){
      Err 'Cloudflare devolvió respuesta inválida (HTML). Se reintentará.'
      break
    }
    if($logs -match 'cf-error-code">(\d+)<'){ $cfCode=$Matches[1]; Err "Código Cloudflare detectado: $cfCode" }
    $m = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -First 1
    if($m){
      $url = $m.Matches[0].Value
      if($JsonLogs){ Write-JsonLog -Level 'INFO' -Message 'URL detectada' -Event 'tunnel_url_found' -Attempt $attempt -Url $url }
      break
    }
    Start-Sleep 2
  }
  if(-not $url -and $attempt -lt $RetryCount){
    # Exponential backoff con cap
    $delay = [Math]::Min($RetryDelaySeconds * [Math]::Pow($BackoffFactor, ($attempt-1)), $MaxRetryDelaySeconds)
    Info "Esperando $([int]$delay)s antes del próximo intento"
    Start-Sleep -Seconds ([int]$delay)
  }
}

if(-not $url){
  Err 'No se obtuvo URL del túnel tras reintentos.'
  docker logs --tail 200 sifu-tunnel | Out-String | Write-Host
  Write-Host 'Sugerencias:' -ForegroundColor Yellow
  Write-Host '  - Esperar 1-2 minutos y reintentar (rate limit temporal o error 1101)' -ForegroundColor DarkYellow
  Write-Host '  - Probar script alternativo: scripts/deploy/local_run_tunnel_backend.ps1 -TunnelProvider ngrok' -ForegroundColor DarkYellow
  Write-Host '  - Considerar un túnel nombrado con cuenta Cloudflare para mayor estabilidad' -ForegroundColor DarkYellow
  exit 1
}
Info "URL túnel: $url"

Ensure-BackendRunning

# El workflow CI/CD normaliza y agrega /api automáticamente, así que el secret es solo la URL base
$apiUrl = "$url"
$stateFile = Join-Path $PSScriptRoot '..' '..' '.tunnel_last_url.txt'
try { $prev = (Get-Content $stateFile -ErrorAction SilentlyContinue).Trim() } catch { $prev = $null }

if($SkipIfUnchanged -and $prev -and $prev -eq $apiUrl){
  if($TriggerDeploy){
    Info "URL sin cambios ($apiUrl). Saltando actualización de secret pero igualmente disparando redeploy (porque -TriggerDeploy)."
    $skipSecretUpdate = $true
  } else {
    Info "URL sin cambios ($apiUrl). Nada que hacer (no se solicitó redeploy)."
    exit 0
  }
}

if(-not $skipSecretUpdate){
  Info "Actualizando secret VITE_PUBLIC_API_URL => $apiUrl"
  Write-Output $apiUrl | gh secret set VITE_PUBLIC_API_URL -R $Repo | Out-Null
  if($LASTEXITCODE -ne 0){ Err 'Fallo actualizando secret'; exit 1 }
  Info 'Secret actualizado.'
  try { $apiUrl | Out-File -FilePath $stateFile -Encoding UTF8 -Force } catch { Write-Warning "No se pudo guardar state file: $_" }
} else {
  Info 'Saltando actualización de secret (sin cambios)'
}

if($TriggerDeploy){
  Info 'Disparando workflow unificado ci-cd (force_frontend_deploy=true)'
  gh workflow run .github/workflows/ci-cd.yml -R $Repo -f force_frontend_deploy=true | Out-Null
  if($LASTEXITCODE -ne 0){ Err 'Fallo disparando workflow ci-cd.yml' } else { Info 'Redeploy solicitado (CI/CD).' }
}

Write-Host "Listo. Nueva URL: $apiUrl" -ForegroundColor Green
