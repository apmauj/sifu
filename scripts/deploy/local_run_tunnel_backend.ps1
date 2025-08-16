<#
 .SYNOPSIS
  Inicia el backend local, crea un túnel público (ngrok o cloudflared) y opcionalmente actualiza el secret VITE_PUBLIC_API_URL en GitHub y dispara el deploy del frontend Pages.

 .DESCRIPTION
  Automatiza el flujo "usar backend local desde frontend publicado en GitHub Pages".
  - Levanta FastAPI (uvicorn) en 0.0.0.0:8000 (si -SkipBackend no está presente)
  - Abre túnel con ngrok (API local) o cloudflared (parseando log)
  - Extrae la URL pública segura (https)
  - (Opcional) Actualiza el secret VITE_PUBLIC_API_URL con gh CLI
  - (Opcional) Dispara workflow deploy-frontend.yml

 .PARAMETER TunnelProvider
  Proveedor del túnel: ngrok | cloudflared (por defecto ngrok)

 .PARAMETER AllowOrigins
  Lista separada por comas de orígenes para CORS (se exporta como ALLOW_ORIGINS al backend)

 .PARAMETER UpdateSecret
  Si se indica, se ejecuta 'gh secret set VITE_PUBLIC_API_URL'. Requiere gh autenticado y permisos.

 .PARAMETER TriggerDeploy
  Si se indica y se actualiza el secret, dispara el workflow 'deploy-frontend.yml'.

 .PARAMETER SkipBackend
  No inicia el backend (asume que ya corre en :8000) y solo crea túnel y/o actualiza secret.

 .PARAMETER PythonVenv
  Ruta de la carpeta del entorno virtual a usar/crear (default .venv)

 .PARAMETER ExtraPipArgs
  Argumentos adicionales para pip install (por ej. --upgrade --no-cache-dir)

 .EXAMPLE
  ./run_tunnel_backend.ps1 -TunnelProvider ngrok -UpdateSecret -TriggerDeploy

 .NOTES
  Requisitos:
   - PowerShell 5+ / 7+
   - Python y pip
   - ngrok (authtoken configurado) o cloudflared en PATH
   - gh CLI si quieres actualizar secrets / disparar workflow
  Este script no se recomienda para producción.
#>
param(
  [ValidateSet('ngrok','cloudflared')]
  [string]$TunnelProvider = 'ngrok',
  [string]$AllowOrigins = 'https://apmauj.github.io',
  [switch]$UpdateSecret,
  [switch]$TriggerDeploy,
  [switch]$SkipBackend,
  [string]$PythonVenv = '.venv',
  [string]$ExtraPipArgs = ''
)

Write-Host "🔧 SIFU Tunnel Helper" -ForegroundColor Cyan
Write-Host "Proveedor: $TunnelProvider" -ForegroundColor DarkCyan

function Assert-Command($name, $installUrl) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Falta comando '$name'" -ForegroundColor Red
    if ($installUrl) { Write-Host "Instalar: $installUrl" -ForegroundColor Yellow }
    exit 1
  }
}

Assert-Command python 'https://www.python.org/downloads/'
if ($TunnelProvider -eq 'ngrok') { Assert-Command ngrok 'https://ngrok.com/download' }
if ($TunnelProvider -eq 'cloudflared') { Assert-Command cloudflared 'https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/' }

if ($UpdateSecret -or $TriggerDeploy) { Assert-Command gh 'https://cli.github.com/' }

$env:ALLOW_ORIGINS = $AllowOrigins

if (-not $SkipBackend) {
  Write-Host "🚀 Iniciando backend (FastAPI)" -ForegroundColor Green
  if (-not (Test-Path $PythonVenv)) {
    Write-Host "🧪 Creando venv $PythonVenv" -ForegroundColor DarkGray
    python -m venv $PythonVenv
  }
  & "$PythonVenv/Scripts/Activate.ps1"
  if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando dependencias" -ForegroundColor DarkGray
    pip install -r requirements.txt $ExtraPipArgs 2>$null | Out-Null
  }
  # Iniciar uvicorn en background
  $backendJob = Start-Job -ScriptBlock {
    param($allowOrigins)
    $env:ALLOW_ORIGINS = $allowOrigins
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
  } -ArgumentList $AllowOrigins
  Start-Sleep -Seconds 2
  Write-Host "⌛ Esperando health..." -NoNewline
  $healthy = $false
  for ($i=0; $i -lt 20; $i++) {
    try { $r = Invoke-RestMethod http://127.0.0.1:8000/api/health -TimeoutSec 2; if ($r.status -eq 'ok') { $healthy = $true; break } } catch {}
    Start-Sleep -Milliseconds 500
    Write-Host '.' -NoNewline
  }
  Write-Host ''
  if (-not $healthy) { Write-Host "⚠️ Backend no respondió aún, se continúa..." -ForegroundColor Yellow } else { Write-Host "✅ Backend listo" -ForegroundColor Green }
}

