#!/usr/bin/env python3
"""
Demo del sistema de monitoreo de SIFU
Simula el comportamiento del sistema para demostrar las funcionalidades
"""

import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List


class MockResponse:
    """Simulación de respuesta HTTP para demo"""
    
    def __init__(self, status_code: int, data: Dict[str, Any]):
        self.status_code = status_code
        self._data = data
        self.elapsed = type('obj', (object,), {'total_seconds': lambda: 0.5})()
    
    def json(self):
        return self._data


class MockRequests:
    """Simulación de requests para demo"""
    
    @staticmethod
    def get(url: str, timeout: int = 10) -> MockResponse:
        """Simular llamadas HTTP"""
        
        # Simular diferentes estados del sistema
        if "/health/simple" in url:
            return MockResponse(200, {"status": "ok", "timestamp": datetime.now().isoformat()})
        
        elif "/health" in url:
            return MockResponse(200, {
                "overall_status": "healthy",
                "message": "All systems operational",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": "healthy",
                    "cache": "healthy",
                    "external_apis": "healthy"
                }
            })
        
        elif "/ui/latest" in url:
            # Simular datos frescos (menos de 30 minutos)
            data_date = datetime.now() - timedelta(minutes=15)
            return MockResponse(200, {
                "data": {
                    "date": data_date.isoformat(),
                    "value": 45.67,
                    "source": "INE"
                },
                "status": "success"
            })
        
        elif "/metrics" in url:
            return MockResponse(200, {
                "ui_freshness": {
                    "ui_gap_detected": False,
                    "ui_latest_age_seconds": 900
                },
                "cache_status": {
                    "brou_cache_age_seconds": 1800,
                    "bcu_cache_age_seconds": 2100
                },
                "system": {
                    "memory_usage_percent": 65.2,
                    "cpu_usage_percent": 23.1
                }
            })
        
        elif "/brou/current" in url:
            return MockResponse(200, {
                "data": [
                    {"currency": "USD", "buy": 42.50, "sell": 42.80},
                    {"currency": "EUR", "buy": 46.20, "sell": 46.50}
                ],
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            return MockResponse(404, {"error": "Endpoint not found"})


def demo_healthy_system():
    """Demo de sistema funcionando correctamente"""
    print("🟢 DEMO: Sistema funcionando correctamente")
    print("=" * 50)
    
    # Simular requests
    import sys
    sys.modules['requests'] = MockRequests()
    
    # Importar después de mockear requests
    from tunnel_monitor import TunnelMonitor, MonitoringConfig
    
    config = MonitoringConfig(
        api_url="http://localhost:8000/api",
        check_interval=0,  # Solo una ejecución
        max_data_age=30,
        max_retries=3,
        alert_webhook="",
        log_file="logs/demo_monitoring.log",
        enable_alerts=False,
        timeout=10
    )
    
    monitor = TunnelMonitor(config)
    
    print("🔍 Ejecutando verificaciones...")
    results = monitor.run_health_checks(config.api_url)
    
    print("\\n📊 Resultados:")
    for result in results:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "error": "💥"
        }.get(result.status, "❓")
        
        print(f"{status_icon} {result.endpoint}: {result.message}")
    
    all_passed = monitor.evaluate_results(results)
    print(f"\\n🎯 Resultado general: {'✅ PASÓ' if all_passed else '❌ FALLÓ'}")
    
    return all_passed


def demo_problematic_system():
    """Demo de sistema con problemas"""
    print("\\n🟡 DEMO: Sistema con problemas")
    print("=" * 50)
    
    # Crear mock personalizado para simular problemas
    class ProblematicMockRequests:
        @staticmethod
        def get(url: str, timeout: int = 10) -> MockResponse:
            if "/health/simple" in url:
                return MockResponse(200, {"status": "ok"})
            elif "/health" in url:
                return MockResponse(200, {
                    "overall_status": "warning",
                    "message": "Some services degraded",
                    "checks": {
                        "database": "healthy",
                        "cache": "warning",
                        "external_apis": "critical"
                    }
                })
            elif "/ui/latest" in url:
                # Simular datos antiguos (más de 30 minutos)
                data_date = datetime.now() - timedelta(minutes=45)
                return MockResponse(200, {
                    "data": {
                        "date": data_date.isoformat(),
                        "value": 45.67,
                        "source": "INE"
                    }
                })
            elif "/metrics" in url:
                return MockResponse(200, {
                    "ui_freshness": {
                        "ui_gap_detected": True,
                        "ui_latest_age_seconds": 2700
                    },
                    "cache_status": {
                        "brou_cache_age_seconds": 7200,  # 2 horas
                        "bcu_cache_age_seconds": 6900
                    },
                    "system": {
                        "memory_usage_percent": 92.5,  # Alto uso de memoria
                        "cpu_usage_percent": 85.3
                    }
                })
            else:
                return MockResponse(404, {"error": "Not found"})
    
    # Aplicar mock problemático
    sys.modules['requests'] = ProblematicMockRequests()
    
    from tunnel_monitor import TunnelMonitor, MonitoringConfig
    
    config = MonitoringConfig(
        api_url="http://localhost:8000/api",
        check_interval=0,
        max_data_age=30,
        max_retries=3,
        alert_webhook="",
        log_file="logs/demo_monitoring.log",
        enable_alerts=False,
        timeout=10
    )
    
    monitor = TunnelMonitor(config)
    
    print("🔍 Ejecutando verificaciones...")
    results = monitor.run_health_checks(config.api_url)
    
    print("\\n📊 Resultados:")
    for result in results:
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "error": "💥"
        }.get(result.status, "❓")
        
        print(f"{status_icon} {result.endpoint}: {result.message}")
    
    all_passed = monitor.evaluate_results(results)
    print(f"\\n🎯 Resultado general: {'✅ PASÓ' if all_passed else '❌ FALLÓ'}")
    
    return all_passed


