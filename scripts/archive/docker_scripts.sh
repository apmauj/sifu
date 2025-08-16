#!/bin/bash

# Scripts de utilidad para SIFU con Docker
# Uso: ./docker-scripts.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}SIFU - Scripts Docker${NC}"
    echo -e "${YELLOW}Uso:${NC} ./docker-scripts.sh [comando]"
    echo ""
    echo -e "${YELLOW}Comandos disponibles:${NC}"
    echo "  build        - Construir todas las imágenes"
    echo "  up           - Ejecutar en modo desarrollo"
    echo "  up-prod      - Ejecutar en modo producción"
    echo "  up-gateway   - Ejecutar con reverse proxy para acceso externo"
    echo "  down         - Detener todos los servicios"
    echo "  logs         - Ver logs de todos los servicios"
    echo "  logs-backend - Ver logs solo del backend"
    echo "  logs-frontend- Ver logs solo del frontend"
    echo "  restart      - Reiniciar todos los servicios"
    echo "  clean        - Limpiar contenedores, imágenes y volúmenes"
    echo "  status       - Ver estado de los servicios"
    echo "  shell-backend- Abrir shell en el backend"
    echo "  shell-frontend- Abrir shell en el frontend"
    echo "  backup       - Hacer backup de la base de datos"
    echo "  restore      - Restaurar backup de la base de datos"
    echo ""
}

# Función para build
docker_build() {
    echo -e "${BLUE}🔨 Construyendo imágenes Docker...${NC}"
    docker-compose build --parallel
    echo -e "${GREEN}✅ Imágenes construidas exitosamente${NC}"
}

# Función para ejecutar en desarrollo
docker_up() {
    echo -e "${BLUE}🚀 Iniciando SIFU en modo desarrollo...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Aplicación iniciada en:${NC}"
    echo -e "  Frontend: ${YELLOW}http://localhost:31001${NC}"
    echo -e "  Backend:  ${YELLOW}http://localhost:8000${NC}"
    echo -e "  API Docs: ${YELLOW}http://localhost:8000/api/docs${NC}"
    echo -e "  Acceso externo: ${YELLOW}http://apmauj.ddns.net:31001${NC}"
}

# Función para ejecutar en producción
docker_up_prod() {
    echo -e "${BLUE}🚀 Iniciando SIFU en modo producción...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    echo -e "${GREEN}✅ Aplicación iniciada en modo producción:${NC}"
    echo -e "  Frontend: ${YELLOW}http://localhost${NC}"
    echo -e "  Backend:  ${YELLOW}http://localhost:8000${NC}"
}

# Función para ejecutar con gateway
docker_up_gateway() {
    echo -e "${BLUE}🚀 Iniciando SIFU con reverse proxy...${NC}"
    docker-compose -f docker-compose.gateway.yml up -d
    echo -e "${GREEN}✅ Aplicación iniciada con gateway:${NC}"
    echo -e "  Acceso externo: ${YELLOW}http://apmauj.ddns.net/sifu${NC}"
    echo -e "  Acceso local: ${YELLOW}http://localhost/sifu${NC}"
    echo -e "  API: ${YELLOW}http://apmauj.ddns.net/sifu/api${NC}"
}

# Función para detener servicios
docker_down() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    docker-compose down
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker-compose -f docker-compose.gateway.yml down 2>/dev/null || true
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para ver logs
docker_logs() {
    docker-compose logs -f
}

# Función para ver logs del backend
docker_logs_backend() {
    docker-compose logs -f backend
}

# Función para ver logs del frontend
docker_logs_frontend() {
    docker-compose logs -f frontend
}

# Función para reiniciar servicios
docker_restart() {
    echo -e "${BLUE}🔄 Reiniciando servicios...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Servicios reiniciados${NC}"
}

# Función para limpiar todo
docker_clean() {
    echo -e "${YELLOW}⚠️  ¿Estás seguro de que quieres limpiar todo? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🧹 Limpiando contenedores, imágenes y volúmenes...${NC}"
        docker-compose down -v --remove-orphans
        docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
        docker system prune -f
        docker volume prune -f
        echo -e "${GREEN}✅ Limpieza completada${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para ver estado
docker_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
}

# Función para abrir shell en backend
docker_shell_backend() {
    echo -e "${BLUE}🐚 Abriendo shell en el backend...${NC}"
    docker-compose exec backend /bin/bash
}

# Función para abrir shell en frontend
docker_shell_frontend() {
    echo -e "${BLUE}🐚 Abriendo shell en el frontend...${NC}"
    docker-compose exec frontend /bin/sh
}

# Función para hacer backup
docker_backup() {
    echo -e "${BLUE}💾 Creando backup de la base de datos...${NC}"
    mkdir -p backups
    timestamp=$(date +"%Y%m%d_%H%M%S")
    docker-compose exec backend cp /app/data/ui_data.db /app/data/ui_data_backup_${timestamp}.db
    docker cp $(docker-compose ps -q backend):/app/data/ui_data_backup_${timestamp}.db ./backups/
    echo -e "${GREEN}✅ Backup creado: ./backups/ui_data_backup_${timestamp}.db${NC}"
}

# Función para restaurar backup
docker_restore() {
    echo -e "${BLUE}📥 Restaurando backup de la base de datos...${NC}"
    echo -e "${YELLOW}Backups disponibles:${NC}"
    ls -la backups/ui_data_backup_*.db 2>/dev/null || echo "No hay backups disponibles"
    echo -e "${YELLOW}Ingresa el nombre del archivo de backup:${NC}"
    read -r backup_file
    if [ -f "backups/$backup_file" ]; then
        docker cp "backups/$backup_file" $(docker-compose ps -q backend):/app/data/ui_data.db
        docker-compose restart backend
        echo -e "${GREEN}✅ Backup restaurado exitosamente${NC}"
    else
        echo -e "${RED}❌ Archivo de backup no encontrado${NC}"
    fi
}

# Procesar comando
case "${1:-help}" in
    build)
        docker_build
        ;;
    up)
        docker_up
        ;;
    up-prod)
        docker_up_prod
        ;;
    up-gateway)
        docker_up_gateway
        ;;
    down)
        docker_down
        ;;
    logs)
        docker_logs
        ;;
    logs-backend)
        docker_logs_backend
        ;;
    logs-frontend)
        docker_logs_frontend
        ;;
    restart)
        docker_restart
        ;;
    clean)
        docker_clean
        ;;
    status)
        docker_status
        ;;
    shell-backend)
        docker_shell_backend
        ;;
    shell-frontend)
        docker_shell_frontend
        ;;
    backup)
        docker_backup
        ;;
    restore)
        docker_restore
        ;;
    help|*)
        show_help
        ;;
esac 