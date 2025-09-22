# 🚀 Automatización de Túnel SIFU

Este directorio contiene scripts para automatizar la actualización y monitoreo del túnel de SIFU, mejorando significativamente el workflow de despliegue y la observabilidad del sistema.

## 📁 Archivos Incluidos

### Scripts Principales

| Archivo | Descripción | Uso Principal |
|---------|-------------|---------------|
| `automated_tunnel_update.ps1` | Script principal de actualización automatizada | Actualización completa con validaciones |
| `tunnel_monitoring_workflow.ps1` | Monitoreo programado del túnel | Verificación continua de salud |
| `setup_tunnel_automation.ps1` | Configuración inicial del sistema | Setup y configuración |

### Scripts de Soporte

| Archivo | Descripción |
|---------|-------------|
| `ejemplos_uso.ps1` | Ejemplos de uso de todos los scripts |
| `test_connectivity.ps1` | Pruebas de conectividad de endpoints |
| `tunnel_config.json` | Configuración del túnel (generado) |
| `monitoring_config.json` | Configuración de monitoreo (generado) |

### Scripts Legacy

| Archivo | Estado | Notas |
|---------|--------|-------|
| `docker_update_tunnel_secret.ps1` | ⚠️ Legacy | Usar `automated_tunnel_update.ps1` |
| `update_tunnel_secret.ps1` | ⚠️ Legacy | Funcionalidad integrada en script principal |
| `local_run_tunnel_backend.ps1` | ✅ Activo | Para desarrollo local |

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```powershell
# Ejecutar como administrador para configurar tareas programadas
.\scripts\deploy\setup_tunnel_automation.ps1 -SetupMonitoring -AlertWebhook "https://hooks.slack.com/..."
```

### 2. Actualización de Túnel

```powershell
# Actualización básica
.\scripts\deploy\automated_tunnel_update.ps1

# Con deploy automático del frontend
.\scripts\deploy\automated_tunnel_update.ps1 -TriggerDeploy

# Con imagen específica
.\scripts\deploy\automated_tunnel_update.ps1 -ImageTag "v1.2.3" -TriggerDeploy
```

### 3. Monitoreo

```powershell
# Verificación única
.\scripts\deploy\tunnel_monitoring_workflow.ps1 -CheckInterval 0

# Monitoreo continuo
.\scripts\deploy\tunnel_monitoring_workflow.ps1 -CheckInterval 5 -AlertWebhook "https://hooks.slack.com/..."
```

## 🔧 Características Principales

### Automated Tunnel Update

#### ✅ Mejoras Implementadas
- **Docker Pull Automático**: Actualiza la imagen del backend antes de recrear
- **Validación de Health Check**: Verifica que el sistema esté funcionando después de la actualización
- **Gestión de Estado**: Evita actualizaciones innecesarias si la URL no cambió
- **Logging Detallado**: Registro completo de todas las operaciones
- **Manejo de Errores**: Recuperación robusta ante fallos

#### 🔄 Flujo de Ejecución
1. **Verificación de Prerrequisitos**: Docker, GitHub CLI, archivos necesarios
2. **Actualización de Imagen**: `docker pull apmauj/sifu-backend:latest`
3. **Recreación del Backend**: Parar y levantar con nueva imagen
4. **Espera de Salud**: Verificar que el backend esté respondiendo
5. **Inicio del Túnel**: Recrear túnel con configuración actualizada
6. **Obtención de URL**: Extraer URL del túnel desde logs
7. **Validación Post-Actualización**: Health check completo del sistema
8. **Actualización de Secret**: Actualizar `VITE_PUBLIC_API_URL` en GitHub
9. **Deploy Opcional**: Disparar workflow de deploy del frontend

### Tunnel Monitoring Workflow

#### 📊 Verificaciones Implementadas
- **Health Check API**: Verificación de `/api/health` y `/api/health/simple`
- **Frescura de Datos**: Verificación de edad de datos UI (`/api/ui/latest`)
- **Métricas del Sistema**: Monitoreo de gaps, caché, memoria
- **Alertas Inteligentes**: Notificaciones solo tras múltiples fallos consecutivos

#### 🔔 Sistema de Alertas
- **Webhooks**: Soporte para Slack, Discord, Microsoft Teams
- **Umbrales Configurables**: Número de reintentos antes de alertar
- **Información Detallada**: Contexto completo en las alertas
- **Logging Persistente**: Historial completo en archivos de log

## ⚙️ Configuración

### Parámetros Principales

#### Automated Tunnel Update
```powershell
param(
    [string]$Repo = 'apmauj/sifu',           # Repositorio GitHub
    [string]$ImageTag = 'latest',            # Tag de imagen Docker
    [int]$TimeoutSeconds = 120,              # Timeout para URL del túnel
    [switch]$TriggerDeploy,                  # Disparar deploy del frontend
    [switch]$SkipIfUnchanged,                # Saltar si URL no cambió
    [int]$HealthCheckRetries = 5,            # Reintentos de health check
    [int]$HealthCheckInterval = 10           # Intervalo entre health checks
)
```

#### Tunnel Monitoring
```powershell
param(
    [string]$ApiUrl = "",                    # URL de la API (auto-detecta)
    [string]$AlertWebhook = "",              # Webhook para alertas
    [int]$MaxDataAge = 30,                   # Edad máxima de datos (minutos)
    [int]$CheckInterval = 5,                 # Intervalo entre checks (minutos)
    [int]$MaxRetries = 3,                    # Max reintentos antes de alertar
    [string]$LogFile = "tunnel_monitoring.log"  # Archivo de log
)
```

### Archivos de Configuración

