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
  [switch]$TriggerDeploy,
  [switch]$SkipIfUnchanged
)

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Err($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }

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

# 1. Levantar/forzar recreación del túnel
if(Test-Path './docker-compose.tunnel.yml'){
  Info 'Levantando túnel con docker-compose.tunnel.yml'
  docker compose -f docker-compose.tunnel.yml up -d --force-recreate --remove-orphans tunnel | Out-Null
} else {
  Err 'docker-compose.tunnel.yml no encontrado'; exit 1
}

# 2. Esperar URL
$regex = 'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
$start = Get-Date
$url = $null
while((Get-Date)-$start -lt [TimeSpan]::FromSeconds($TimeoutSeconds)){
  $logs = docker logs --tail 80 sifu-tunnel 2>&1
  $m = Select-String -InputObject $logs -Pattern $regex -AllMatches | Select-Object -First 1
  if($m){ $url = $m.Matches[0].Value; break }
  Start-Sleep 2
}
if(-not $url){ Err 'No se obtuvo URL del túnel'; docker logs --tail 120 sifu-tunnel; exit 1 }
Info "URL túnel: $url"

$apiUrl = "$url/api"
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
