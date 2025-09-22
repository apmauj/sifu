#!/usr/bin/env python3
"""
Script de configuración para el sistema de monitoreo de SIFU
Configura el entorno y crea archivos de configuración necesarios
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any


def create_directory_structure():
    """Crear estructura de directorios necesaria"""
    directories = [
        "scripts/monitoring",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {directory}")


def create_monitoring_config(webhook_url: str = "", check_interval: int = 5, max_data_age: int = 30) -> Dict[str, Any]:
    """Crear configuración de monitoreo"""
    config = {
        "api_url": "",
        "check_interval": check_interval,
        "max_data_age": max_data_age,
        "max_retries": 3,
        "alert_webhook": webhook_url,
        "log_file": "logs/tunnel_monitoring.log",
        "enable_alerts": bool(webhook_url),
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
            "max_data_age_minutes": max_data_age,
            "max_memory_usage": 90,
            "max_cache_age_seconds": 3600
        }
    }
    
    return config


def create_cron_config() -> str:
    """Crear configuración de cron para Linux"""
    cron_content = """# SIFU Tunnel Monitoring - Cron Configuration
# Ejecutar cada 5 minutos
*/5 * * * * cd /home/apmauj/repos/sifu && python3 scripts/monitoring/tunnel_monitor.py --single-run >> logs/cron_monitoring.log 2>&1

# Ejecutar cada hora (verificación más completa)
0 * * * * cd /home/apmauj/repos/sifu && python3 scripts/monitoring/tunnel_monitor.py --single-run --check-interval 0 >> logs/cron_monitoring.log 2>&1
"""
    return cron_content


def create_systemd_service() -> str:
    """Crear servicio systemd para Linux"""
    service_content = """[Unit]
Description=SIFU Tunnel Monitoring Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=apmauj
Group=apmauj
WorkingDirectory=/home/apmauj/repos/sifu
ExecStart=/usr/bin/python3 /home/apmauj/repos/sifu/scripts/monitoring/tunnel_monitor.py --check-interval 5
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

# Variables de entorno
Environment=PYTHONPATH=/home/apmauj/repos/sifu

[Install]
WantedBy=multi-user.target
"""
    return service_content


def create_test_script() -> str:
    """Crear script de prueba del sistema de monitoreo"""
    test_script = """#!/usr/bin/env python3
