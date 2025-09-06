$ErrorActionPreference="Stop"
Write-Host "=== Menu Deploy ===" -ForegroundColor Cyan
Write-Host "1) Frontend (deploy Pages con force_frontend_deploy=true)"
Write-Host "2) Backend (pull) + Frontend (redeploy)"
Write-Host "3) Backend (build imagen CI/CD) + Frontend"
Write-Host "4) Refresh Exchange (INE histórico)"
Write-Host "5) Frontend sólo (sin esperar)"
Write-Host "6) Salir"
$choice = Read-Host "Opción"
switch ($choice) {
  "1" { & "$PSScriptRoot\deploy_frontend.ps1" -Wait }
  "2" { & "$PSScriptRoot\deploy_backend.ps1" -RedeployFrontend -WaitWorkflows }
  "3" { & "$PSScriptRoot\deploy_backend.ps1" -BuildImage -RedeployFrontend -WaitWorkflows }
  "4" {
        # Refresco histórico INE con robustez (async + fallback sync) y verificación de backend
        $base = "http://localhost:8000"
        function Get-Json($method, $url) {
          try { return Invoke-RestMethod -Method $method -Uri $url -TimeoutSec 30 -ErrorAction Stop } catch { return $null }
        }
        # Comprobar salud del backend
        $health = Get-Json -method Get -url ("$base/api/health")
        if (-not $health) {
          Write-Host "Backend no responde en $base. Intentando levantar contenedor..." -ForegroundColor Yellow
          try {
            & "$PSScriptRoot\deploy_backend.ps1" -StartupProbe Exchange
          } catch {
            Write-Host "No se pudo levantar backend automáticamente: $_" -ForegroundColor Red
            break
          }
          # Re-verificar health con espera breve
          $ok=$false
          for($i=0;$i -lt 20;$i++){
            Start-Sleep -Seconds 3
            $health = Get-Json -method Get -url ("$base/api/health")
            if($health){ $ok=$true; break }
          }
          if(-not $ok){ Write-Host "Backend aún no responde en $base." -ForegroundColor Red; break }
        }

        # Intentar job asíncrono
        $job = Get-Json -method Post -url ("$base/api/exchange-rate/refresh-async")
        if ($null -eq $job -or -not $job.job_id) {
          Write-Host "No se pudo iniciar job asíncrono; probando modo sincrónico..." -ForegroundColor Yellow
          $sync = Get-Json -method Post -url ("$base/api/exchange-rate/refresh")
          if ($sync -and $sync.success) {
            Write-Host "OK (sync):" $sync.message -ForegroundColor Green
            if ($sync.data) {
              $total=$sync.data.total_records
              $min=$sync.data.date_range.min_date
              $max=$sync.data.date_range.max_date
              Write-Host "Registros procesados:" $total "| Rango:" $min "a" $max
            }
            $info = Get-Json -method Get -url ("$base/api/exchange-rate/info")
            if ($info) { Write-Host "Último día disponible ahora:" $info.date_range.max_date -ForegroundColor Cyan }
            break
          } else {
            Write-Host "Fallo en modo sincrónico. Ver logs del backend." -ForegroundColor Red
            break
          }
        }

        Write-Host "Job iniciado:" $job.job_id
        $jobId=$job.job_id
        $timeoutSec = 900  # 15 minutos
        $poll = 0
        $spinner = @('|','/','-','\\')
        while ($poll -lt $timeoutSec) {
          $status = Get-Json -method Get -url ("$base/api/exchange-rate/refresh-status/$jobId")
          if ($status -and ($status.status -in @('success','error'))) { break }
          $ch = $spinner[$poll % $spinner.Count]
          # Usar `r (carriage return) correcto en PowerShell para sobrescribir la misma línea
          Write-Host -NoNewline "`rEsperando ($ch) estado=$($status.status) ..."
          Start-Sleep -Seconds 3
          $poll += 3
        }
        Write-Host ""  # salto de línea
        if (-not $status) { Write-Host "Sin respuesta del job" -ForegroundColor Yellow; break }
        if ($status.status -eq 'success') {
          Write-Host "OK: " $status.message -ForegroundColor Green
          if ($status.result) {
            $total=$status.result.total_records
            $max=$status.result.date_range.max_date
            $min=$status.result.date_range.min_date
            Write-Host "Registros procesados:" $total "| Rango:" $min "a" $max
          }
          $info = Get-Json -method Get -url ("$base/api/exchange-rate/info")
          if ($info) { Write-Host "Último día disponible ahora:" $info.date_range.max_date -ForegroundColor Cyan }
        } else {
          Write-Host "FALLO: " $status.message -ForegroundColor Red
        }
      }
  "5" { & "$PSScriptRoot\deploy_frontend.ps1" }
  default { Write-Host "Salir" }
}
