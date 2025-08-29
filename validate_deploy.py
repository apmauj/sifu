#!/usr/bin/env python3
"""
Script de validación de deploy para SIFU
Verifica que todas las configuraciones de seguridad estén correctas antes del deploy
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Ejecuta un comando y retorna (success, output, error)"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ejecutando comando"
    except Exception as e:
        return False, "", str(e)

def validate_environment():
    """Valida que el entorno esté correctamente configurado"""
    print("🔍 Validando entorno de deploy...")

    # Verificar archivos críticos
    required_files = [
        ".env",
        "requirements.txt",
        "secret_manager.py",
        "docker-compose.yml",
        ".dockerignore"
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False

    print("✅ Archivos críticos presentes")
    return True

def validate_secrets():
    """Valida la configuración de secrets"""
    print("🔐 Validando configuración de secrets...")

    # Verificar que secret_manager.py existe y funciona
    if not Path("secret_manager.py").exists():
        print("❌ secret_manager.py no encontrado")
        return False

    success, stdout, stderr = run_command("python secret_manager.py --validate")
    if not success:
        print(f"❌ Error en validación de secrets: {stderr}")
        return False

    print("✅ Secrets configurados correctamente")
    return True

def read_requirements_recursive(filename):
    """Lee requirements.txt recursivamente incluyendo archivos con -r"""
    requirements = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("-r "):
                    # Incluir archivo referenciado
                    ref_file = line[3:].strip()
                    requirements.extend(read_requirements_recursive(ref_file))
                elif line and not line.startswith("#"):
                    # Extraer nombre del paquete (antes de ==, >=, etc. o [extras])
                    package_name = line.split()[0].split("==")[0].split(">=")[0].split("<=")[0].split("!=")[0].split("[")[0]
                    requirements.append(package_name)
    except FileNotFoundError:
        pass
    return requirements

def validate_dependencies():
    """Valida que las dependencias críticas estén instaladas"""
    print("📦 Validando dependencias...")

    # Leer requirements recursivamente
    all_requirements = read_requirements_recursive("requirements.txt")

    critical_deps = ["python-dotenv", "fastapi", "uvicorn"]
    missing_deps = []

    for dep in critical_deps:
        if dep not in all_requirements:
            missing_deps.append(dep)

    if missing_deps:
        print(f"❌ Dependencias faltantes: {', '.join(missing_deps)}")
        return False

    # Verificar cryptography (opcional pero recomendado)
    if "cryptography" not in all_requirements:
        print("⚠️  cryptography no está en requirements - logging seguro limitado")

    print("✅ Dependencias críticas presentes")
    return True

def validate_docker():
    """Valida la configuración de Docker"""
    print("🐳 Validando configuración Docker...")

    # Verificar que docker-compose.yml use .env
    with open("docker-compose.yml", "r") as f:
        compose_content = f.read()

    if "env_file:" not in compose_content:
        print("❌ docker-compose.yml no está configurado para usar .env file")
        return False

    # Verificar .dockerignore
    if not Path(".dockerignore").exists():
        print("❌ .dockerignore no encontrado")
        return False

    with open(".dockerignore", "r") as f:
        dockerignore = f.read()

    sensitive_files = [".env", "__pycache__", "*.pyc"]
    missing_ignores = []

    for file in sensitive_files:
        if file not in dockerignore:
            missing_ignores.append(file)

    if missing_ignores:
        print(f"⚠️  .dockerignore podría no excluir: {', '.join(missing_ignores)}")

    print("✅ Configuración Docker validada")
    return True

def validate_build():
    """Valida que el proyecto se pueda construir"""
    print("🔨 Validando construcción del proyecto...")

    # Verificar que se puede importar el módulo principal
    success, stdout, stderr = run_command("python -c \"import main; print('Import OK')\"")
    if not success:
        print(f"❌ Error importando módulo principal: {stderr}")
        return False

    print("✅ Proyecto se puede importar correctamente")
    return True

def main():
    """Función principal de validación"""
    print("🚀 Iniciando validación de deploy para SIFU\n")

    validations = [
        ("Entorno", validate_environment),
        ("Secrets", validate_secrets),
        ("Dependencias", validate_dependencies),
        ("Docker", validate_docker),
        ("Build", validate_build)
    ]

    all_passed = True
    for name, validator in validations:
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ Error en validación {name}: {e}")
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("✅ Todas las validaciones pasaron exitosamente")
        print("🚀 El proyecto está listo para deploy")
        return 0
    else:
        print("❌ Algunas validaciones fallaron")
        print("🔧 Corrija los problemas antes del deploy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