'''
Script de prueba para el sistema de monitoreo de SIFU
Prueba todos los endpoints y funciones del monitor
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.monitoring.tunnel_monitor import TunnelMonitor, MonitoringConfig
import time

def test_monitoring_system():
    print("🧪 Probando sistema de monitoreo de SIFU")
    print("=" * 50)
    
    # Configuración de prueba
    config = MonitoringConfig(
        api_url="http://localhost:8000/api",  # Cambiar por la URL real
        check_interval=0,  # Solo una ejecución
        max_data_age=30,
        max_retries=1,
        alert_webhook="",  # Sin alertas para pruebas
        log_file="logs/test_monitoring.log",
        enable_alerts=False,
        timeout=10
    )
    
    # Crear monitor
    monitor = TunnelMonitor(config)
    
    print(f"📡 URL de la API: {config.api_url}")
    print(f"⏱️  Timeout: {config.timeout} segundos")
    print(f"📊 Edad máxima de datos: {config.max_data_age} minutos")
    print()
    
    # Ejecutar verificaciones
    print("🔍 Ejecutando verificaciones de salud...")
    results = monitor.run_health_checks(config.api_url)
    
    # Mostrar resultados
    print("\\n📋 Resultados:")
    print("-" * 30)
    
    for result in results:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "error": "💥"
        }.get(result.status, "❓")
        
        print(f"{status_icon} {result.endpoint}")
        print(f"   Estado: {result.status.upper()}")
        print(f"   Mensaje: {result.message}")
        if result.response_time > 0:
            print(f"   Tiempo de respuesta: {result.response_time:.2f}s")
        print()
    
    # Evaluar resultados
    all_passed = monitor.evaluate_results(results)
    
    if all_passed:
        print("🎉 Todas las verificaciones pasaron correctamente!")
        return True
    else:
        print("⚠️  Algunas verificaciones fallaron")
        return False

if __name__ == "__main__":
    try:
        success = test_monitoring_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
        sys.exit(1)
"""
    return test_script


def install_dependencies():
    """Instalar dependencias necesarias"""
    print("📦 Instalando dependencias...")
    
    try:
        # Verificar si requests está instalado
        import requests
        print("✅ requests ya está instalado")
    except ImportError:
        print("📥 Instalando requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        print("✅ requests instalado exitosamente")
    
    # Verificar otras dependencias opcionales
    optional_deps = ["psutil", "schedule"]
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} ya está instalado")
        except ImportError:
            print(f"📥 Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ {dep} instalado exitosamente")


def setup_webhook_guide():
    """Mostrar guía para configurar webhooks"""
    guide = """
🔔 Configuración de Webhooks para Alertas

1. SLACK:
   - Ve a https://api.slack.com/apps
   - Crea una nueva app
   - Ve a "Incoming Webhooks" y actívalo
   - Crea un webhook para tu canal
   - Usa la URL del webhook en la configuración

2. DISCORD:
   - Ve a la configuración del servidor
   - Integraciones → Webhooks
   - Crea un nuevo webhook
   - Copia la URL del webhook

3. MICROSOFT TEAMS:
   - Ve a tu canal de Teams
   - Más opciones → Conectores
   - Configura "Incoming Webhook"
   - Copia la URL del webhook

4. USAR WEBHOOK:
   python3 scripts/monitoring/tunnel_monitor.py --alert-webhook "URL_DEL_WEBHOOK"
"""
    return guide


def main():
    """Función principal de configuración"""
    print("🔧 Configurando sistema de monitoreo de SIFU")
    print("=" * 50)
    
    # Crear estructura de directorios
    create_directory_structure()
    
    # Instalar dependencias
    install_dependencies()
    
    # Crear archivos de configuración
    print("\\n📝 Creando archivos de configuración...")
    
    # Configuración principal
    config = create_monitoring_config()
    with open("config/monitoring_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("✅ Configuración creada: config/monitoring_config.json")
    
    # Script de prueba
    test_script = create_test_script()
    with open("scripts/monitoring/test_monitoring.py", "w") as f:
        f.write(test_script)
    os.chmod("scripts/monitoring/test_monitoring.py", 0o755)
    print("✅ Script de prueba creado: scripts/monitoring/test_monitoring.py")
    
    # Configuración de cron (Linux)
    cron_config = create_cron_config()
    with open("scripts/monitoring/cron_config.txt", "w") as f:
        f.write(cron_config)
    print("✅ Configuración de cron creada: scripts/monitoring/cron_config.txt")
    
    # Servicio systemd (Linux)
    systemd_service = create_systemd_service()
    with open("scripts/monitoring/sifu-monitoring.service", "w") as f:
        f.write(systemd_service)
    print("✅ Servicio systemd creado: scripts/monitoring/sifu-monitoring.service")
    
    # Crear directorio de logs
    Path("logs").mkdir(exist_ok=True)
    print("✅ Directorio de logs creado: logs/")
    
    # Mostrar guía de webhooks
    print("\\n" + setup_webhook_guide())
    
    print("\\n🎉 Configuración completada!")
    print("\\n📋 Próximos pasos:")
    print("1. Probar el sistema: python3 scripts/monitoring/test_monitoring.py")
    print("2. Configurar webhook (opcional): Editar config/monitoring_config.json")
    print("3. Ejecutar monitoreo: python3 scripts/monitoring/tunnel_monitor.py")
    print("4. Para Linux, configurar cron o systemd usando los archivos creados")
    
    print("\\n🔗 Archivos creados:")
    print("• config/monitoring_config.json - Configuración principal")
    print("• scripts/monitoring/test_monitoring.py - Script de prueba")
    print("• scripts/monitoring/cron_config.txt - Configuración de cron")
    print("• scripts/monitoring/sifu-monitoring.service - Servicio systemd")
    print("• logs/ - Directorio para archivos de log")


if __name__ == "__main__":
    main()
