# Docker Deployment Guide - TOTP Configuration

Esta guía explica cómo configurar el `MONITORING_TOTP_SECRET` en el contenedor Docker del backend.

## 📋 Métodos de Configuración

### Método 1: Docker Compose (Recomendado)

#### Paso 1: Crear archivo .env.docker

```bash
# Copiar el template
cp .env.docker.example .env.docker

# Generar secret
python -c "import pyotp; print(pyotp.random_base32())"
# Output: XYZ123ABC456DEF789...
```

#### Paso 2: Editar .env.docker

```bash
# .env.docker
MONITORING_TOTP_SECRET=XYZ123ABC456DEF789
MONITORING_SESSION_HOURS=1
```

#### Paso 3: Levantar con docker-compose

```bash
# Usando el archivo .env.docker
docker-compose --env-file .env.docker -f docker-compose.prod.yml up -d

# O si renombraste .env.docker a .env
docker-compose -f docker-compose.prod.yml up -d
```

### Método 2: Variables de entorno directas

#### Linux/Mac:

```bash
# Exportar variables
export MONITORING_TOTP_SECRET="XYZ123ABC456DEF789"
export MONITORING_SESSION_HOURS=1

# Ejecutar script
chmod +x scripts/docker-run-backend.sh
./scripts/docker-run-backend.sh
```

#### Windows (PowerShell):

```powershell
# Configurar variables
$env:MONITORING_TOTP_SECRET = "XYZ123ABC456DEF789"
$env:MONITORING_SESSION_HOURS = 1

# Ejecutar script
.\scripts\docker-run-backend.ps1
```

### Método 3: Docker run directo

```bash
docker run -d \
    --name sifu-backend-prod \
    -p 8000:8000 \
    -v ui_data:/app/data \
    -e ENVIRONMENT=production \
    -e MONITORING_TOTP_SECRET="XYZ123ABC456DEF789" \
    -e MONITORING_SESSION_HOURS=1 \
    --restart unless-stopped \
    apmauj/sifu-backend:latest
```

## 🔧 Setup Inicial - Configurar Authenticator App

Una vez que el contenedor esté corriendo:

### Opción A: Endpoint de Setup (Solo primera vez)

```bash
# 1. Cambiar temporalmente a development
docker exec sifu-backend-prod \
    sh -c "export ENVIRONMENT=development && uvicorn main:app --reload" &

# 2. Obtener QR code
curl http://localhost:8000/api/monitoring/setup

# 3. Escanear QR con Google Authenticator/Authy

# 4. Detener y volver a production
docker stop sifu-backend-prod
docker start sifu-backend-prod  # Con ENVIRONMENT=production
```

### Opción B: Manual (Sin endpoint)

```bash
# 1. Obtener el secret del contenedor
docker exec sifu-backend-prod env | grep MONITORING_TOTP_SECRET

# 2. Crear URI manualmente
echo "otpauth://totp/SIFU%20Monitoring?secret=TU_SECRET&issuer=SIFU"

# 3. Usar un generador de QR online o app que acepte entrada manual
# Ejemplo: https://www.the-qrcode-generator.com/
```

## 🔍 Verificación

```bash
# 1. Verificar que las variables estén configuradas
docker exec sifu-backend-prod env | grep MONITORING

# Output esperado:
# MONITORING_TOTP_SECRET=XYZ123ABC456DEF789
# MONITORING_SESSION_HOURS=1

# 2. Verificar que el servidor esté corriendo
curl http://localhost:8000/api/health

# 3. Probar endpoint de verificación (con código de tu app)
curl -X POST "http://localhost:8000/api/monitoring/verify?code=123456"

# Si es válido, recibirás:
# {
#   "access": "granted",
#   "session_token": "uuid-here",
#   "expires_in": 3600
# }
```

## 🔐 Seguridad - Best Practices

### ✅ Recomendado

1. **Secret único por entorno:**
   ```bash
   Dev:     MONITORING_TOTP_SECRET=ABC123...
   Staging: MONITORING_TOTP_SECRET=DEF456...
   Prod:    MONITORING_TOTP_SECRET=XYZ789...  # Diferente!
   ```

2. **No hardcodear en docker-compose.yml:**
   ```yaml
   # ❌ MAL
   environment:
     - MONITORING_TOTP_SECRET=ABC123...
   
   # ✅ BIEN
   environment:
     - MONITORING_TOTP_SECRET=${MONITORING_TOTP_SECRET}
   ```

3. **Usar secretos de Docker Swarm o Kubernetes:**
   ```bash
   # Docker Swarm
   echo "XYZ123..." | docker secret create monitoring_totp -
   
   # En docker-compose.yml
   secrets:
     - monitoring_totp
   ```

### ❌ Evitar

- ❌ Commitear el secret en git
- ❌ Compartir el mismo secret entre dev y prod
- ❌ Hardcodear en Dockerfile o docker-compose
- ❌ Enviar el secret por email sin encriptar

## 🔄 Rotación de Secret

```bash
# 1. Generar nuevo secret
python -c "import pyotp; print(pyotp.random_base32())"

# 2. Actualizar .env.docker
nano .env.docker  # Cambiar MONITORING_TOTP_SECRET

# 3. Recrear contenedor
docker-compose -f docker-compose.prod.yml down
docker-compose --env-file .env.docker -f docker-compose.prod.yml up -d

# 4. Reconfigurar authenticator apps de todo el equipo
```

## 📝 Troubleshooting

### Problema: "No MONITORING_TOTP_SECRET found"

```bash
# Verificar que la variable esté pasando al contenedor
docker exec sifu-backend-prod env | grep MONITORING

# Si está vacía, revisar:
# 1. Que .env.docker tenga el valor
# 2. Que docker-compose use --env-file
# 3. Que la variable no tenga espacios extra
```

### Problema: "Invalid or expired TOTP code"

```bash
# 1. Verificar que el reloj del servidor esté sincronizado
docker exec sifu-backend-prod date

# 2. Verificar que el secret sea correcto
docker exec sifu-backend-prod env | grep MONITORING_TOTP_SECRET

# 3. Probar con el código actual
python -c "import pyotp; totp = pyotp.TOTP('TU_SECRET'); print(totp.now())"
```

## 🌐 Integración con Cloud Providers

### AWS ECS

```json
{
  "environment": [
    {
      "name": "MONITORING_TOTP_SECRET",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:monitoring-totp"
    }
  ]
}
```

### Google Cloud Run

```bash
gcloud run deploy sifu-backend \
    --image gcr.io/project/sifu-backend \
    --set-secrets MONITORING_TOTP_SECRET=monitoring-totp:latest
```

### Azure Container Instances

```bash
az container create \
    --resource-group myResourceGroup \
    --name sifu-backend \
    --image apmauj/sifu-backend:latest \
    --secure-environment-variables \
        MONITORING_TOTP_SECRET=$SECRET
```

## 📚 Referencias

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [PyOTP Documentation](https://pyauth.github.io/pyotp/)
- [TOTP Setup Guide](./TOTP_SETUP.md)
