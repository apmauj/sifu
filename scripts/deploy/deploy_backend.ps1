param(
  [switch]$BuildImage,
  [string]$Branch="master",
  [switch]$WaitWorkflows,
  [switch]$RedeployFrontend,
  [switch]$SkipValidation,
  [string]$EnvFile = ".env",
  [ValidateSet('Default','Exchange','None')]
  [string]$StartupProbe='Default'
)
$ErrorActionPreference="Stop"

# Validación de seguridad antes del deploy
if (-not $SkipValidation) {
  Write-Host "[INFO] Ejecutando validaciones de seguridad..." -ForegroundColor Yellow

  # Verificar que existe el archivo .env
  if (-not (Test-Path $EnvFile)) {
    throw "Archivo $EnvFile no encontrado. Crear desde .env.template"
  }

  # Verificar que existe el secret_manager
  $secretManager = Join-Path $PSScriptRoot "..\..\secret_manager.py"
  if (-not (Test-Path $secretManager)) {
    throw "secret_manager.py no encontrado en la raíz del proyecto"
  }

  # Ejecutar validación de configuración
  Write-Host "[INFO] Validando configuración..." -ForegroundColor DarkCyan
  try {
    python $secretManager --validate
    Write-Host "[OK] Configuración validada correctamente" -ForegroundColor Green
  } catch {
    throw "Error en validación de configuración: $_"
  }

  # Verificar dependencias de seguridad
  Write-Host "[INFO] Verificando dependencias de seguridad..." -ForegroundColor DarkCyan
  
  # Función para leer requirements recursivamente
  function Get-RequirementsRecursive {
    param([string]$FileName)
    $requirements = @()
    try {
      $lines = Get-Content $FileName -ErrorAction SilentlyContinue
      foreach ($line in $lines) {
        $line = $line.Trim()
        if ($line -match "^-r (.+)$") {
          $refFile = $Matches[1]
          $requirements += Get-RequirementsRecursive $refFile
        } elseif ($line -and -not $line.StartsWith("#")) {
          # Extraer nombre del paquete (antes de ==, >=, etc. o [extras])
          $packageName = $line -split "[=<>!]" | Select-Object -First 1
          $packageName = $packageName -split "\[" | Select-Object -First 1
          $requirements += $packageName.Trim()
        }
      }
    } catch {
      Write-Warning "Error leyendo $FileName`: $($_.Exception.Message)"
    }
    return $requirements
  }
  
  $allRequirements = Get-RequirementsRecursive "requirements.txt"
  
  if ($allRequirements -notcontains "cryptography") {
    Write-Warning "cryptography no está en requirements - logging seguro limitado"
  }
  if ($allRequirements -notcontains "python-dotenv") {
    throw "python-dotenv es requerido para gestión de secrets"
  }
}

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
docker compose up -d --force-recreate --remove-orphans --no-deps backend
try { Write-Host ("Health: "+ (curl.exe -s "http://localhost:8000/api/health")) } catch {}

# Probas de inicio según contexto
switch ($StartupProbe) {
  'Exchange' {
    $ex = curl.exe -s "http://localhost:8000/api/exchange-rate/info"
    try {
      $info = ($ex | ConvertFrom-Json)
      $max = $info.date_range.max_date
      Write-Host "Exchange info: último día=$max"
    } catch {
      Write-Warning "Respuesta Exchange/info no JSON"
    }
  }
  'Default' {
    $brou = curl.exe -s "http://localhost:8000/api/brou/current?force_refresh=true&full=true"
    try {
      $len=((($brou|ConvertFrom-Json).data).Count)
      Write-Host "BROU items: $len"
    } catch {
      Write-Warning "Respuesta BROU no JSON"
    }
    docker logs -n 40 sifu-backend | Select-String "BROU Cache" | Select-Object -First 2
  }
  'None' { }
}
if($RedeployFrontend){
  & "$PSScriptRoot\deploy_frontend.ps1" -Branch $Branch -Wait:$WaitWorkflows
}
