param(
  [string]$TaskName = 'SIFU-Tunnel-Sync-OnStartup',
  [string]$Repo = 'apmauj/sifu',
  [int]$StartupDelayMinutes = 2,
  [switch]$UseCurrentUserLogon,
  [switch]$AllowUserLogonFallback,
  [switch]$RunNow,
  [switch]$Remove
)

$ErrorActionPreference = 'Stop'

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Err($m){ Write-Host "[ERR]  $m" -ForegroundColor Red }

function Test-IsAdmin {
  $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$isAdmin = Test-IsAdmin

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$startupScript = Join-Path $repoRoot 'scripts\deploy\startup_sync_wrapper.ps1'

if (-not (Test-Path $startupScript)) {
  Err "No se encontró script de arranque: $startupScript"
  exit 1
}

if ($Remove) {
  try {
    schtasks.exe /Delete /TN $TaskName /F | Out-Null
    Ok "Tarea eliminada: $TaskName"
    exit 0
  } catch {
    Warn "No se pudo eliminar la tarea (puede no existir): $TaskName"
    exit 0
  }
}

$delay = '0000:00'
if ($StartupDelayMinutes -gt 0) {
  $minutes = '{0:d4}' -f $StartupDelayMinutes
  $delay = "$minutes`:00"
}

$runArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$startupScript`""
$taskCommand = "powershell.exe $runArgs"

if ($UseCurrentUserLogon) {
  $currentUser = "$env:USERDOMAIN\$env:USERNAME"
  Info "Creando tarea '$TaskName' ($currentUser, ONLOGON)"
  $createOutput = schtasks.exe /Create /TN $TaskName /TR $taskCommand /SC ONLOGON /RU $currentUser /RL LIMITED /F 2>&1
} elseif ($isAdmin) {
  Info "Creando tarea '$TaskName' (SYSTEM, ONSTART, delay=$delay)"
  $createOutput = schtasks.exe /Create /TN $TaskName /TR $taskCommand /SC ONSTART /DELAY $delay /RU SYSTEM /RL HIGHEST /F 2>&1
} elseif ($AllowUserLogonFallback) {
  $currentUser = "$env:USERDOMAIN\$env:USERNAME"
  Warn "Sin privilegios de administrador. Creando fallback ONLOGON para usuario actual: $currentUser"
  $createOutput = schtasks.exe /Create /TN $TaskName /TR $taskCommand /SC ONLOGON /RU $currentUser /RL LIMITED /F 2>&1
} else {
  Err 'Este script requiere PowerShell como administrador para tarea ONSTART/SYSTEM. Reintenta como admin o usa -AllowUserLogonFallback.'
  exit 1
}
if ($LASTEXITCODE -ne 0) {
  Err "Falló creación de tarea: $createOutput"
  exit 1
}

Ok "Tarea creada correctamente: $TaskName"

$query = schtasks.exe /Query /TN $TaskName /V /FO LIST 2>&1
if ($LASTEXITCODE -eq 0) {
  $query | Select-String 'TaskName|Run As User|Schedule|Start In|Last Run Time|Last Result|Task To Run' | ForEach-Object { $_.Line }
}

if ($RunNow) {
  Info "Ejecutando tarea ahora: $TaskName"
  schtasks.exe /Run /TN $TaskName | Out-Null
  if ($LASTEXITCODE -eq 0) {
    Ok 'Tarea disparada manualmente.'
  } else {
    Warn 'No se pudo ejecutar manualmente la tarea.'
  }
}

Ok 'Listo. En próximos reinicios del host, se ejecutará sync automático de túnel y redeploy si corresponde.'
