<#
.SYNOPSIS
	Levanta backend+túnel con Docker y opcionalmente sincroniza la URL dinámica con GitHub.

.DESCRIPTION
	Flujo recomendado para "revivir" la app después de reiniciar la PC:
	1) Levanta backend y túnel con docker compose
	2) Espera a que el túnel publique una URL trycloudflare
	3) (Opcional) Actualiza secret VITE_PUBLIC_API_URL
	4) (Opcional) Dispara CI/CD para redeploy frontend

.EXAMPLE
	./run_tunnel_backend.ps1

.EXAMPLE
	./run_tunnel_backend.ps1 -SyncFrontend

.EXAMPLE
	./run_tunnel_backend.ps1 -SyncFrontend -TriggerDeploy
#>

param(
	[string]$ComposeFile = 'config/docker/docker-compose.tunnel.yml',
	[switch]$SyncFrontend,
	[switch]$TriggerDeploy,
	[switch]$SkipIfUnchanged,
	[int]$HealthWaitSeconds = 45
)

# Este script puede ejecutarse desde wrappers con ErrorActionPreference=Stop.
# Para comandos nativos (docker/gh), evitar que stderr informativo se eleve como excepción.
$ErrorActionPreference = 'Continue'
try { $global:PSNativeCommandUseErrorActionPreference = $false } catch {}

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function Err($m){ Write-Host "[ERR]  $m" -ForegroundColor Red }

function Start-ContainerIfNeeded {
	param(
		[string]$ContainerName,
		[string]$ComposeService,
		[string]$ComposeFilePath
	)

	$existing = docker ps -a --filter "name=^/$ContainerName$" --format "{{.ID}}"
	if (-not [string]::IsNullOrWhiteSpace($existing)) {
		$status = docker inspect -f "{{.State.Status}}" $ContainerName 2>$null
		if ($LASTEXITCODE -ne 0) {
			Err "No se pudo inspeccionar $ContainerName"
			exit 1
		}

		if ($status -eq 'running') {
			Info "$ContainerName ya está corriendo"
			return
		}

		Info "$ContainerName existe en estado '$status'. Iniciando..."
		docker start $ContainerName | Out-Null
		if ($LASTEXITCODE -ne 0) {
			Err "No se pudo iniciar $ContainerName"
			exit 1
		}
		return
	}

	Info "Creando servicio '$ComposeService' con docker compose"
	$upOutput = docker compose -f $ComposeFilePath up -d $ComposeService 2>&1
	$upExit = $LASTEXITCODE
	if ($upExit -ne 0) {
		$upText = ($upOutput | Out-String).Trim()
		if (-not [string]::IsNullOrWhiteSpace($upText)) {
			Err "docker compose output: $upText"
		}
		Err "Falló docker compose up para servicio '$ComposeService'"
		exit 1
	}
}

$resolvedComposeFile = $ComposeFile
if (-not [System.IO.Path]::IsPathRooted($resolvedComposeFile)) {
	$resolvedComposeFile = Join-Path $PSScriptRoot $resolvedComposeFile
}

if(-not (Test-Path $resolvedComposeFile)) {
	Err "No se encontró compose file: $resolvedComposeFile"
	exit 1
}

Info "Asegurando backend+túnel"
Start-ContainerIfNeeded -ContainerName 'sifu-backend' -ComposeService 'backend' -ComposeFilePath $resolvedComposeFile
Start-ContainerIfNeeded -ContainerName 'sifu-tunnel' -ComposeService 'tunnel' -ComposeFilePath $resolvedComposeFile

Info "Esperando health local en http://127.0.0.1:8000/api/health/simple"
$healthy = $false
$deadline = (Get-Date).AddSeconds($HealthWaitSeconds)
while((Get-Date) -lt $deadline){
	try {
		$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health/simple' -TimeoutSec 4
		if($r.status -eq 'ok' -or $r.status -eq 'healthy'){
			$healthy = $true
			break
		}
	} catch {}
	Start-Sleep -Seconds 2
}

if($healthy){ Ok 'Backend local saludable' } else { Info 'Backend aún calentando; se continúa' }

try {
	$logs = docker logs --tail 120 sifu-tunnel 2>&1
	$m = Select-String -InputObject $logs -Pattern 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' -AllMatches | Select-Object -Last 1
	if($m){
		$tunnelUrl = $m.Matches[0].Value
		Ok "Túnel detectado: $tunnelUrl"
	} else {
		Info 'No se detectó URL de túnel todavía (puede tardar unos segundos más)'
	}
} catch {
	Info 'No se pudieron leer logs del túnel en este momento'
}

if($SyncFrontend -or $TriggerDeploy){
	$syncScript = Join-Path $PSScriptRoot 'scripts/deploy/update_tunnel_secret.ps1'
	if(-not (Test-Path $syncScript)){
		Err "No se encontró script de sincronización: $syncScript"
		exit 1
	}

	Info 'Sincronizando URL dinámica con secret de GitHub'
	$params = @{
		Repo = 'apmauj/sifu'
	}
	if($TriggerDeploy){ $params.TriggerDeploy = $true }
	if($SkipIfUnchanged){ $params.SkipIfUnchanged = $true }

	& $syncScript @params
	if($LASTEXITCODE -ne 0){
		Err 'Falló la sincronización de túnel/secret'
		exit 1
	}
}

Ok 'Proceso completado'
