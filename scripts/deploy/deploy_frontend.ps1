param([string]$Branch="master",[switch]$Wait)
$ErrorActionPreference="Stop"
$update="$PSScriptRoot\update_tunnel_secret.ps1"
if(Test-Path $update){ & $update } else { Write-Warning "No update_tunnel_secret.ps1" }
gh workflow run "Deploy Frontend to GitHub Pages" -r $Branch | Out-Null
if($Wait){
  Start-Sleep 4
  $run=gh run list --workflow "Deploy Frontend to GitHub Pages" --limit 1 --json databaseId,status,conclusion -q ".[0]"
  while($run.status -ne "completed"){
    Start-Sleep 6
    $run=gh run view $run.databaseId --json status,conclusion -q "{status:.status,conclusion:.conclusion}"
  }
  if($run.conclusion -ne "success"){ throw "Frontend deploy falló: $($run.conclusion)" }
  Write-Host "Frontend OK" -ForegroundColor Green
}else{
  Write-Host "Workflow lanzado (no se espera)."
}
