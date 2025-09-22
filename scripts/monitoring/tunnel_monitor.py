#!/usr/bin/env python3
"""
Sistema de monitoreo programado para el túnel de SIFU
Funciona en Linux y Windows, con detección automática del entorno
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)


@dataclass
class MonitoringConfig:
    """Configuración del sistema de monitoreo"""
    api_url: str = ""
    check_interval: int = 5  # minutos
    max_data_age: int = 30  # minutos
    max_retries: int = 3
    alert_webhook: str = ""
    log_file: str = "tunnel_monitoring.log"
    enable_alerts: bool = False
    timeout: int = 10


@dataclass
class HealthCheckResult:
    """Resultado de una verificación de salud"""
    endpoint: str
    status: str  # healthy, warning, critical, error
    response_time: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class TunnelMonitor:
    """Monitor principal del túnel SIFU"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.consecutive_failures = 0
        self.last_successful_check = datetime.now()
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def detect_tunnel_url(self) -> Optional[str]:
        """Detectar URL del túnel automáticamente"""
        try:
            # Intentar con Docker si está disponible
            if self.is_docker_available():
                return self.detect_tunnel_from_docker()
            
            # Intentar con archivos de estado
            return self.detect_tunnel_from_files()
            
        except Exception as e:
            self.logger.error(f"Error detectando URL del túnel: {e}")
            return None
    
    def is_docker_available(self) -> bool:
        """Verificar si Docker está disponible"""
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def detect_tunnel_from_docker(self) -> Optional[str]:
        """Detectar URL del túnel desde logs de Docker"""
        try:
            result = subprocess.run(
                ['docker', 'logs', '--tail', '100', 'sifu-tunnel'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                import re
                pattern = r'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
                matches = re.findall(pattern, result.stdout)
                if matches:
                    return matches[-1]  # Última URL encontrada
                    
        except Exception as e:
            self.logger.debug(f"Error leyendo logs de Docker: {e}")
            
        return None
    
    def detect_tunnel_from_files(self) -> Optional[str]:
        """Detectar URL del túnel desde archivos de estado"""
        try:
            # Buscar archivo de estado del túnel
            state_files = [
                '.tunnel_last_url.txt',
                'tunnel_state.json',
                'logs/tunnel_state.log'
            ]
            
            for file_path in state_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read().strip()
                        if content.startswith('http'):
                            return content
                            
        except Exception as e:
            self.logger.debug(f"Error leyendo archivos de estado: {e}")
            
        return None
    
    def test_endpoint(self, url: str, description: str) -> HealthCheckResult:
        """Probar un endpoint específico"""
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=self.config.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthCheckResult(
                    endpoint=description,
                    status="healthy",
                    response_time=response_time,
                    message="OK",
                    details={"status_code": response.status_code},
                    timestamp=datetime.now()
                )
            else:
                return HealthCheckResult(
                    endpoint=description,
                    status="warning",
                    response_time=response_time,
                    message=f"HTTP {response.status_code}",
                    details={"status_code": response.status_code},
                    timestamp=datetime.now()
                )
                
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                endpoint=description,
                status="critical",
                response_time=self.config.timeout,
                message="Timeout",
                details={"error": "Request timeout"},
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                endpoint=description,
                status="error",
                response_time=time.time() - start_time,
                message=str(e),
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def check_api_health(self, base_url: str) -> HealthCheckResult:
        """Verificar salud de la API"""
        health_url = f"{base_url}/health"
        return self.test_endpoint(health_url, "API Health")
    
    def check_simple_health(self, base_url: str) -> HealthCheckResult:
        """Verificar salud simple de la API"""
        health_url = f"{base_url}/health/simple"
        return self.test_endpoint(health_url, "Simple Health")
    
    def check_data_freshness(self, base_url: str) -> HealthCheckResult:
        """Verificar frescura de los datos"""
        ui_url = f"{base_url}/ui/latest"
        
        try:
            response = requests.get(ui_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and data['data'].get('date'):
                    data_date = datetime.fromisoformat(data['data']['date'].replace('Z', '+00:00'))
                    age_minutes = (datetime.now() - data_date.replace(tzinfo=None)).total_seconds() / 60
                    
                    if age_minutes <= self.config.max_data_age:
                        return HealthCheckResult(
                            endpoint="Data Freshness",
                            status="healthy",
                            response_time=0,
                            message=f"Data is fresh ({age_minutes:.1f} minutes old)",
                            details={"age_minutes": age_minutes, "data_date": data['data']['date']},
                            timestamp=datetime.now()
                        )
                    else:
                        return HealthCheckResult(
                            endpoint="Data Freshness",
                            status="warning",
                            response_time=0,
                            message=f"Data is stale ({age_minutes:.1f} minutes old)",
                            details={"age_minutes": age_minutes, "data_date": data['data']['date']},
                            timestamp=datetime.now()
                        )
                else:
                    return HealthCheckResult(
                        endpoint="Data Freshness",
                        status="critical",
                        response_time=0,
                        message="No data available",
                        details={"error": "No data in response"},
                        timestamp=datetime.now()
                    )
            else:
                return HealthCheckResult(
                    endpoint="Data Freshness",
                    status="critical",
                    response_time=0,
                    message=f"HTTP {response.status_code}",
                    details={"status_code": response.status_code},
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return HealthCheckResult(
                endpoint="Data Freshness",
                status="error",
                response_time=0,
                message=str(e),
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def check_system_metrics(self, base_url: str) -> HealthCheckResult:
        """Verificar métricas del sistema"""
        metrics_url = f"{base_url}/metrics"
        
        try:
            response = requests.get(metrics_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                metrics = response.json()
                issues = []
                
                # Verificar métricas críticas
                if metrics.get('ui_freshness', {}).get('ui_gap_detected'):
                    issues.append("UI data gap detected")
                
                if metrics.get('cache_status', {}).get('brou_cache_age_seconds', 0) > 3600:
                    issues.append("BROU cache too old")
                
                if metrics.get('system', {}).get('memory_usage_percent', 0) > 90:
                    issues.append("High memory usage")
                
                if not issues:
                    return HealthCheckResult(
                        endpoint="System Metrics",
                        status="healthy",
                        response_time=0,
                        message="All metrics OK",
                        details=metrics,
                        timestamp=datetime.now()
                    )
                else:
                    return HealthCheckResult(
                        endpoint="System Metrics",
                        status="warning",
                        response_time=0,
                        message=f"Issues: {', '.join(issues)}",
                        details={"metrics": metrics, "issues": issues},
                        timestamp=datetime.now()
                    )
            else:
                return HealthCheckResult(
                    endpoint="System Metrics",
                    status="critical",
                    response_time=0,
                    message=f"HTTP {response.status_code}",
                    details={"status_code": response.status_code},
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return HealthCheckResult(
                endpoint="System Metrics",
                status="error",
                response_time=0,
                message=str(e),
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def send_alert(self, message: str, level: str = "ERROR", details: Dict[str, Any] = None):
        """Enviar alerta via webhook"""
        if not self.config.enable_alerts or not self.config.alert_webhook:
            self.logger.warning("Alerts not configured, skipping notification")
            return
        
        try:
            payload = {
                "text": f"🚨 **SIFU Tunnel Alert - {level}**",
                "attachments": [
                    {
                        "color": "danger" if level == "ERROR" else "warning",
                        "fields": [
                            {"title": "Message", "value": message, "short": False},
                            {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True},
                            {"title": "API URL", "value": self.config.api_url, "short": True}
                        ]
                    }
                ]
            }
            
            if details:
                payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": json.dumps(details, indent=2),
                    "short": False
                })
            
            response = requests.post(
                self.config.alert_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Alert sent successfully")
            else:
                self.logger.error(f"Failed to send alert: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    def run_health_checks(self, base_url: str) -> List[HealthCheckResult]:
        """Ejecutar todas las verificaciones de salud"""
        checks = [
            self.check_simple_health(base_url),
            self.check_api_health(base_url),
            self.check_data_freshness(base_url),
            self.check_system_metrics(base_url)
        ]
        
        return checks
    
    def evaluate_results(self, results: List[HealthCheckResult]) -> bool:
        """Evaluar resultados y determinar si hay problemas"""
        critical_issues = 0
        warnings = 0
        
        for result in results:
            self.logger.info(f"{result.endpoint}: {result.status.upper()} - {result.message}")
            
            if result.status in ["critical", "error"]:
                critical_issues += 1
            elif result.status == "warning":
                warnings += 1
        
        if critical_issues > 0:
            self.logger.error(f"Critical issues detected: {critical_issues}")
            return False
        elif warnings > 0:
            self.logger.warning(f"Warnings detected: {warnings}")
            return True  # Warnings no son críticos
        else:
            self.logger.info("All checks passed successfully")
            return True
    
    def monitor_loop(self):
        """Loop principal de monitoreo"""
        # Determinar URL de la API
        if not self.config.api_url:
            self.logger.info("Auto-detecting tunnel URL...")
            tunnel_url = self.detect_tunnel_url()
            
            if not tunnel_url:
                self.logger.error("Could not detect tunnel URL automatically")
                return False
            
            self.config.api_url = f"{tunnel_url}/api"
            self.logger.info(f"Detected tunnel URL: {tunnel_url}")
        
        self.logger.info(f"Starting monitoring loop for: {self.config.api_url}")
        self.logger.info(f"Check interval: {self.config.check_interval} minutes")
        self.logger.info(f"Max data age: {self.config.max_data_age} minutes")
        
        while True:
            check_start = datetime.now()
            self.logger.info("=== Starting health check cycle ===")
            
            try:
                # Ejecutar verificaciones
                results = self.run_health_checks(self.config.api_url)
                
                # Evaluar resultados
                all_passed = self.evaluate_results(results)
                
                if all_passed:
                    self.consecutive_failures = 0
                    self.last_successful_check = datetime.now()
                else:
                    self.consecutive_failures += 1
                    self.logger.error(f"Health checks failed (consecutive failures: {self.consecutive_failures})")
                    
                    # Enviar alerta si se supera el umbral
                    if self.consecutive_failures >= self.config.max_retries:
                        alert_message = f"SIFU tunnel has failed {self.consecutive_failures} consecutive health checks"
                        alert_details = {
                            "results": [asdict(r) for r in results],
                            "last_successful_check": self.last_successful_check.isoformat(),
                            "consecutive_failures": self.consecutive_failures
                        }
                        
                        self.send_alert(alert_message, "ERROR", alert_details)
                        
                        # Resetear contador después de enviar alerta
                        self.consecutive_failures = 0
                
                check_duration = datetime.now() - check_start
                self.logger.info(f"Health check cycle completed in {check_duration.total_seconds():.1f} seconds")
                
                # Si check_interval es 0, solo ejecutar una vez
                if self.config.check_interval == 0:
                    self.logger.info("Single execution mode, exiting")
                    break
                
                # Esperar antes del siguiente check
                self.logger.info(f"Waiting {self.config.check_interval} minutes until next check...")
                time.sleep(self.config.check_interval * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
        
        return True


def load_config(config_file: str = "monitoring_config.json") -> MonitoringConfig:
    """Cargar configuración desde archivo"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return MonitoringConfig(**data)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    return MonitoringConfig()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="SIFU Tunnel Monitoring System")
    parser.add_argument("--api-url", help="API URL (auto-detect if not provided)")
    parser.add_argument("--check-interval", type=int, default=5, help="Check interval in minutes (0 for single run)")
    parser.add_argument("--max-data-age", type=int, default=30, help="Max data age in minutes")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries before alerting")
    parser.add_argument("--alert-webhook", help="Webhook URL for alerts")
    parser.add_argument("--log-file", default="tunnel_monitoring.log", help="Log file path")
    parser.add_argument("--config", default="monitoring_config.json", help="Config file path")
    parser.add_argument("--single-run", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    # Cargar configuración
    config = load_config(args.config)
    
    # Aplicar argumentos de línea de comandos
    if args.api_url:
        config.api_url = args.api_url
    if args.check_interval is not None:
        config.check_interval = args.check_interval
    if args.max_data_age is not None:
        config.max_data_age = args.max_data_age
    if args.max_retries is not None:
        config.max_retries = args.max_retries
    if args.alert_webhook:
        config.alert_webhook = args.alert_webhook
        config.enable_alerts = True
    if args.log_file:
        config.log_file = args.log_file
    if args.single_run:
        config.check_interval = 0
    
    # Crear y ejecutar monitor
    monitor = TunnelMonitor(config)
    
    try:
        success = monitor.monitor_loop()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
