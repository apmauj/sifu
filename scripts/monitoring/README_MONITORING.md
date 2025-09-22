# 🔍 Sistema de Monitoreo SIFU

Sistema completo de monitoreo programado para el túnel de SIFU, diseñado para funcionar en Linux y Windows con detección automática del entorno.

## 📁 Estructura de Archivos

```
scripts/monitoring/
├── tunnel_monitor.py          # Monitor principal
├── setup_monitoring.py        # Configuración inicial
├── quick_test.py              # Prueba rápida de conectividad
├── test_monitoring.py         # Script de prueba completo
├── demo_monitoring.py         # Demo del sistema
└── README_MONITORING.md       # Esta documentación

config/
└── monitoring_config.json     # Configuración principal

logs/
└── tunnel_monitoring.log      # Logs del sistema

scripts/monitoring/
├── cron_config.txt            # Configuración de cron (Linux)
└── sifu-monitoring.service    # Servicio systemd (Linux)
```

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# Configurar el sistema completo
python3 scripts/monitoring/setup_monitoring.py

# Probar conectividad
python3 scripts/monitoring/quick_test.py

# Ver demo del sistema
python3 scripts/monitoring/demo_monitoring.py
```

### 2. Ejecución del Monitoreo

```bash
# Monitoreo continuo (cada 5 minutos)
python3 scripts/monitoring/tunnel_monitor.py

# Verificación única
python3 scripts/monitoring/tunnel_monitor.py --single-run

# Con webhook de alertas
python3 scripts/monitoring/tunnel_monitor.py --alert-webhook "https://hooks.slack.com/..."
```

## 🔧 Características Principales

### ✅ Verificaciones Implementadas

#### 1. **Health Check Simple** (`/api/health/simple`)
- Verificación básica de disponibilidad
- Timeout: 10 segundos
- Respuesta esperada: `{"status": "ok"}`

#### 2. **Health Check Completo** (`/api/health`)
- Verificación avanzada del sistema
- Estado general: healthy/warning/critical
- Detalles de componentes individuales

#### 3. **Frescura de Datos** (`/api/ui/latest`)
- Verificación de edad de datos UI
- Umbral configurable (default: 30 minutos)
- Detección de gaps en datos

#### 4. **Métricas del Sistema** (`/api/metrics`)
- Monitoreo de uso de memoria
- Estado de cachés (BROU, BCU)
- Detección de gaps en datos UI
- Métricas de rendimiento

### 🔔 Sistema de Alertas

#### Configuración de Webhooks
- **Slack**: Integración completa con canales
- **Discord**: Notificaciones en servidores
- **Microsoft Teams**: Alertas en canales de trabajo
- **Custom**: Soporte para cualquier webhook HTTP

#### Tipos de Alertas
- **ERROR**: Problemas críticos que requieren atención inmediata
- **WARNING**: Problemas menores que deben monitorearse
- **INFO**: Información general del sistema

#### Umbrales Configurables
```json
{
  "max_data_age_minutes": 30,
  "max_response_time": 5.0,
  "max_memory_usage": 90,
  "max_cache_age_seconds": 3600,
  "max_retries": 3
}
```

### 📊 Logging y Observabilidad

#### Formato de Logs
```
2025-09-21 17:29:16,819 - INFO - Simple Health: HEALTHY - OK
2025-09-21 17:29:16,820 - INFO - Data Freshness: HEALTHY - Data is fresh (15.0 minutes old)
2025-09-21 17:29:16,821 - ERROR - System Metrics: CRITICAL - High memory usage detected
```

#### Niveles de Log
- **INFO**: Operaciones normales
- **WARNING**: Situaciones que requieren atención
- **ERROR**: Problemas que afectan funcionalidad
- **CRITICAL**: Problemas graves del sistema

## ⚙️ Configuración

### Archivo de Configuración Principal

```json
{
  "api_url": "",
  "check_interval": 5,
  "max_data_age": 30,
  "max_retries": 3,
  "alert_webhook": "",
  "log_file": "logs/tunnel_monitoring.log",
  "enable_alerts": false,
  "timeout": 10,
  "endpoints": {
    "health": "/health",
    "health_simple": "/health/simple",
    "ui_latest": "/ui/latest",
    "metrics": "/metrics",
    "brou_current": "/brou/current",
    "exchange_latest": "/exchange/latest"
  },
  "thresholds": {
    "max_response_time": 5.0,
    "max_data_age_minutes": 30,
    "max_memory_usage": 90,
    "max_cache_age_seconds": 3600
  }
}
```

### Parámetros de Línea de Comandos

```bash
python3 tunnel_monitor.py [OPCIONES]

