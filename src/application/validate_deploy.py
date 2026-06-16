#!/usr/bin/env python3
"""
Deploy validation script for SIFU
Verifies that all security and configuration settings are correct before deploy.
Updated: removed secret_manager and Docker references, adapted for Render deployment.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Ejecuta un comando y retorna (success, output, error)"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ejecutando comando"
    except Exception as e:
        return False, "", str(e)


def validate_environment():
    """Valida que el entorno este correctamente configurado"""
    print("Validando entorno de deploy...")

    # Verificar archivos criticos para Render
    required_files = [
        "requirements.txt",
        "runtime.txt",
        "main.py",
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"  FAILED - Archivos faltantes: {', '.join(missing_files)}")
        return False

    # Verificar render.yaml (opcional pero recomendado)
    if not Path("render.yaml").exists():
        print("  WARNING - render.yaml no encontrado (opcional pero recomendado)")

    print("  PASSED - Archivos criticos presentes")
    return True


def validate_secrets():
    """Valida la configuracion de variables de entorno criticas"""
    print("Validando variables de entorno...")

    critical_vars = ["SECRET_KEY", "API_KEY", "DATABASE_URL"]
    recommended_vars = ["MONITORING_TOTP_SECRET", "ALLOW_ORIGINS", "ENVIRONMENT"]

    missing_critical = []
    for var in critical_vars:
        if not os.getenv(var):
            missing_critical.append(var)

    if missing_critical:
        print(f"  FAILED - Variables criticas faltantes: {', '.join(missing_critical)}")
        return False

    missing_recommended = []
    for var in recommended_vars:
        if not os.getenv(var):
            missing_recommended.append(var)

    if missing_recommended:
        print(f"  WARNING - Variables recomendadas no configuradas: {', '.join(missing_recommended)}")
        if "MONITORING_TOTP_SECRET" in missing_recommended:
            print("    MONITORING_TOTP_SECRET: Sin esta variable, el dashboard de monitoreo")
            print("    genera un secreto nuevo en cada reinicio, invalidando tu authenticator app.")

    print("  PASSED - Variables criticas configuradas")
    return True


def read_requirements_recursive(filename):
    """Lee requirements.txt recursivamente incluyendo archivos con -r"""
    requirements = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("-r "):
                    ref_file = line[3:].strip()
                    requirements.extend(read_requirements_recursive(ref_file))
                elif line and not line.startswith("#"):
                    package_name = (
                        line.split()[0]
                        .split("==")[0]
                        .split(">=")[0]
                        .split("<=")[0]
                        .split("!=")[0]
                        .split("[")[0]
                    )
                    requirements.append(package_name)
    except FileNotFoundError:
        pass
    return requirements


def validate_dependencies():
    """Valida que las dependencias criticas esten instaladas"""
    print("Validando dependencias...")

    all_requirements = read_requirements_recursive("requirements.txt")

    critical_deps = ["python-dotenv", "fastapi", "uvicorn", "pyotp"]
    missing_deps = []

    for dep in critical_deps:
        if dep not in all_requirements:
            missing_deps.append(dep)

    if missing_deps:
        print(f"  FAILED - Dependencias faltantes: {', '.join(missing_deps)}")
        return False

    print("  PASSED - Dependencias criticas presentes")
    return True


def validate_build():
    """Valida que el proyecto se pueda construir"""
    print("Validando construccion del proyecto...")

    success, stdout, stderr = run_command(
        "python -c \"import main; print('Import OK')\""
    )
    if not success:
        print(f"  FAILED - Error importando modulo principal: {stderr}")
        return False

    print("  PASSED - Proyecto se puede importar correctamente")
    return True


def main():
    """Funcion principal de validacion"""
    print("Iniciando validacion de deploy para SIFU\n")

    validations = [
        ("Entorno", validate_environment),
        ("Variables de entorno", validate_secrets),
        ("Dependencias", validate_dependencies),
        ("Build", validate_build),
    ]

    all_passed = True
    for name, validator in validations:
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"  FAILED - Error en validacion {name}: {e}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("Todas las validaciones pasaron exitosamente")
        print("El proyecto esta listo para deploy")
        return 0
    else:
        print("Algunas validaciones fallaron")
        print("Corrija los problemas antes del deploy")
        return 1


if __name__ == "__main__":
    sys.exit(main())