def demo_alert_system():
    """Demo del sistema de alertas"""
    print("\\n🔔 DEMO: Sistema de alertas")
    print("=" * 50)
    
    print("📋 Simulando escenarios de alerta:")
    print()
    
    scenarios = [
        {
            "name": "Datos antiguos",
            "description": "Los datos UI tienen más de 30 minutos",
            "level": "WARNING"
        },
        {
            "name": "Gap en datos detectado",
            "description": "Se detectó un hueco en los datos UI",
            "level": "ERROR"
        },
        {
            "name": "Alto uso de memoria",
            "description": "El sistema está usando más del 90% de memoria",
            "level": "WARNING"
        },
        {
            "name": "API no disponible",
            "description": "La API no responde a las verificaciones",
            "level": "ERROR"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. 🚨 {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        print(f"   🏷️  Nivel: {scenario['level']}")
        print()
    
    print("💡 Para configurar alertas reales:")
    print("   1. Configura un webhook (Slack, Discord, Teams)")
    print("   2. Ejecuta: python3 tunnel_monitor.py --alert-webhook 'URL'")
    print("   3. El sistema enviará alertas automáticamente")


def demo_monitoring_loop():
    """Demo del loop de monitoreo continuo"""
    print("\\n🔄 DEMO: Monitoreo continuo")
    print("=" * 50)
    
    print("📊 Simulando 3 ciclos de monitoreo:")
    print()
    
    for cycle in range(1, 4):
        print(f"🔄 Ciclo {cycle}/3 - {datetime.now().strftime('%H:%M:%S')}")
        
        # Simular diferentes estados en cada ciclo
        if cycle == 1:
            print("   ✅ Todos los checks pasaron")
        elif cycle == 2:
            print("   ⚠️  Datos un poco antiguos (25 minutos)")
        else:
            print("   ❌ Datos muy antiguos (45 minutos) - ALERTA!")
        
        print("   ⏱️  Tiempo de verificación: 1.2s")
        print("   📈 Métricas: OK")
        print()
        
        if cycle < 3:
            print("   ⏳ Esperando 5 minutos hasta próximo ciclo...")
            time.sleep(2)  # Demo más rápido
            print()
    
    print("🎯 Resumen del monitoreo:")
    print("   • 3 ciclos ejecutados")
    print("   • 2 ciclos exitosos")
    print("   • 1 alerta generada")
    print("   • Tiempo promedio: 1.1s por ciclo")


def main():
    """Función principal del demo"""
    print("🎭 SIFU - Demo del Sistema de Monitoreo")
    print("=" * 60)
    print("Este demo simula el comportamiento del sistema de monitoreo")
    print("para demostrar sus capacidades sin necesidad del backend real.")
    print()
    
    try:
        # Demo 1: Sistema funcionando
        demo_healthy_system()
        
        # Demo 2: Sistema con problemas
        demo_problematic_system()
        
        # Demo 3: Sistema de alertas
        demo_alert_system()
        
        # Demo 4: Monitoreo continuo
        demo_monitoring_loop()
        
        print("\\n🎉 Demo completado!")
        print("\\n📋 Para usar el sistema real:")
        print("   1. Asegúrate de que el backend esté ejecutándose")
        print("   2. Ejecuta: python3 scripts/monitoring/quick_test.py")
        print("   3. Si funciona, ejecuta: python3 scripts/monitoring/tunnel_monitor.py")
        
    except Exception as e:
        print(f"\\n💥 Error en el demo: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️  Demo interrumpido por el usuario")
        sys.exit(1)
