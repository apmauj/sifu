param(
  [string]$Branch = "master",
  [switch]$Wait,
  [switch]$SkipTunnel,
  [int]$TimeoutSec = 300,
  [int]$PollSec = 6
)

$ErrorActionPreference = "Stop"
$wfName = "Deploy Frontend to GitHub Pages"
Write-Host "[INFO] Workflow: $wfName (branch=$Branch)" -ForegroundColor Cyan

if (-not $SkipTunnel) {
  $update = Join-Path $PSScriptRoot "update_tunnel_secret.ps1"
  if (Test-Path $update) {
    Write-Host "[INFO] Actualizando túnel/secret..." -ForegroundColor DarkCyan
    & $update
  } else {
    Write-Host "[WARN] update_tunnel_secret.ps1 no encontrado" -ForegroundColor Yellow
  }
}

# Baseline de runs existentes
$baselineJson = gh run list --workflow "$wfName" --limit 30 --json databaseId,createdAt,status,conclusion 2>$null
$baseline = @()
if ($baselineJson) { $baseline = ($baselineJson | ConvertFrom-Json).databaseId }

$triggerTime = Get-Date
Write-Host "[DEBUG] Runs previos: $($baseline -join ',')" -ForegroundColor DarkGray

gh workflow run "$wfName" -r $Branch | Out-Null
Write-Host "[INFO] Workflow dispatch enviado."

if (-not $Wait) { return }

Start-Sleep 4
$start = Get-Date
$newRunId = $null
$attempt = 0

function Get-NewRun {
  param($Name,$BaselineIds,$Since)
  $json = gh run list --workflow "$Name" --limit 30 --json databaseId,createdAt,status,conclusion,headBranch 2>$null
  if (-not $json) { return $null }
  $items = $json | ConvertFrom-Json
  $candidates = $items |
    Where-Object {
      ($BaselineIds -notcontains $_.databaseId) -and
      ([DateTime]$_.createdAt -ge $Since.AddSeconds(-20))
    } |
    Sort-Object createdAt -Descending
  return ($candidates | Select-Object -First 1)
}

while (-not $newRunId) {
  $attempt++
  $runObj = Get-NewRun -Name $wfName -BaselineIds $baseline -Since $triggerTime
  if ($runObj) {
    $newRunId = $runObj.databaseId
    Write-Host "[INFO] Run nuevo detectado: id=$newRunId createdAt=$($runObj.createdAt) status=$($runObj.status)" -ForegroundColor DarkCyan
    break
  } else {
    Write-Host "[WAIT] Buscando nuevo run (intento $attempt)..." -ForegroundColor DarkGray
  }
  if ((Get-Date) - $start -gt [TimeSpan]::FromSeconds($TimeoutSec)) {
    Write-Warning "Timeout sin detectar run nuevo. Últimos runs:"
    gh run list --workflow "$wfName" --limit 5 --json databaseId,createdAt,status,conclusion | Write-Host
    throw "Timeout esperando aparición del run."
  }
  Start-Sleep 3
}

# Seguimiento
while ($true) {
  $viewJson = gh run view $newRunId --json status,conclusion,url 2>$null
  if ($viewJson) {
    $view = $viewJson | ConvertFrom-Json
    Write-Host "[WAIT] status=$($view.status) conclusion=$($view.conclusion)"
    if ($view.status -eq "completed") {
      if ($view.conclusion -ne "success") { throw "Workflow terminó: $($view.conclusion) ($($view.url))" }
      Write-Host "[OK] Frontend deploy success. $($view.url)" -ForegroundColor Green
      break
    }
  } else {
    Write-Host "[WARN] gh run view vacío, reintentando..." -ForegroundColor Yellow
  }
  if ((Get-Date) - $start -gt [TimeSpan]::FromSeconds($TimeoutSec)) {
    throw "Timeout esperando finalización."
  }
  Start-Sleep $PollSec
}
