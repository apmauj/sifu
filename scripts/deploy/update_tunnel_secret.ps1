<#
Automatiza:
  1. Reinicia contenedor cloudflared (sifu-tunnel) usando docker-compose.tunnel.yml si existe
  2. Extrae nueva URL trycloudflare de los logs
  3. Actualiza secret VITE_PUBLIC_API_URL en GitHub (gh CLI)
  4. Opcional: dispara redeploy frontend

Uso:
  ./scripts/deploy/docker_update_tunnel_secret.ps1 -Repo apmauj/sifu -TriggerDeploy

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
  [switch]$SkipIfUnchanged,
  [switch]$ForceDeployOnUnchanged
)

$ErrorActionPreference = 'Continue'
try { $global:PSNativeCommandUseErrorActionPreference = $false } catch {}

$rateLimitFile = Join-Path (Join-Path (Join-Path $PSScriptRoot '..') '..') '.tunnel_rate_limit_until.txt'

function Read-RateLimitUntil {
  if(-not (Test-Path $rateLimitFile)){ return $null }
  try {
    $raw = Get-Content $rateLimitFile -ErrorAction SilentlyContinue | Select-Object -First 1
    if([string]::IsNullOrWhiteSpace($raw)){ return $null }
    return [DateTime]::Parse($raw)
  } catch { return $null }
}

function Write-RateLimitUntil($dt){
  try { $dt.ToString('o') | Out-File -FilePath $rateLimitFile -Encoding UTF8 -Force } catch {}
}

function Info($m){ if($JsonLogs){ Write-JsonLog -Level 'INFO' -Message $m } else { Write-Host "[INFO] $m" -ForegroundColor Cyan } }
function Err($m){ if($JsonLogs){ Write-JsonLog -Level 'ERROR' -Message $m } else { Write-Host "[ERROR] $m" -ForegroundColor Red } }
function Write-JsonLog {
  param(
    [string]$Level,
    [string]$Message,
    [string]$EventName,
    [int]$Attempt,
    [string]$Url
  )
  $obj = [ordered]@{ ts = (Get-Date).ToString('o'); level = $Level; message = $Message }
  if($EventName){ $obj.event = $EventName }
  if($Attempt){ $obj.attempt = $Attempt }
  if($Url){ $obj.url = $Url }
  $obj | ConvertTo-Json -Compress | Write-Host
}

function Test-BackendHealth {
  param(
    [string]$BaseUrl,
    [int[]]$Delays = @(8,15,30,45,60,90)
  )

  $attempts = $Delays.Count
  $endpoints = @(
    "$BaseUrl/api/health/simple",
    "$BaseUrl/api/health"
  )

  for($i = 0; $i -lt $attempts; $i++){
    $attemptNum = $i + 1

    foreach($endpoint in $endpoints){
      Info "Verificando health ($attemptNum/$attempts): $endpoint"
      try {
        $response = Invoke-WebRequest -Method Get -Uri $endpoint -TimeoutSec 12 -UseBasicParsing
        $body = $response.Content
        $status = $null

        try {
          $parsed = $body | ConvertFrom-Json -ErrorAction Stop
          if($parsed -and $parsed.PSObject.Properties.Name -contains 'status'){
            $status = "$($parsed.status)".ToLowerInvariant()
          }
        } catch {
          # Algunos edge responses no son JSON en los primeros segundos del túnel.
        }

        if($response.StatusCode -eq 200 -and ($status -eq 'ok' -or $status -eq 'healthy')){
          Info "Health OK en intento $attemptNum"
          return $true
        }

        if($response.StatusCode -eq 200 -and [string]::IsNullOrWhiteSpace($status) -and $endpoint.EndsWith('/api/health')){
          Info "Health respondió 200 en endpoint alternativo; se considera OK"
          return $true
        }

        if($body -match 'FAIL|cf-error-code|cloudflare'){
          Err "Health devolvió respuesta transitoria de túnel/edge. Reintentando..."
        } else {
          Err "Health devolvió estado inesperado: $status"
        }
      } catch {
        $errText = $_.Exception.Message
        if($errText -match 'Host desconocido|No such host is known|NameResolutionFailure|Name or service not known'){
          Err "DNS del túnel aún no propagó. Reintentando..."
        } else {
          Err "Health request falló (intento $attemptNum): $_"
        }
      }
    }

    if($attemptNum -lt $attempts){
      $sleep = $Delays[$i]
      Info "Reintentando health en $sleep s"
      Start-Sleep -Seconds $sleep
    }
  }
  return $false
}

