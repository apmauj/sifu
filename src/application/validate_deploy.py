#!/usr/bin/env python3
"""
Script de validación de deploy para SIFU
Verifica que todas las configuraciones estén correctas antes del deploy en Render
"""

import sys
import os
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
    """Valida que el entorno esté correctamente configurado"""
    print("🔍 Validando entorno de deploy...")

    # Verificar archivos críticos para Render
    required_files = [
        "requirements.txt",
        "render.yaml",
        "runtime.txt",
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False

    # Verificar runtime.txt tiene formato correcto (solo versión, sin prefijo python-)
    if Path("runtime.txt").exists():
        content = Path("runtime.txt").read_text().strip()
        if content.startswith("python-"):
            print(f"❌ runtime.txt tiene formato Heroku ('{content}'). Usar solo la versión (ej: '3.12.4')")
            return False

    print("✅ Archivos críticos presentes")
    return True


def validate_env_vars():
    """Valida que las variables de entorno críticas estén definidas"""
    print("🔐 Validando variables de entorno...")

    # Env vars que deberían estar configuradas en Render Dashboard
    critical_vars = ["ALLOW_ORIGINS"]
    recommended_vars = ["PYTHON_VERSION"]

    missing_critical = []
    for var in critical_vars:
        if not os.environ.get(var):
            missing_critical.append(var)

    if missing_critical:
        print(f"⚠️  Variables críticas no definidas en entorno: {', '.join(missing_critical)}")
        print("   Configúralas en Render Dashboard → Environment")
        # No fallar — en CI estas vars no están, solo importan en Render

    missing_recommended = []
    for var in recommended_vars:
        if not os.environ.get(var):
            missing_recommended.append(var)

    if missing_recommended:
        print(f"💡 Variables recomendadas no definidas: {', '.join(missing_recommended)}")

    if not missing_critical:
        print("✅ Variables de entorno críticas presentes")
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


def validate_build():
    """Valida que el proyecto se pueda construir"""
    print("🔨 Validando construcción del proyecto...")

    # Verificar que se puede importar el módulo principal
    success, stdout, stderr = run_command(
        "python -c \"import main; print('Import OK')\""
    )
    if not success:
        print(f"❌ Error importando módulo principal: {stderr}")
        return False

    print("✅ Proyecto se puede importar correctamente")
    return True


def main():
    """Función principal de validación"""
    print("🚀 Iniciando validación de deploy para SIFU (Render)\n")

    validations = [
        ("Entorno", validate_environment),
        ("Env Vars", validate_env_vars),
        ("Dependencias", validate_dependencies),
        ("Build", validate_build),
    ]

    all_passed = True
    for name, validator in validations:
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ Error en validación {name}: {e}")
            all_passed = False

    print("\n" + "=" * 50)
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
    