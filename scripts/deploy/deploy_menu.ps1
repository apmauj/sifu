$ErrorActionPreference="Stop"
Write-Host "=== Menu Deploy ===" -ForegroundColor Cyan
Write-Host "1) Frontend"
Write-Host "2) Backend (pull) + Frontend"
Write-Host "3) Backend (build) + Frontend"
Write-Host "4) Refresh BROU cache"
Write-Host "5) Salir"
$choice = Read-Host "Opción"
switch ($choice) {
  "1" { & "$PSScriptRoot\deploy_frontend.ps1" -Wait }
  "2" { & "$PSScriptRoot\deploy_backend.ps1" -RedeployFrontend -WaitWorkflows }
  "3" { & "$PSScriptRoot\deploy_backend.ps1" -BuildImage -RedeployFrontend -WaitWorkflows }
  "4" {
        $r=curl.exe -s "http://localhost:8000/api/brou/current?force_refresh=true&full=true"
        try {
          $json=$r|ConvertFrom-Json
          Write-Host "Monedas:" $json.data.Count
        } catch {
          Write-Host $r
        }
      }
  default { Write-Host "Salir" }
}
