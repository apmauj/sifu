#!/usr/bin/env python3
"""
Script de configuración de producción para SIFU
Genera configuración segura para entorno de producción
"""

import os
import secrets
import string
from pathlib import Path

def generate_secure_key(length=32):
    """Genera una clave segura aleatoria"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_password(length=32):
    """Genera una contraseña segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def setup_production_env():
    """Configura el entorno de producción con valores seguros"""
    print("🔐 Configurando entorno de producción para SIFU...")

    # Verificar que existe el template
    template_file = Path(".env.production.template")
    if not template_file.exists():
        print("❌ .env.production.template no encontrado")
        return False

    # Leer template
    with open(template_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Generar valores seguros
    replacements = {
        "CHANGE_THIS_STRONG_PASSWORD_32_CHARS_MIN": generate_secure_password(32),
        "CHANGE_THIS_TO_A_NEW_64_CHAR_RANDOM_SECRET_KEY_FOR_PRODUCTION_SECURITY": generate_secure_key(64),
        "CHANGE_THIS_TO_A_NEW_SECURE_API_KEY_FROM_VAULT_32_CHARS_MIN": generate_secure_key(32),
        "CHANGE_THIS_TO_A_NEW_32_CHAR_ENCRYPTION_KEY_VAULT_ONLY": generate_secure_key(32),
        "CHANGE_THIS_TO_A_NEW_64_CHAR_JWT_SECRET_FOR_PRODUCTION": generate_secure_key(64),
        "CHANGE_THIS_TO_A_NEW_32_CHAR_LOG_ENCRYPTION_KEY": generate_secure_key(32),
    }

    # Aplicar reemplazos
    for old_value, new_value in replacements.items():
        content = content.replace(old_value, new_value)

    # Crear archivo .env.production
    env_prod_file = Path(".env.production")
    with open(env_prod_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Archivo .env.production configurado con valores seguros")
    print("⚠️  IMPORTANTE: Revisa y personaliza los siguientes valores:")
    print("   - DATABASE_URL: Configura tu base de datos PostgreSQL")
    print("   - REDIS_URL: Configura tu servidor Redis")
    print("   - ALLOW_ORIGINS: Configura tus dominios de producción")
    print("   - SSL_CERT_PATH y SSL_KEY_PATH: Configura certificados SSL")
    print("   - ALERT_WEBHOOK_URL y ALERT_EMAIL: Configura alertas")

    return True

def validate_production_config():
    """Valida la configuración de producción"""
    print("\n🔍 Validando configuración de producción...")

    env_prod_file = Path(".env.production")
    if not env_prod_file.exists():
        print("❌ .env.production no encontrado")
        return False

    with open(env_prod_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar valores que deben ser cambiados
    warning_values = [
        "your-prod-db-host",
        "your-prod-redis-host",
        "your-sifu-prod-domain.com",
        "/path/to/ssl/",
        "your-alert-system.com",
        "alerts@yourdomain.com"
    ]

    warnings = []
    for value in warning_values:
        if value in content:
            warnings.append(value)

    if warnings:
        print("⚠️  Valores que necesitan configuración:")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print("✅ Todos los valores parecen estar configurados")

    return len(warnings) == 0

def main():
    """Función principal"""
    print("🚀 Configuración de Producción SIFU")
    print("=" * 50)

    # Configurar entorno
    if not setup_production_env():
        return 1

    # Validar configuración
    is_valid = validate_production_config()

    print("\n" + "=" * 50)
    if is_valid:
        print("✅ Configuración de producción completada exitosamente")
        print("📋 Próximos pasos:")
        print("   1. Revisa .env.production y configura valores específicos")
        print("   2. Configura tu base de datos PostgreSQL")
        print("   3. Configura Redis para cache")
        print("   4. Configura certificados SSL")
        print("   5. Prueba el deploy: pwsh -File .\\scripts\\deploy\\deploy_backend.ps1")
        return 0
    else:
        print("⚠️  Configuración completada pero requiere ajustes manuales")
        print("🔧 Revisa las advertencias arriba y configura los valores necesarios")
        return 1

if __name__ == "__main__":
    exit(main())
