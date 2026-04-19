param(
    [ValidateSet("warn", "fail")]
    [string]$Mode = "warn",
    [string]$ReportPath = "logs/architecture/layer_violations.json"
)

$ErrorActionPreference = "Stop"

$knownLayers = @("api", "application", "domain", "infrastructure", "utils")

$allowedImports = @{
    "api" = @("api", "application", "domain", "infrastructure", "utils")
    "application" = @("application", "domain", "infrastructure", "utils")
    "domain" = @("domain", "utils")
    "infrastructure" = @("infrastructure", "domain", "utils")
    "utils" = @("utils")
}

function Get-LayerFromPath {
    param([string]$Path)

    $normalized = $Path.Replace('\\', '/').ToLowerInvariant()

    if ($normalized -match '^src/api/') { return "api" }
    if ($normalized -match '^src/application/') { return "application" }
    if ($normalized -match '^src/domain/') { return "domain" }
    if ($normalized -match '^src/infrastructure/') { return "infrastructure" }
    if ($normalized -match '^src/utils/') { return "utils" }

    return $null
}

function Get-ImportTargetsFromLine {
    param([string]$Line)

    $targets = New-Object System.Collections.Generic.List[string]

    if ($Line -match '^\s*from\s+src\.([A-Za-z_][\w]*)') {
        [void]$targets.Add($Matches[1].ToLowerInvariant())
    }

    if ($Line -match '^\s*import\s+src\.([A-Za-z_][\w]*)') {
        [void]$targets.Add($Matches[1].ToLowerInvariant())
    }

    return $targets | Select-Object -Unique
}

$pythonFiles = Get-ChildItem -Path "src" -Recurse -Filter "*.py" -File
$violations = New-Object System.Collections.Generic.List[object]

foreach ($file in $pythonFiles) {
    $relativePath = $file.FullName.Substring((Get-Location).Path.Length + 1).Replace('\\', '/')
    $fromLayer = Get-LayerFromPath -Path $relativePath

    if (-not $fromLayer) { continue }

    $lineNumber = 0
    foreach ($line in Get-Content -Path $file.FullName) {
        $lineNumber++
        $targets = Get-ImportTargetsFromLine -Line $line

        foreach ($targetLayer in $targets) {
            if ($knownLayers -notcontains $targetLayer) { continue }
            if ($allowedImports[$fromLayer] -contains $targetLayer) { continue }

            $violations.Add([PSCustomObject]@{
                file = $relativePath
                line = $lineNumber
                from_layer = $fromLayer
                to_layer = $targetLayer
                import_line = $line.Trim()
            }) | Out-Null
        }
    }
}

$reportDir = Split-Path -Parent $ReportPath
if (-not [string]::IsNullOrWhiteSpace($reportDir) -and -not (Test-Path $reportDir)) {
    New-Item -Path $reportDir -ItemType Directory -Force | Out-Null
}

$summaryByEdge = @()
if ($violations.Count -gt 0) {
    $summaryByEdge = $violations |
        Group-Object from_layer, to_layer |
        Sort-Object Count -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                edge = $_.Name.Replace(', ', ' -> ')
                count = $_.Count
            }
        }
}

$report = [PSCustomObject]@{
    mode = $Mode
    scanned_files = $pythonFiles.Count
    known_layers = $knownLayers
    total_violations = $violations.Count
    summary_by_edge = $summaryByEdge
    violations = $violations
}

$report | ConvertTo-Json -Depth 8 | Out-File -FilePath $ReportPath -Encoding utf8

if ($violations.Count -eq 0) {
    Write-Host "Layer import check PASS: no violations found across $($pythonFiles.Count) files."
    exit 0
}

Write-Host "Layer import check detected $($violations.Count) violation(s) across $($pythonFiles.Count) files."
Write-Host "Top layer edges with violations:"
$summaryByEdge | Select-Object -First 10 | ForEach-Object {
    Write-Host " - $($_.edge): $($_.count)"
}
Write-Host "Report written to $ReportPath"

if ($Mode -eq "fail") {
    exit 1
}

Write-Host "Mode=warn, continuing without failing the job."
exit 0
