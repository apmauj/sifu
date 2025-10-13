# Análisis de colores hardcodeados en frontend
Write-Host "
=== ANÁLISIS DE COLORES HARDCODEADOS ===" -ForegroundColor Cyan

# Buscar en archivos de componentes (excluyendo tests)
$componentColors = Get-ChildItem -Path src/components -Filter *.jsx -Recurse | 
    Select-String -Pattern "(text|bg|border)-(blue|red|green|yellow|orange|purple|indigo|teal|gray|pink|cyan)-\d+" | 
    Group-Object Path | 
    Select-Object @{Name='File';Expression={Split-Path $_.Name -Leaf}}, Count

Write-Host "
--- COMPONENTES (src/components/*.jsx) ---" -ForegroundColor Yellow
$componentColors | Format-Table -AutoSize
$totalComponents = ($componentColors | Measure-Object Count -Sum).Sum
Write-Host "Total en componentes: $totalComponents matches" -ForegroundColor Green

# Buscar en tests
$testColors = Get-ChildItem -Path src/test -Filter *.jsx -Recurse | 
    Select-String -Pattern "(text|bg|border)-(blue|red|green|yellow|orange|purple|indigo|teal|gray|pink|cyan)-\d+" | 
    Group-Object Path | 
    Select-Object @{Name='File';Expression={Split-Path $_.Name -Leaf}}, Count

Write-Host "
--- TESTS (src/test/**/*.jsx) ---" -ForegroundColor Yellow
$testColors | Format-Table -AutoSize
$totalTests = ($testColors | Measure-Object Count -Sum).Sum
Write-Host "Total en tests: $totalTests matches" -ForegroundColor Green

Write-Host "
=== RESUMEN ===" -ForegroundColor Cyan
Write-Host "Componentes: $totalComponents colores hardcodeados"
Write-Host "Tests: $totalTests colores hardcodeados"
Write-Host "TOTAL:  matches" -ForegroundColor Magenta
