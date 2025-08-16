param(
  [switch]$BuildImage,
  [string]$Branch="master",
  [switch]$WaitWorkflows,
  [switch]$RedeployFrontend
)
$ErrorActionPreference="Stop"
function WaitWF($n){
  if(-not $WaitWorkflows){return}
  Start-Sleep 4
  $r=gh run list --workflow "$n" --limit 1 --json databaseId,status,conclusion -q ".[0]"
  while($r.status -ne "completed"){
    Start-Sleep 8
    $r=gh run view $r.databaseId --json status,conclusion -q "{status:.status,conclusion:.conclusion}"
  }
  if($r.conclusion -ne "success"){ throw "$n falló: $($r.conclusion)" }
}
if($BuildImage){
  gh workflow run "Publish Backend Image" -r $Branch | Out-Null
  WaitWF "Publish Backend Image"
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
docker logs -n 40 sifu-backend | Select-String "BROU Cache" | Select -First 2
if($RedeployFrontend){
  & "$PSScriptRoot\deploy_frontend.ps1" -Branch $Branch -Wait:$WaitWorkflows
}
