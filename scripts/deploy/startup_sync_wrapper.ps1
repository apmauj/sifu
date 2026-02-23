param(
  [string]$LogFile = 'logs/startup_sync.log',
  [int]$DockerReadyTimeoutSeconds = 360,
  [int]$DockerPollSeconds = 6
)

$ErrorActionPreference = 'Stop'

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Err($m){ Write-Host "[ERR]  $m" -ForegroundColor Red }

function Wait-DockerReady {
  param(
    [int]$TimeoutSeconds,
    [int]$PollSeconds,
    [string]$LogPath
  )

  $start = Get-Date
  $deadline = $start.AddSeconds($TimeoutSeconds)
  $dockerDesktopExe = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
  $startedDesktop = $false

  while ((Get-Date) -lt $deadline) {
    try {
      docker version 1>$null 2>$null
      if ($LASTEXITCODE -eq 0) {
        "[OK] Docker engine disponible" | Out-File -FilePath $LogPath -Encoding UTF8 -Append
        return $true
      }
    } catch {}

    if (-not $startedDesktop -and -not (Get-Process -Name 'Docker Desktop' -ErrorAction SilentlyContinue)) {
      if (Test-Path $dockerDesktopExe) {
        try {
          Start-Process -FilePath $dockerDesktopExe | Out-Null
          $startedDesktop = $true
          "[INFO] Docker Desktop no estaba corriendo; se intentó iniciar automáticamente" | Out-File -FilePath $LogPath -Encoding UTF8 -Append
        } catch {
          "[WARN] No se pudo iniciar Docker Desktop automáticamente: $($_.Exception.Message)" | Out-File -FilePath $LogPath -Encoding UTF8 -Append
        }
      }
    }

    Start-Sleep -Seconds $PollSeconds
  }

  "[ERR] Docker engine no estuvo disponible en ${TimeoutSeconds}s" | Out-File -FilePath $LogPath -Encoding UTF8 -Append
  return $false
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runScript = Join-Path $repoRoot 'run_tunnel_backend.ps1'
$logPath = if([System.IO.Path]::IsPathRooted($LogFile)) { $LogFile } else { Join-Path $repoRoot $LogFile }
$logDir = Split-Path -Parent $logPath
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

"=== Startup Sync Wrapper: $(Get-Date -Format o) ===" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"[INFO] User=$([Environment]::UserName) Domain=$([Environment]::UserDomainName)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"[INFO] RepoRoot=$repoRoot" | Out-File -FilePath $logPath -Encoding UTF8 -Append
"[INFO] RunScript=$runScript" | Out-File -FilePath $logPath -Encoding UTF8 -Append

try {
  $dockerCmd = Get-Command docker -ErrorAction Stop
  "[INFO] DockerCommand=$($dockerCmd.Source)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
} catch {
  "[WARN] Docker command no disponible en este contexto: $($_.Exception.Message)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
}

try {
  $ghCmd = Get-Command gh -ErrorAction Stop
  "[INFO] GhCommand=$($ghCmd.Source)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
} catch {
  "[WARN] gh command no disponible en este contexto: $($_.Exception.Message)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
}

if (-not (Test-Path $runScript)) {
  Err "No se encontró script: $runScript"
  "[ERR] No se encontró script principal" | Out-File -FilePath $logPath -Encoding UTF8 -Append
  exit 1
}

"[INFO] Esperando Docker engine (timeout=${DockerReadyTimeoutSeconds}s, poll=${DockerPollSeconds}s)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
if (-not (Wait-DockerReady -TimeoutSeconds $DockerReadyTimeoutSeconds -PollSeconds $DockerPollSeconds -LogPath $logPath)) {
  Err 'Docker no estuvo listo a tiempo; se aborta sync de startup.'
  exit 1
}

Push-Location $repoRoot
try {
  Info 'Intento 1: sync completa (secret + redeploy)'
  & $runScript -SyncFrontend -TriggerDeploy -SkipIfUnchanged *>&1 | Tee-Object -FilePath $logPath -Append | Out-Host
  if ($LASTEXITCODE -eq 0) {
    Info 'Sync completa OK'
    "[OK] Sync completa OK" | Out-File -FilePath $logPath -Encoding UTF8 -Append
    exit 0
  }

  Warn "Sync completa falló (exit=$LASTEXITCODE). Intentando fallback local..."
  "[WARN] Sync completa falló (exit=$LASTEXITCODE). Fallback local." | Out-File -FilePath $logPath -Encoding UTF8 -Append

  & $runScript *>&1 | Tee-Object -FilePath $logPath -Append | Out-Host
  if ($LASTEXITCODE -eq 0) {
    Info 'Fallback local OK (backend+túnel arriba).'
    "[OK] Fallback local OK" | Out-File -FilePath $logPath -Encoding UTF8 -Append
    exit 0
  }

  Err "Fallback local también falló (exit=$LASTEXITCODE)"
  "[ERR] Fallback local también falló (exit=$LASTEXITCODE)" | Out-File -FilePath $logPath -Encoding UTF8 -Append
  exit $LASTEXITCODE
}
catch {
  $msg = "[ERR] Excepción en wrapper: $($_.Exception.Message)"
  $trace = $_.ScriptStackTrace
  $msg | Out-File -FilePath $logPath -Encoding UTF8 -Append
  if ($trace) {
    "[ERR] Stack: $trace" | Out-File -FilePath $logPath -Encoding UTF8 -Append
  }
  exit 1
}
finally {
  Pop-Location
}