Opciones:
  --api-url URL              URL de la API (auto-detecta si no se proporciona)
  --check-interval MINUTES   Intervalo entre verificaciones en minutos (0 = una sola ejecución)
  --max-data-age MINUTES     Edad máxima permitida para los datos
  --max-retries COUNT        Número máximo de reintentos antes de alertar
  --alert-webhook URL        URL del webhook para alertas
  --log-file PATH            Archivo de log
  --config FILE              Archivo de configuración
  --single-run               Ejecutar una sola vez y salir
```

## 🐧 Configuración en Linux

### Opción 1: Cron (Recomendado para sistemas simples)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar cada 5 minutos
*/5 * * * * cd /home/apmauj/repos/sifu && python3 scripts/monitoring/tunnel_monitor.py --single-run >> logs/cron_monitoring.log 2>&1
```

### Opción 2: Systemd Service (Recomendado para producción)

```bash
# Copiar archivo de servicio
sudo cp scripts/monitoring/sifu-monitoring.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable sifu-monitoring.service

# Iniciar servicio
sudo systemctl start sifu-monitoring.service

# Verificar estado
sudo systemctl status sifu-monitoring.service

# Ver logs
sudo journalctl -u sifu-monitoring.service -f
```

### Opción 3: Supervisor (Para entornos avanzados)

```ini
[program:sifu-monitoring]
command=python3 /home/apmauj/repos/sifu/scripts/monitoring/tunnel_monitor.py
directory=/home/apmauj/repos/sifu
user=apmauj
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/apmauj/repos/sifu/logs/supervisor_monitoring.log
```

## 🪟 Configuración en Windows

### Opción 1: Tarea Programada

```powershell
# Crear tarea programada
schtasks /create /tn "SIFU Monitoring" /tr "python.exe C:\path\to\sifu\scripts\monitoring\tunnel_monitor.py" /sc minute /mo 5 /ru SYSTEM
```

### Opción 2: PowerShell Script

```powershell
# Ejecutar como servicio
.\scripts\monitoring\tunnel_monitor.py --check-interval 5
```

### Opción 3: Windows Service (Usando NSSM)

```bash
# Descargar NSSM
# Instalar como servicio
nssm install SIFU-Monitoring python.exe
nssm set SIFU-Monitoring Parameters "C:\path\to\sifu\scripts\monitoring\tunnel_monitor.py"
nssm set SIFU-Monitoring AppDirectory "C:\path\to\sifu"
nssm start SIFU-Monitoring
```

## 🔔 Configuración de Alertas

### Slack

1. **Crear App de Slack**:
   - Ve a https://api.slack.com/apps
   - Crea una nueva app
   - Ve a "Incoming Webhooks" y actívalo
   - Crea un webhook para tu canal

2. **Configurar Webhook**:
   ```bash
   python3 tunnel_monitor.py --alert-webhook "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
   ```

### Discord

1. **Crear Webhook**:
   - Ve a la configuración del servidor
   - Integraciones → Webhooks
   - Crea un nuevo webhook

2. **Configurar**:
   ```bash
   python3 tunnel_monitor.py --alert-webhook "https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXX"
   ```

### Microsoft Teams

1. **Crear Webhook**:
   - Ve a tu canal de Teams
   - Más opciones → Conectores
   - Configura "Incoming Webhook"

2. **Configurar**:
   ```bash
   python3 tunnel_monitor.py --alert-webhook "https://outlook.office.com/webhook/XXXXXXXXXXXXXXXXXXXXXXXX"
   ```

## 🧪 Testing y Debugging

### Pruebas Rápidas

```bash
# Prueba de conectividad básica
python3 scripts/monitoring/quick_test.py

# Prueba completa del sistema
python3 scripts/monitoring/test_monitoring.py

# Demo del sistema (sin backend)
python3 scripts/monitoring/demo_monitoring.py
```

### Debugging

```bash
# Ejecutar con logs detallados
python3 tunnel_monitor.py --single-run --log-file logs/debug.log

# Verificar configuración
cat config/monitoring_config.json

# Revisar logs
tail -f logs/tunnel_monitoring.log
```

### Verificación de Endpoints

```bash
# Verificar endpoints manualmente
curl http://localhost:8000/api/health/simple
curl http://localhost:8000/api/health
curl http://localhost:8000/api/ui/latest
curl http://localhost:8000/api/metrics
```

## 📊 Métricas y KPIs

### Métricas del Sistema
- **Tiempo de Respuesta**: < 5 segundos (objetivo)
- **Disponibilidad**: > 99.5%
- **Tiempo de Detección**: < 5 minutos
- **Tasa de Alertas Falsas**: < 5%

### Métricas de Datos
- **Frescura de Datos UI**: < 30 minutos
- **Gaps en Datos**: 0 gaps críticos
- **Edad de Caché BROU**: < 1 hora
- **Edad de Caché BCU**: < 1 hora

