#!/usr/bin/env python3
"""
Workflow integrado de monitoreo y actualización de túnel SIFU
Combina la actualización automática del túnel con el monitoreo continuo
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.tunnel_monitor import TunnelMonitor, MonitoringConfig
except ImportError:
    print("Error: No se puede importar tunnel_monitor. Asegúrate de estar en el directorio correcto.")
    sys.exit(1)


class IntegratedWorkflow:
    """Workflow integrado de monitoreo y actualización"""
    
    def __init__(self, config_file: str = "config/integrated_workflow_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración del workflow integrado"""
        default_config = {
            "monitoring": {
                "check_interval": 5,  # minutos
                "max_data_age": 30,
                "max_retries": 3,
                "alert_webhook": "",
                "enable_alerts": False,
                "log_file": "logs/integrated_workflow.log"
            },
            "tunnel_update": {
                "auto_update": True,
                "update_interval": 60,  # minutos
                "image_tag": "latest",
                "trigger_deploy": False,
                "health_check_retries": 5,
                "health_check_interval": 10
            },
            "workflow": {
                "enable_monitoring": True,
                "enable_auto_update": True,
                "restart_on_failure": True,
                "max_restart_attempts": 3,
                "restart_delay": 300  # segundos
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge con configuración por defecto
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración: {e}. Usando configuración por defecto.")
        
        return default_config
    
    def setup_logging(self):
        """Configurar logging"""
        log_file = self.config["monitoring"]["log_file"]
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def save_config(self):
        """Guardar configuración actualizada"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    
    def detect_tunnel_url(self) -> Optional[str]:
        """Detectar URL del túnel automáticamente"""
        try:
            # Intentar con Docker si está disponible
            result = subprocess.run(['docker', 'logs', '--tail', '100', 'sifu-tunnel'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                import re
                pattern = r'https://[a-zA-Z0-9-]+\.trycloudflare\.com'
                matches = re.findall(pattern, result.stdout)
                if matches:
                    return matches[-1]
        except Exception as e:
            self.logger.debug(f"Error detectando URL del túnel: {e}")
        
        return None
    
    def update_tunnel(self) -> bool:
        """Actualizar túnel usando el script de PowerShell"""
        try:
            self.logger.info("Iniciando actualización del túnel...")
            
            # Construir comando PowerShell
            script_path = "scripts/deploy/automated_tunnel_update.ps1"
            if not os.path.exists(script_path):
                self.logger.error(f"Script de actualización no encontrado: {script_path}")
                return False
            
            # Ejecutar script de actualización
            cmd = [
                "powershell.exe", "-ExecutionPolicy", "Bypass", "-File", 
                script_path,
                "-ImageTag", self.config["tunnel_update"]["image_tag"]
            ]
            
            if self.config["tunnel_update"]["trigger_deploy"]:
                cmd.append("-TriggerDeploy")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("Túnel actualizado exitosamente")
                return True
            else:
                self.logger.error(f"Error actualizando túnel: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout actualizando túnel")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado actualizando túnel: {e}")
            return False
    
    def run_monitoring_cycle(self) -> bool:
        """Ejecutar un ciclo de monitoreo"""
        try:
            # Detectar URL del túnel
            tunnel_url = self.detect_tunnel_url()
            if not tunnel_url:
                self.logger.error("No se pudo detectar URL del túnel")
                return False
            
            api_url = f"{tunnel_url}/api"
            self.logger.info(f"Monitoreando: {api_url}")
            
            # Crear configuración de monitoreo
            monitoring_config = MonitoringConfig(
                api_url=api_url,
                check_interval=0,  # Solo una ejecución
                max_data_age=self.config["monitoring"]["max_data_age"],
                max_retries=self.config["monitoring"]["max_retries"],
                alert_webhook=self.config["monitoring"]["alert_webhook"],
                log_file=self.config["monitoring"]["log_file"],
                enable_alerts=self.config["monitoring"]["enable_alerts"],
                timeout=10
            )
            
            # Crear y ejecutar monitor
            monitor = TunnelMonitor(monitoring_config)
            results = monitor.run_health_checks(api_url)
            
            # Evaluar resultados
            all_passed = monitor.evaluate_results(results)
            
            if all_passed:
                self.logger.info("Ciclo de monitoreo exitoso")
                return True
            else:
                self.logger.warning("Ciclo de monitoreo detectó problemas")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en ciclo de monitoreo: {e}")
            return False
    
    def should_update_tunnel(self) -> bool:
        """Determinar si el túnel debe actualizarse"""
        if not self.config["tunnel_update"]["auto_update"]:
            return False
        
        # Verificar si ha pasado el tiempo de actualización
        update_interval = self.config["tunnel_update"]["update_interval"]
        last_update_file = "logs/last_tunnel_update.txt"
        
        if os.path.exists(last_update_file):
            try:
                with open(last_update_file, 'r') as f:
                    last_update_str = f.read().strip()
                    last_update = datetime.fromisoformat(last_update_str)
                    
                    if datetime.now() - last_update < timedelta(minutes=update_interval):
                        return False
            except Exception as e:
                self.logger.warning(f"Error leyendo último update: {e}")
        
        return True
    
    def record_tunnel_update(self):
        """Registrar la última actualización del túnel"""
        try:
            with open("logs/last_tunnel_update.txt", 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            self.logger.warning(f"Error registrando update: {e}")
    
    def run_workflow_cycle(self) -> bool:
        """Ejecutar un ciclo completo del workflow"""
        cycle_start = datetime.now()
        self.logger.info("=== Iniciando ciclo de workflow ===")
        
        success = True
        
        # 1. Verificar si necesita actualizar túnel
        if self.should_update_tunnel():
            self.logger.info("Actualización del túnel programada")
            if self.update_tunnel():
                self.record_tunnel_update()
            else:
                self.logger.error("Fallo en actualización del túnel")
                success = False
        
        # 2. Ejecutar monitoreo
        if self.config["workflow"]["enable_monitoring"]:
            if not self.run_monitoring_cycle():
                self.logger.warning("Problemas detectados en monitoreo")
                success = False
        
        cycle_duration = datetime.now() - cycle_start
        self.logger.info(f"Ciclo completado en {cycle_duration.total_seconds():.1f} segundos")
        
        return success
    
    def run_continuous_workflow(self):
        """Ejecutar workflow continuo"""
        self.logger.info("Iniciando workflow integrado continuo")
        
        check_interval = self.config["monitoring"]["check_interval"]
        consecutive_failures = 0
        max_restart_attempts = self.config["workflow"]["max_restart_attempts"]
        restart_delay = self.config["workflow"]["restart_delay"]
        
        while True:
            try:
                # Ejecutar ciclo de workflow
                cycle_success = self.run_workflow_cycle()
                
                if cycle_success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    
                    # Si hay demasiados fallos consecutivos, intentar reiniciar
                    if (consecutive_failures >= max_restart_attempts and 
                        self.config["workflow"]["restart_on_failure"]):
                        self.logger.error(f"Demasiados fallos consecutivos ({consecutive_failures}). Intentando reinicio...")
                        
                        # Intentar reiniciar servicios
                        if self.restart_services():
                            consecutive_failures = 0
                            self.logger.info("Servicios reiniciados exitosamente")
                        else:
                            self.logger.error("Fallo en reinicio de servicios")
                
                # Esperar hasta el próximo ciclo
                self.logger.info(f"Esperando {check_interval} minutos hasta próximo ciclo...")
                time.sleep(check_interval * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Workflow interrumpido por el usuario")
                break
            except Exception as e:
                self.logger.error(f"Error inesperado en workflow: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def restart_services(self) -> bool:
        """Reiniciar servicios Docker"""
        try:
            self.logger.info("Reiniciando servicios Docker...")
            
            # Reiniciar backend
            result = subprocess.run(['docker', 'compose', '-f', 'docker-compose.tunnel.yml', 'restart', 'backend'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.logger.error(f"Error reiniciando backend: {result.stderr}")
                return False
            
            # Reiniciar túnel
            result = subprocess.run(['docker', 'compose', '-f', 'docker-compose.tunnel.yml', 'restart', 'tunnel'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.logger.error(f"Error reiniciando túnel: {result.stderr}")
                return False
            
            # Esperar a que los servicios estén listos
            time.sleep(30)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error reiniciando servicios: {e}")
            return False
    
    def run_single_cycle(self) -> bool:
        """Ejecutar un solo ciclo del workflow"""
        return self.run_workflow_cycle()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="SIFU Integrated Workflow - Monitoreo y Actualización de Túnel")
    parser.add_argument("--config", default="config/integrated_workflow_config.json", help="Archivo de configuración")
    parser.add_argument("--single-cycle", action="store_true", help="Ejecutar solo un ciclo")
    parser.add_argument("--monitoring-only", action="store_true", help="Solo monitoreo, sin actualización")
    parser.add_argument("--update-only", action="store_true", help="Solo actualización, sin monitoreo")
    
    args = parser.parse_args()
    
    # Crear workflow
    workflow = IntegratedWorkflow(args.config)
    
    # Configurar modo de ejecución
    if args.monitoring_only:
        workflow.config["workflow"]["enable_auto_update"] = False
    elif args.update_only:
        workflow.config["workflow"]["enable_monitoring"] = False
    
    try:
        if args.single_cycle:
            success = workflow.run_single_cycle()
            sys.exit(0 if success else 1)
        else:
            workflow.run_continuous_workflow()
            
    except KeyboardInterrupt:
        print("\\n⏹️  Workflow interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\\n💥 Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
