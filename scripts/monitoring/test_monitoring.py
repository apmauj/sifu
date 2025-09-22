#!/usr/bin/env python3
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
    print("\n📋 Resultados:")
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