### Métricas de Sistema
- **Uso de Memoria**: < 90%
- **Uso de CPU**: < 80%
- **Tiempo de Verificación**: < 10 segundos

## 🚨 Troubleshooting

### Problemas Comunes

#### Error: "Connection Error"
```bash
# Verificar que el backend esté ejecutándose
docker ps | grep sifu-backend

# Verificar puertos
netstat -tlnp | grep 8000

# Revisar logs del backend
docker logs sifu-backend --tail 50
```

#### Error: "No se pudo detectar URL del túnel"
```bash
# Verificar que el túnel esté ejecutándose
docker ps | grep sifu-tunnel

# Revisar logs del túnel
docker logs sifu-tunnel --tail 100

# Buscar URL en logs
docker logs sifu-tunnel | grep trycloudflare.com
```

#### Error: "Health check falló"
```bash
# Verificar endpoints manualmente
curl -v http://localhost:8000/api/health/simple

# Revisar configuración
cat config/monitoring_config.json

# Verificar timeouts
python3 tunnel_monitor.py --single-run --timeout 30
```

### Logs y Debugging

#### Ubicación de Logs
- **Logs principales**: `logs/tunnel_monitoring.log`
- **Logs de cron**: `logs/cron_monitoring.log`
- **Logs de systemd**: `journalctl -u sifu-monitoring.service`

#### Formato de Logs
```
[2025-09-21 17:29:16,819] [INFO] Simple Health: HEALTHY - OK
[2025-09-21 17:29:16,820] [ERROR] Data Freshness: CRITICAL - Data is stale (45.0 minutes old)
[2025-09-21 17:29:16,821] [WARNING] System Metrics: WARNING - Issues: High memory usage
```

#### Comandos de Debugging
```bash
# Seguir logs en tiempo real
tail -f logs/tunnel_monitoring.log

# Buscar errores específicos
grep "ERROR" logs/tunnel_monitoring.log

# Verificar configuración
python3 -c "import json; print(json.load(open('config/monitoring_config.json')))"

# Probar conectividad
python3 scripts/monitoring/quick_test.py
```

## 🔄 Integración con CI/CD

### GitHub Actions

```yaml
name: SIFU Monitoring
on:
  schedule:
    - cron: '*/5 * * * *'  # Cada 5 minutos
  workflow_dispatch:

jobs:
  monitoring:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install requests
      - name: Run monitoring
        run: |
          python3 scripts/monitoring/tunnel_monitor.py --single-run
        env:
          API_URL: ${{ secrets.SIFU_API_URL }}
          ALERT_WEBHOOK: ${{ secrets.ALERT_WEBHOOK }}
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    triggers {
        cron('*/5 * * * *')
    }
    stages {
        stage('Monitor') {
            steps {
                sh 'python3 scripts/monitoring/tunnel_monitor.py --single-run'
            }
        }
    }
    post {
        failure {
            // Enviar notificación en caso de fallo
            slackSend channel: '#alerts', message: 'SIFU Monitoring failed!'
        }
    }
}
```

## 📈 Roadmap y Mejoras Futuras

### Fase 2: Mejoras Planeadas
1. **Dashboard Web**: Interfaz web para visualizar métricas
2. **Prometheus Integration**: Exportación de métricas a Prometheus
3. **Grafana Dashboards**: Dashboards visuales para métricas
4. **Auto-Recovery**: Recuperación automática ante fallos
5. **Multi-Tunnel Support**: Soporte para múltiples túneles

### Optimizaciones Técnicas
1. **Paralelización**: Ejecución paralela de verificaciones
2. **Caching**: Cache de verificaciones para reducir latencia
3. **Compresión**: Compresión de logs y métricas
4. **Backup**: Backup automático de configuraciones

### Integraciones Adicionales
1. **PagerDuty**: Integración con sistemas de alertas empresariales
2. **Datadog**: Integración con plataformas de monitoreo
3. **New Relic**: Integración con APM
4. **Custom APIs**: Soporte para APIs personalizadas

---

## 📞 Soporte

Para problemas o sugerencias:

1. **Revisar logs**: `tail -f logs/tunnel_monitoring.log`
2. **Verificar configuración**: `cat config/monitoring_config.json`
3. **Probar conectividad**: `python3 scripts/monitoring/quick_test.py`
4. **Ejecutar demo**: `python3 scripts/monitoring/demo_monitoring.py`

### Comandos de Emergencia

```bash
# Detener monitoreo
sudo systemctl stop sifu-monitoring.service

# Reiniciar monitoreo
sudo systemctl restart sifu-monitoring.service

# Verificar estado
sudo systemctl status sifu-monitoring.service

# Ver logs recientes
sudo journalctl -u sifu-monitoring.service --since "1 hour ago"
```

**Última actualización**: 2025-09-21  
**Versión**: 1.0.0  
**Compatibilidad**: Linux, Windows, macOS