#### tunnel_config.json
```json
{
    "DefaultImageTag": "latest",
    "TimeoutSeconds": 120,
    "HealthCheckRetries": 5,
    "HealthCheckInterval": 10,
    "AutoTriggerDeploy": false
}
```

#### monitoring_config.json
```json
{
    "CheckInterval": 10,
    "MaxDataAge": 30,
    "MaxRetries": 3,
    "AlertWebhook": "",
    "LogFile": "tunnel_monitoring.log",
    "EnableAlerts": false
}
```

## 🔐 Requisitos

### Software Necesario
- **PowerShell 5.1+** o **PowerShell Core 7+**
- **Docker** y **Docker Compose**
- **GitHub CLI** (`gh`) - autenticado
- **Permisos de administrador** (para tareas programadas)

### Configuración de GitHub CLI
```bash
# Autenticación
gh auth login

# Verificar permisos
gh auth status

# Verificar acceso al repositorio
gh repo view apmauj/sifu
```

### Configuración de Webhooks

#### Slack
1. Crear una app en https://api.slack.com/apps
2. Habilitar "Incoming Webhooks"
3. Crear webhook para el canal deseado
4. Usar URL del webhook en los scripts

#### Discord
1. Configurar webhook en el servidor Discord
2. Copiar URL del webhook
3. Usar directamente en los scripts

## 📋 Casos de Uso

### Desarrollo Diario
```powershell
# Actualización rápida con deploy
.\scripts\deploy\automated_tunnel_update.ps1 -TriggerDeploy
```

### Monitoreo en Producción
```powershell
# Configurar monitoreo cada 5 minutos con alertas
.\scripts\deploy\setup_tunnel_automation.ps1 -SetupMonitoring -MonitoringInterval 5 -AlertWebhook "https://hooks.slack.com/..."
```

### Debugging y Troubleshooting
```powershell
# Verificar conectividad
.\scripts\deploy\test_connectivity.ps1

# Monitoreo manual con logs detallados
.\scripts\deploy\tunnel_monitoring_workflow.ps1 -CheckInterval 0 -MaxDataAge 60
```

### Actualización con Imagen Específica
```powershell
# Usar versión específica del backend
.\scripts\deploy\automated_tunnel_update.ps1 -ImageTag "v1.2.3" -TriggerDeploy -TimeoutSeconds 180
```

## 🚨 Troubleshooting

### Problemas Comunes

#### Error: "Docker no está instalado"
```powershell
# Verificar instalación de Docker
docker --version
docker-compose --version
```

#### Error: "GitHub CLI no autenticado"
```powershell
# Re-autenticar
gh auth login
gh auth status
```

#### Error: "No se pudo obtener URL del túnel"
```powershell
# Verificar que el túnel esté corriendo
docker ps | findstr sifu-tunnel
docker logs sifu-tunnel --tail 50
```

#### Error: "Health check falló"
```powershell
# Verificar logs del backend
docker logs sifu-backend --tail 100

# Verificar conectividad manual
curl http://localhost:8000/api/health
```

### Logs y Debugging

#### Logs del Script de Actualización
- Salida en consola con timestamps
- Estado guardado en `.tunnel_last_url.txt`

#### Logs del Monitoreo
- Archivo: `tunnel_monitoring.log`
- Formato: `[YYYY-MM-DD HH:mm:ss] [LEVEL] Mensaje`
- Niveles: INFO, WARN, ERROR, SUCCESS

#### Logs de Docker
```powershell
# Backend
docker logs sifu-backend --tail 100 -f

# Túnel
docker logs sifu-tunnel --tail 100 -f
```

## 🔄 Integración con CI/CD

### GitHub Actions
Los scripts están diseñados para integrarse con GitHub Actions:

```yaml
- name: Update Tunnel
  run: |
    .\scripts\deploy\automated_tunnel_update.ps1 -TriggerDeploy
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Tareas Programadas de Windows
```powershell
# Crear tarea programada para monitoreo
.\scripts\deploy\setup_tunnel_automation.ps1 -SetupMonitoring -MonitoringInterval 10
```

## 📈 Métricas y Monitoreo

### KPIs del Sistema
- **Tiempo de Actualización**: < 3 minutos (objetivo)
- **Disponibilidad del Túnel**: > 99.5%
- **Tiempo de Detección de Problemas**: < 5 minutos
- **Tasa de Actualizaciones Exitosas**: > 95%

### Alertas Configurables
- **Datos Antiguos**: > 30 minutos (configurable)
- **Health Check Crítico**: Inmediato
- **Gaps en Datos**: Inmediato
- **Uso de Memoria**: > 90%

## 🎯 Próximas Mejoras

### Fase 2: Mejoras Planeadas
1. **Dashboard Web**: Interfaz web para monitoreo
2. **Métricas Avanzadas**: Prometheus/Grafana integration
3. **Auto-Recovery**: Recuperación automática ante fallos
4. **Multi-Tunnel**: Soporte para múltiples túneles simultáneos
5. **Notificaciones Push**: Integración con servicios móviles

### Optimizaciones Técnicas
1. **Paralelización**: Ejecución paralela de verificaciones
2. **Caching**: Cache de verificaciones para reducir latencia
3. **Compresión**: Compresión de logs y métricas
4. **Backup**: Backup automático de configuraciones

---

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar logs detallados
2. Verificar configuración en archivos JSON
3. Consultar ejemplos en `ejemplos_uso.ps1`
4. Probar conectividad con `test_connectivity.ps1`

**Última actualización**: $(Get-Date -Format 'yyyy-MM-dd')
**Versión**: 1.0.0
