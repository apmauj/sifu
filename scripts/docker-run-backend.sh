#!/bin/bash
# Script para ejecutar el contenedor backend con TOTP configurado

# Generar secret si no existe
if [ -z "$MONITORING_TOTP_SECRET" ]; then
    echo "⚠️  MONITORING_TOTP_SECRET no está configurado"
    echo "Genera uno con: python -c \"import pyotp; print(pyotp.random_base32())\""
    exit 1
fi

# Ejecutar contenedor con variables de entorno
docker run -d \
    --name sifu-backend-prod \
    -p 8000:8000 \
    -v ui_data:/app/data \
    -e PYTHONPATH=/app \
    -e PYTHONUNBUFFERED=1 \
    -e DATABASE_PATH=/app/data/ui_data.db \
    -e ENVIRONMENT=production \
    -e MONITORING_TOTP_SECRET="$MONITORING_TOTP_SECRET" \
    -e MONITORING_SESSION_HOURS="${MONITORING_SESSION_HOURS:-1}" \
    --restart unless-stopped \
    apmauj/sifu-backend:latest

echo "✅ Contenedor iniciado con TOTP configurado"
echo "Session duration: ${MONITORING_SESSION_HOURS:-1} hour(s)"