function Start-BackendIfNeeded {
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

# Respetar ventana de cooldown si previamente hubo rate limit (429)
$until = Read-RateLimitUntil
if($until -and $until -gt (Get-Date)){
  $waitMinutes = [int]([Math]::Ceiling(($until - (Get-Date)).TotalMinutes))
  Err "Se detectó rate limit previo. Espera ~${waitMinutes}m antes de reintentar."
  exit 1
}

# Verificar autenticación gh antes de continuar (para evitar fallo tardío)
gh auth status 1>$null 2>$null
if($LASTEXITCODE -ne 0){
  Err 'gh no está autenticado. Ejecuta: gh auth login'
  Write-Host "Pasos sugeridos:" -ForegroundColor Yellow
  Write-Host "  1) gh auth login" -ForegroundColor DarkYellow
  Write-Host "     - GitHub.com -> HTTPS -> Y (git) -> Login via browser" -ForegroundColor DarkYellow
  Write-Host "  2) Scope mínimo PAT (si usas token manual): repo, workflow" -ForegroundColor DarkYellow
  Write-Host "  3) Reintenta: ./scripts/deploy/docker_update_tunnel_secret.ps1 -TriggerDeploy" -ForegroundColor DarkYellow
  Write-Host "Alternativa: exporta GH_TOKEN (PAT con scopes repo, workflow) y reintenta" -ForegroundColor DarkYellow
  exit 1
}

# 1. Intentar obtener URL con reintentos (problemas intermitentes Cloudflare Quick Tunnel)
if(-not (Test-Path './config/docker/docker-compose.tunnel.yml')){ Err 'config/docker/docker-compose.tunnel.yml no encontrado'; exit 1 }

Start-BackendIfNeeded

$regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
$url = $null
$rateLimited = $false

for($attempt=1; $attempt -le $RetryCount -and -not $url; $attempt++){
  if($attempt -gt 1){ Info "Reintento $attempt/$RetryCount (reiniciando contenedor túnel)" }
  Info 'Levantando túnel con config/docker/docker-compose.tunnel.yml'
  $existingTunnel = docker ps -aq --filter "name=^/sifu-tunnel$"
  if($existingTunnel){
    Info 'Deteniendo túnel previo para evitar conflictos'
    docker rm -f sifu-tunnel | Out-Null
  }
  $composeOut = docker compose -f config/docker/docker-compose.tunnel.yml up -d --no-deps --force-recreate --remove-orphans tunnel 2>&1
  $composeExit = $LASTEXITCODE
  if($composeExit -ne 0){
    $composeText = ($composeOut | Out-String).Trim()
    if(-not [string]::IsNullOrWhiteSpace($composeText)){ Err "docker compose output: $composeText" }
    Err 'docker compose falló al recrear el servicio tunnel. Reintentando...'
    continue
  }
  $start = Get-Date
  while((Get-Date)-$start -lt [TimeSpan]::FromSeconds($TimeoutSeconds)){
    $logs = docker logs --tail 160 sifu-tunnel 2>&1
    if($logs -match 'Error unmarshaling QuickTunnel response'){ Err 'Cloudflare devolvió respuesta inválida (HTML). Se reintentará.'; break }
    if($logs -match 'status_code="429"' -or $logs -match 'Too Many Requests' -or $logs -match 'cf-error-code">1015<'){
      Err 'Cloudflare rate limit (429).'
      $rateLimited = $true
      break
    }
    if($logs -match 'cf-error-code">(\d+)<'){ $cfCode=$Matches[1]; Err "Código Cloudflare detectado: $cfCode" }
    $m = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -Last 1
    if($m){
      $candidateUrl = $m.Matches[0].Value
      Info "URL candidata: $candidateUrl"

      $candidateHealthOk = Test-BackendHealth -BaseUrl $candidateUrl -Delays @(8,15,30,45,60,90)
      if($candidateHealthOk){
        $url = $candidateUrl
        if($JsonLogs){ Write-JsonLog -Level 'INFO' -Message 'URL validada' -EventName 'tunnel_url_valid' -Attempt $attempt -Url $url }
      } else {
        Err 'La URL candidata no pasó health tras ventana completa de espera. Se recreará túnel.'
      }
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
  if($rateLimited){
    $cooldown = (Get-Date).AddMinutes(60)
    Write-RateLimitUntil $cooldown
    Err 'No se obtuvo URL por rate limit (429). Se establece cooldown de 60 minutos antes de nuevos intentos.'
  } else {
    Err 'No se obtuvo URL del túnel tras reintentos.'
  }
  docker logs --tail 200 sifu-tunnel | Out-String | Write-Host
  Write-Host 'Sugerencias:' -ForegroundColor Yellow
  Write-Host '  - Esperar 10 minutos y reintentar si fue rate limit' -ForegroundColor DarkYellow
  Write-Host '  - Probar script alternativo: scripts/deploy/local_run_tunnel_backend.ps1 -TunnelProvider ngrok' -ForegroundColor DarkYellow
  Write-Host '  - Considerar un túnel nombrado con cuenta Cloudflare para mayor estabilidad' -ForegroundColor DarkYellow
  exit 1
}
Info "URL túnel: $url"

# El workflow CI/CD normaliza y agrega /api automáticamente, así que el secret es solo la URL base
$apiUrl = "$url"
$stateFile = Join-Path (Join-Path (Join-Path $PSScriptRoot '..') '..') '.tunnel_last_url.txt'
try { $prev = (Get-Content $stateFile -ErrorAction SilentlyContinue).Trim() } catch { $prev = $null }

if($SkipIfUnchanged -and $prev -and $prev -eq $apiUrl){
  if($TriggerDeploy -and $ForceDeployOnUnchanged){
    Info "URL sin cambios ($apiUrl). Saltando actualización de secret y forzando redeploy por -ForceDeployOnUnchanged."
    $skipSecretUpdate = $true
  } else {
    if($TriggerDeploy){
      Info "URL sin cambios ($apiUrl). No se dispara redeploy para evitar loops (usar -ForceDeployOnUnchanged para override)."
    } else {
      Info "URL sin cambios ($apiUrl). Nada que hacer (no se solicitó redeploy)."
    }
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
