#!/usr/bin/env pwsh

# Scripts de utilidad para SIFU con Docker en Windows
# Uso: .\docker-scripts.ps1 [comando]

param(
    [string]$Command = "help"
)

# Función para mostrar ayuda
function Show-Help {
    Write-Host "🔷 SIFU - Scripts Docker para Windows" -ForegroundColor Blue
    Write-Host "Uso: .\docker-scripts.ps1 [comando]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor Yellow
    Write-Host "  build        - Construir todas las imágenes"
    Write-Host "  up           - Ejecutar en modo desarrollo"
    Write-Host "  up-prod      - Ejecutar en modo producción"
    Write-Host "  up-gateway   - Ejecutar con reverse proxy"
    Write-Host "  down         - Detener todos los servicios"
    Write-Host "  logs         - Ver logs de todos los servicios"
    Write-Host "  status       - Ver estado de los servicios"
    Write-Host "  clean        - Limpiar contenedores e imágenes"
    Write-Host ""
}

# Función para build
function Docker-Build {
    Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Blue
    docker-compose build --parallel
    Write-Host "✅ Imágenes construidas exitosamente" -ForegroundColor Green
}

# Función para ejecutar en desarrollo
function Docker-Up {
    Write-Host "🚀 Iniciando SIFU en modo desarrollo..." -ForegroundColor Blue
    docker-compose up -d
    Write-Host "✅ Aplicación iniciada en:" -ForegroundColor Green
    Write-Host "  Frontend: http://localhost:31001" -ForegroundColor Yellow
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Yellow
    Write-Host "  API Docs: http://localhost:8000/api/docs" -ForegroundColor Yellow
    Write-Host "  Acceso externo: http://apmauj.ddns.net:31001" -ForegroundColor Yellow
}

# Función para ejecutar en producción
function Docker-Up-Prod {
    Write-Host "🚀 Iniciando SIFU en modo producción..." -ForegroundColor Blue
    docker-compose -f docker-compose.prod.yml up -d
    Write-Host "✅ Aplicación iniciada en modo producción" -ForegroundColor Green
}

# Función para ejecutar con gateway
function Docker-Up-Gateway {
    Write-Host "🚀 Iniciando SIFU con reverse proxy..." -ForegroundColor Blue
    docker-compose -f docker-compose.gateway.yml up -d
    Write-Host "✅ Aplicación iniciada con gateway:" -ForegroundColor Green
    Write-Host "  Acceso externo: http://apmauj.ddns.net/sifu" -ForegroundColor Yellow
    Write-Host "  Acceso local: http://localhost/sifu" -ForegroundColor Yellow
}

# Función para detener servicios
function Docker-Down {
    Write-Host "🛑 Deteniendo servicios..." -ForegroundColor Blue
    docker-compose down
    docker-compose -f docker-compose.prod.yml down 2>$null
    docker-compose -f docker-compose.gateway.yml down 2>$null
    Write-Host "✅ Servicios detenidos" -ForegroundColor Green
}

# Función para ver logs
function Docker-Logs {
    docker-compose logs -f
}

# Función para ver estado
function Docker-Status {
    Write-Host "📊 Estado de los servicios:" -ForegroundColor Blue
    docker-compose ps
}

# Función para limpiar
function Docker-Clean {
    $response = Read-Host "⚠️ ¿Estás seguro de que quieres limpiar todo? (y/N)"
    if ($response -match "^[Yy]$") {
        Write-Host "🧹 Limpiando contenedores, imágenes y volúmenes..." -ForegroundColor Blue
        docker-compose down -v --remove-orphans
        docker system prune -f
        docker volume prune -f
        Write-Host "✅ Limpieza completada" -ForegroundColor Green
    } else {
        Write-Host "Operación cancelada" -ForegroundColor Yellow
    }
}

# Procesar comando
switch ($Command.ToLower()) {
    "build" { Docker-Build }
    "up" { Docker-Up }
    "up-prod" { Docker-Up-Prod }
    "up-gateway" { Docker-Up-Gateway }
    "down" { Docker-Down }
    "logs" { Docker-Logs }
    "status" { Docker-Status }
    "clean" { Docker-Clean }
    default { Show-Help }
}
