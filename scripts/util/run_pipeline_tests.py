#!/usr/bin/env python3
"""
Script para ejecutar tests de manera que evite problemas de aislamiento
"""

import subprocess
import sys
from pathlib import Path


def run_tests_isolated():
    """Ejecuta los tests en lotes para evitar problemas de aislamiento"""

    # Script moved under scripts/util; run commands from repo root.
    project_dir = Path(__file__).resolve().parents[2]

    print("🧪 Ejecutando tests de SIFU con aislamiento...")

    # Tests que pueden tener problemas de aislamiento
    isolated_tests = ["tests/test_integration_api.py"]

    # Todos los demás tests
    regular_tests = [
        "async_test.py",
        "test_brou_monitoring.py",
        "test_circuit_breaker.py",
        "test_health_checks.py",
        "test_server.py",
        "test_ur.py",
        "tests/test_api.py",
        "tests/test_api_simple.py",
        "tests/test_bcu_url_fix.py",
        "tests/test_bootstrap.py",
        "tests/test_cache_endpoints.py",
        "tests/test_excel_processor_comprehensive.py",
        "tests/test_main_coverage.py",
        "tests/test_main_edge_cases.py",
        "tests/test_models.py",
        "tests/test_services.py",
        "tests/test_services_edge_cases.py",
        "tests/test_ur_api.py",
        "tests/test_ur_services.py",
    ]

    # Ejecutar tests regulares primero
    print("\n📋 Ejecutando tests regulares...")
    cmd_regular = [
        sys.executable,
        "-m",
        "pytest",
        "--tb=short",
        "-x",  # Detener al primer fallo
    ] + regular_tests

    result_regular = subprocess.run(
        cmd_regular, cwd=project_dir, capture_output=True, text=True
    )

    if result_regular.returncode != 0:
        print("❌ Fallaron los tests regulares:")
        print(result_regular.stdout)
        print(result_regular.stderr)
        return False

    print("✅ Tests regulares pasaron")

    # Ejecutar tests aislados en procesos separados
    print("\n🔒 Ejecutando tests de integración (aislados)...")
    for test_file in isolated_tests:
        print(f"   Ejecutando {test_file}...")
        cmd_isolated = [sys.executable, "-m", "pytest", test_file, "--tb=short", "-v"]

        result_isolated = subprocess.run(
            cmd_isolated, cwd=project_dir, capture_output=True, text=True
        )

        if result_isolated.returncode != 0:
            print(f"❌ Falló {test_file}:")
            print(result_isolated.stdout)
            print(result_isolated.stderr)
            return False

        print(f"✅ {test_file} pasó")

    print("\n🎉 Todos los tests pasaron exitosamente!")
    return True


def run_linting():
    """Ejecuta verificación de linting"""
    print("\n🔍 Ejecutando verificación de linting...")

    project_dir = Path(__file__).resolve().parents[2]
    cmd_lint = [sys.executable, "-m", "ruff", "check", ".", "--output-format=concise"]

    result_lint = subprocess.run(
        cmd_lint, cwd=project_dir, capture_output=True, text=True
    )

    if result_lint.returncode != 0:
        print("❌ Errores de linting encontrados:")
        print(result_lint.stdout)
        return False

    print("✅ Linting pasó")
    return True


if __name__ == "__main__":
    print("🚀 Iniciando verificación completa de SIFU...")

    # Verificar linting primero
    if not run_linting():
        sys.exit(1)

    # Ejecutar tests
    if not run_tests_isolated():
        sys.exit(1)

    print("\n✅ Verificación completa exitosa!")
    print("🎯 El pipeline está listo para producción.")
