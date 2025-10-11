#!/usr/bin/env python3
"""
Prueba rápida de conectividad para el sistema SIFU
Verifica que los endpoints principales estén funcionando
"""

import requests
import time
import sys
from datetime import datetime


def test_endpoint(url, description, timeout=10):
    """Probar un endpoint específico"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ {description}: OK ({response_time:.2f}s)")
            return True, response.json() if 'application/json' in response.headers.get('content-type', '') else None
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False, None
    except requests.exceptions.Timeout:
        print(f"⏰ {description}: TIMEOUT ({timeout}s)")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"🔌 {description}: CONNECTION ERROR")
        return False, None
    except Exception as e:
        print(f"💥 {description}: ERROR - {str(e)}")
        return False, None


def main():
    """Función principal de prueba"""
    print("🧪 SIFU - Prueba Rápida de Conectividad")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs base para probar
    base_urls = [
        "http://localhost:8000",
        "https://localhost:8000",  # Por si hay HTTPS
    ]
    
    # Detectar URL del túnel automáticamente
    tunnel_url = None
    try:
        import subprocess
        result = subprocess.run(['docker', 'logs', '--tail', '50', 'sifu-tunnel'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            import re
            pattern = r'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
            matches = re.findall(pattern, result.stdout)
            if matches:
                tunnel_url = matches[-1]
                base_urls.append(tunnel_url)
                print(f"🌐 Túnel detectado: {tunnel_url}")
    except Exception:  # noqa: S110
        pass
    
    print()
    
    # Endpoints a probar
    endpoints = [
        ("/api/health/simple", "Health Check Simple"),
        ("/api/health", "Health Check Completo"),
        ("/api/ui/latest", "Datos UI Más Recientes"),
        ("/api/metrics", "Métricas del Sistema"),
        ("/api/brou/current", "Datos BROU Actuales"),
        ("/api/exchange/latest", "Datos Exchange Recientes"),
    ]
    
    total_tests = 0
    successful_tests = 0
    working_urls = []
    
    for base_url in base_urls:
        print(f"🔍 Probando: {base_url}")
        print("-" * 40)
        
        url_success = 0
        url_total = 0
        
        for endpoint, description in endpoints:
            url_total += 1
            total_tests += 1
            
            full_url = base_url + endpoint
            success, data = test_endpoint(full_url, description)
            
            if success:
                successful_tests += 1
                url_success += 1
                
                # Mostrar información adicional si está disponible
                if data and endpoint == "/api/health/simple":
                    print(f"   📊 Estado: {data.get('status', 'unknown')}")
                elif data and endpoint == "/api/ui/latest":
                    if data.get('data', {}).get('date'):
                        print(f"   📅 Fecha datos: {data['data']['date']}")
                elif data and endpoint == "/api/metrics":
                    if 'ui_freshness' in data:
                        gap_detected = data['ui_freshness'].get('ui_gap_detected', False)
                        print(f"   📈 Gap UI detectado: {'Sí' if gap_detected else 'No'}")
        
        print(f"📊 Resultados para {base_url}: {url_success}/{url_total}")
        
        if url_success > 0:
            working_urls.append(base_url)
        
        print()
    
    # Resumen final
    print("📋 RESUMEN FINAL")
    print("=" * 30)
    print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
    print(f"🌐 URLs funcionando: {len(working_urls)}")
    
    if working_urls:
        print("\\n🔗 URLs disponibles:")
        for url in working_urls:
            print(f"   • {url}")
        
        # Recomendar URL para monitoreo
        if tunnel_url:
            recommended_url = f"{tunnel_url}/api"
            print("\n💡 Recomendación para monitoreo:")
            print(f"   python3 scripts/monitoring/tunnel_monitor.py --api-url {recommended_url}")
        elif "http://localhost:8000" in working_urls:
            recommended_url = "http://localhost:8000/api"
            print("\n💡 Recomendación para monitoreo local:")
            print(f"   python3 scripts/monitoring/tunnel_monitor.py --api-url {recommended_url}")
    else:
        print("\\n❌ No se encontraron URLs funcionando")
        print("\\n🔧 Soluciones posibles:")
        print("   1. Verificar que el backend esté ejecutándose")
        print("   2. Verificar que Docker esté funcionando")
        print("   3. Verificar configuración de puertos")
        print("   4. Revisar logs del backend: docker logs sifu-backend")
    
    print()
    
    # Sugerir próximos pasos
    if successful_tests > 0:
        print("🎉 ¡Sistema funcionando! Próximos pasos:")
        print("   1. Configurar monitoreo: python3 scripts/monitoring/setup_monitoring.py")
        print("   2. Probar monitoreo: python3 scripts/monitoring/test_monitoring.py")
        print("   3. Ejecutar monitoreo continuo: python3 scripts/monitoring/tunnel_monitor.py")
    else:
        print("⚠️  Sistema no funcionando. Revisar configuración.")
    
    return successful_tests > 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️  Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Error crítico: {e}")
        sys.exit(1)
