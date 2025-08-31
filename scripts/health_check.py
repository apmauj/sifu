#!/usr/bin/env python3
"""
Script de verificación automática para el Plan de Acción SIFU
Ejecuta verificacion                    score = lighthouse_data.get('categories', {}).get('accessibility', {}).get('score', 0) * 100
                    self.results['UX-CHK-002'] = {
                        'status': 'PASS' if score >= 90 else 'WARN' if score >= 75 else 'FAIL',
                        'value': f"{score:.1f}",
                        'message': f'Lighthouse Accessibility: {score:.1f}/100'
                    }
                except Exception:
                    self.results['UX-CHK-002'] = {'status': 'ERROR', 'message': 'Error parseando Lighthouse'}atizadas del checklist y genera reporte
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

class SifuHealthChecker:
    def __init__(self):
        self.results = {}
        self.base_path = Path(__file__).parent.parent

    def run_command(self, cmd, shell=False):
        """Ejecuta un comando y retorna resultado"""
        try:
            result = subprocess.run(
                cmd if shell else cmd.split(),
                shell=shell,
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def check_security(self):
        """Verificaciones de seguridad"""
        print("🔒 Verificando Seguridad...")

        # SEC-CHK-001: Dependencias sin vulnerabilidades críticas
        success, stdout, stderr = self.run_command("pip-audit --format json")
        if success:
            try:
                audit_data = json.loads(stdout)
                vuln_count = len(audit_data.get('vulnerabilities', []))
                self.results['SEC-CHK-001'] = {
                    'status': 'PASS' if vuln_count == 0 else 'FAIL',
                    'value': vuln_count,
                    'message': f'{vuln_count} vulnerabilidades encontradas'
                }
            except Exception:
                self.results['SEC-CHK-001'] = {'status': 'ERROR', 'message': 'Error parseando pip-audit'}
        else:
            self.results['SEC-CHK-001'] = {'status': 'ERROR', 'message': stderr}

        # SEC-CHK-002: Validación de inputs
        success, stdout, stderr = self.run_command('grep -r "validate\|sanitize" --include="*.py" . | wc -l', shell=True)
        if success:
            count = int(stdout.strip())
            self.results['SEC-CHK-002'] = {
                'status': 'PASS' if count > 0 else 'FAIL',
                'value': count,
                'message': f'{count} funciones de validación encontradas'
            }

    def check_observability(self):
        """Verificaciones de observabilidad"""
        print("📊 Verificando Observabilidad...")

        # OBS-CHK-001: Health check endpoint
        success, stdout, stderr = self.run_command("curl -s http://localhost:8000/api/health")
        if success:
            try:
                health_data = json.loads(stdout)
                has_timestamp = 'timestamp' in health_data
                self.results['OBS-CHK-001'] = {
                    'status': 'PASS' if has_timestamp else 'FAIL',
                    'message': 'Health check con timestamp' if has_timestamp else 'Health check sin timestamp'
                }
            except Exception:
                self.results['OBS-CHK-001'] = {'status': 'ERROR', 'message': 'Error parseando health check'}
        else:
            self.results['OBS-CHK-001'] = {'status': 'FAIL', 'message': 'Health check no disponible'}

    def check_performance(self):
        """Verificaciones de performance"""
        print("⚡ Verificando Performance...")

        # PERF-CHK-002: Latencia del health check
        success, stdout, stderr = self.run_command("curl -s -w '%{time_total}' -o /dev/null http://localhost:8000/api/health")

        if success:
            try:
                latency = float(stdout.strip()) * 1000  # Convertir a ms
                self.results['PERF-CHK-002'] = {
                    'status': 'PASS' if latency < 500 else 'WARN' if latency < 1000 else 'FAIL',
                    'value': f"{latency:.2f}ms",
                    'message': f'Latencia: {latency:.2f}ms'
                }
            except Exception:
                self.results['PERF-CHK-002'] = {'status': 'ERROR', 'message': 'Error midiendo latencia'}
        else:
            self.results['PERF-CHK-002'] = {'status': 'FAIL', 'message': 'Endpoint no disponible'}

    def check_frontend(self):
        """Verificaciones del frontend"""
        print("🎨 Verificando Frontend...")

        # UX-CHK-002: Lighthouse check (si está disponible)
        success, stdout, stderr = self.run_command("which lighthouse")
        if success:
            # Asumiendo que el frontend está corriendo en localhost:3000
            success, stdout, stderr = self.run_command("lighthouse http://localhost:3000 --output json --quiet")
            if success:
                try:
                    lighthouse_data = json.loads(stdout)
                    score = lighthouse_data.get('categories', {}).get('accessibility', {}).get('score', 0) * 100
                    self.results['UX-CHK-002'] = {
                        'status': 'PASS' if score >= 90 else 'WARN' if score >= 75 else 'FAIL',
                        'value': f"{score:.1f}",
                        'message': f'Lighthouse Accessibility: {score:.1f}/100'
                    }
                except Exception:
                    self.results['UX-CHK-002'] = {'status': 'ERROR', 'message': 'Error parseando Lighthouse'}
            else:
                self.results['UX-CHK-002'] = {'status': 'SKIP', 'message': 'Lighthouse no ejecutado'}
        else:
            self.results['UX-CHK-002'] = {'status': 'SKIP', 'message': 'Lighthouse no instalado'}

    def generate_report(self):
        """Genera reporte de resultados"""
        print("\n" + "="*60)
        print("📋 REPORTE DE VERIFICACIÓN - SIFU")
        print("="*60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        status_counts = {'PASS': 0, 'FAIL': 0, 'WARN': 0, 'ERROR': 0, 'SKIP': 0}

        for check_id, result in self.results.items():
            status = result['status']
            status_counts[status] += 1

            emoji = {
                'PASS': '✅',
                'FAIL': '❌',
                'WARN': '⚠️',
                'ERROR': '🔥',
                'SKIP': '⏭️'
            }.get(status, '❓')

            print(f"{emoji} {check_id}: {result.get('message', '')}")

        print("\n" + "-"*60)
        print("📊 RESUMEN:")
        for status, count in status_counts.items():
            if count > 0:
                emoji = {
                    'PASS': '✅',
                    'FAIL': '❌',
                    'WARN': '⚠️',
                    'ERROR': '🔥',
                    'SKIP': '⏭️'
                }.get(status, '❓')
                print(f"  {emoji} {status}: {count}")

        # Calcular puntuación general
        total_checks = len(self.results)
        if total_checks > 0:
            score = (status_counts['PASS'] * 1.0 + status_counts['WARN'] * 0.5) / total_checks * 100
            print(f"  📊 Puntuación General: {score:.1f}%")
        print("="*60)

        # Guardar resultados en JSON
        report_file = self.base_path / "docs" / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results,
                'summary': status_counts
            }, f, indent=2)

        print(f"\n📄 Reporte guardado en: {report_file}")

    def run_all_checks(self):
        """Ejecuta todas las verificaciones"""
        print("🚀 Iniciando verificación automática de SIFU...")
        print(f"Directorio base: {self.base_path}")

        self.check_security()
        self.check_observability()
        self.check_performance()
        self.check_frontend()

        self.generate_report()

if __name__ == "__main__":
    checker = SifuHealthChecker()
    checker.run_all_checks()
