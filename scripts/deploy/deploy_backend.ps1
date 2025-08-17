param(
  [switch]$BuildImage,
  [string]$Branch="master",
  [switch]$WaitWorkflows,
  [switch]$RedeployFrontend
)
$ErrorActionPreference="Stop"

function WaitWF {
  param(
    [string]$WorkflowName,
    [string]$RunId
  )
  if (-not $WaitWorkflows) { return }

  Write-Host "[WAIT] Esperando workflow '$WorkflowName'..." -ForegroundColor DarkCyan

  # Si no tenemos RunId, intentar detectarlo (similar a deploy_frontend)
  if (-not $RunId) {
    Start-Sleep 4
    $attempt = 0
    do {
      $attempt++
      $json = gh run list --workflow "$WorkflowName" --limit 1 --json databaseId,status,conclusion,createdAt 2>$null
      if ($json) {
        $item = ($json | ConvertFrom-Json)
        if ($item) { $RunId = $item[0].databaseId }
      }
      if (-not $RunId) {
        Write-Host "[WAIT] Aún sin run id ($attempt)" -ForegroundColor DarkGray
        Start-Sleep 3
      }
      if ($attempt -gt 15 -and -not $RunId) { throw "No se pudo detectar run para '$WorkflowName'" }
    } while (-not $RunId)
    Write-Host "[INFO] Run detectado id=$RunId" -ForegroundColor DarkCyan
  }

  # Loop de seguimiento
  while ($true) {
    $viewJson = gh run view $RunId --json status,conclusion,url 2>$null
    if (-not $viewJson) {
      Write-Host "[WARN] gh run view vacío, reintentando..." -ForegroundColor Yellow
      Start-Sleep 5
      continue
    }
    $view = $viewJson | ConvertFrom-Json
    Write-Host "[WAIT] status=$($view.status) conclusion=$($view.conclusion)" -ForegroundColor DarkGray
    if ($view.status -eq 'completed') {
      if ($view.conclusion -ne 'success') { throw "Workflow '$WorkflowName' falló: $($view.conclusion) ($($view.url))" }
      Write-Host "[OK] Workflow '$WorkflowName' success." -ForegroundColor Green
      break
    }
    Start-Sleep 6
  }
}

if ($BuildImage) {
  $dispatchOut = gh workflow run "Publish Backend Image" -r $Branch 2>$null
  $runId = $null
  if ($dispatchOut -match 'runs/(\d+)') { $runId = $Matches[1] }
  WaitWF -WorkflowName "Publish Backend Image" -RunId $runId
}
docker pull apmauj/sifu-backend:latest | Out-Null
docker compose up -d --force-recreate --no-deps backend
try { Write-Host ("Health: "+ (curl.exe -s "http://localhost:8000/api/health")) } catch {}
$brou = curl.exe -s "http://localhost:8000/api/brou/current?force_refresh=true&full=true"
try {
  $len=((($brou|ConvertFrom-Json).data).Count)
  Write-Host "BROU items: $len"
} catch {
  Write-Warning "Respuesta BROU no JSON"
}
docker logs -n 40 sifu-backend | Select-String "BROU Cache" | Select-Object -First 2
if($RedeployFrontend){
  & "$PSScriptRoot\deploy_frontend.ps1" -Branch $Branch -Wait:$WaitWorkflows
}