Write-Host "🌍 Creando túnel público ($TunnelProvider)" -ForegroundColor Green

function Get-TunnelUrl-Ngrok {
  # Iniciar ngrok si no corre ya
  $existing = Get-Process ngrok -ErrorAction SilentlyContinue
  if (-not $existing) {
    Start-Process ngrok -ArgumentList 'http 8000' -WindowStyle Hidden
    Start-Sleep -Seconds 2
  }
  $url = $null
  for ($i=0; $i -lt 20; $i++) {
    try {
      $res = Invoke-RestMethod http://127.0.0.1:4040/api/tunnels -TimeoutSec 2
      $url = ($res.tunnels | Where-Object {$_.public_url -like 'https://*'} | Select-Object -First 1).public_url
      if ($url) { break }
    } catch {}
    Start-Sleep -Milliseconds 500
  }
  return $url
}

function Get-TunnelUrl-Cloudflared {
  $logFile = Join-Path $env:TEMP "cloudflared_sifu.log"
  if (Test-Path $logFile) { Remove-Item $logFile -Force }
  Start-Process cloudflared -ArgumentList 'tunnel --url http://localhost:8000' -RedirectStandardOutput $logFile -RedirectStandardError $logFile -WindowStyle Hidden
  $url = $null
  for ($i=0; $i -lt 40; $i++) {
    if (Test-Path $logFile) {
      $content = Get-Content $logFile -Raw
      if ($content -match 'https://[a-zA-Z0-9-]+\.trycloudflare\.com') {
        $url = $Matches[0]; break
      }
    }
    Start-Sleep -Milliseconds 500
  }
  return $url
}

switch ($TunnelProvider) {
  'ngrok' { $publicUrl = Get-TunnelUrl-Ngrok }
  'cloudflared' { $publicUrl = Get-TunnelUrl-Cloudflared }
}

if (-not $publicUrl) {
  Write-Host "❌ No se pudo obtener URL pública del túnel" -ForegroundColor Red
  Write-Host "Revisa que el proveedor funcione manualmente." -ForegroundColor Yellow
  if (-not $SkipBackend -and $backendJob) { Stop-Job $backendJob | Out-Null }
  exit 1
}

Write-Host "✅ Túnel listo: $publicUrl" -ForegroundColor Green
Write-Host "🔗 Health: $publicUrl/api/health" -ForegroundColor Cyan

$fullApi = "$publicUrl/api"

if ($UpdateSecret) {
  Write-Host "🔐 Actualizando secret VITE_PUBLIC_API_URL => $fullApi" -ForegroundColor Magenta
  $secretResult = gh secret set VITE_PUBLIC_API_URL -b $fullApi 2>&1
  if ($LASTEXITCODE -eq 0) { Write-Host "✅ Secret actualizado" -ForegroundColor Green } else { Write-Host "⚠️ Falló actualizar secret: $secretResult" -ForegroundColor Yellow }
  if ($TriggerDeploy) {
    Write-Host "🚀 Disparando workflow deploy-frontend.yml" -ForegroundColor Magenta
    gh workflow run deploy-frontend.yml 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Workflow disparado" -ForegroundColor Green } else { Write-Host "⚠️ Falló disparar workflow" -ForegroundColor Yellow }
  }
}

Write-Host "📋 Copiá esto si querés exportarlo manualmente:" -ForegroundColor DarkGray
Write-Host "    VITE_PUBLIC_API_URL=$fullApi" -ForegroundColor DarkGray
Write-Host "📝 Abrí luego: https://apmauj.github.io/sifu/ (tras el redeploy)" -ForegroundColor White
Write-Host "⏹ Para detener: cierra este PowerShell y mata procesos ngrok/cloudflared si siguen activos." -ForegroundColor Yellow
