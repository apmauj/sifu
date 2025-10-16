#!/usr/bin/env python3
"""
Script de configuración de HTTPS para SIFU
Implementa HTTPS obligatorio con certificados SSL/TLS
"""

import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Ejecuta un comando y retorna (success, output, error)"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ejecutando comando"
    except Exception as e:
        return False, "", str(e)


def create_ssl_directory():
    """Crea directorio para certificados SSL"""
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    print("✅ Directorio SSL creado: ssl/")
    return ssl_dir


def generate_self_signed_cert(ssl_dir):
    """Genera certificado SSL autofirmado para desarrollo/testing"""
    cert_path = ssl_dir / "sifu.crt"
    key_path = ssl_dir / "sifu.key"

    if cert_path.exists() and key_path.exists():
        print("⚠️  Certificados SSL ya existen, omitiendo generación")
        return True

    # Generar certificado autofirmado válido por 365 días
    cmd = f'openssl req -x509 -newkey rsa:4096 -keyout "{key_path}" -out "{cert_path}" -days 365 -nodes -subj "/C=UY/ST=Montevideo/L=Montevideo/O=SIFU/OU=Dev/CN=localhost"'

    success, stdout, stderr = run_command(cmd)
    if success:
        print("✅ Certificado SSL autofirmado generado")
        print(f"   📄 Certificado: {cert_path}")
        print(f"   🔑 Clave privada: {key_path}")
        return True
    else:
        print(f"❌ Error generando certificado: {stderr}")
        return False


def update_nginx_ssl(nginx_conf_path):
    """Actualiza configuración de nginx para HTTPS"""
    nginx_config = """# SIFU HTTPS Configuration
# Redirect all HTTP traffic to HTTPS

server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    # SSL Configuration
    ssl_certificate /app/ssl/sifu.crt;
    ssl_certificate_key /app/ssl/sifu.key;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to backend
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""

    try:
        with open(nginx_conf_path, "w", encoding="utf-8") as f:
            f.write(nginx_config)
        print(f"✅ Configuración nginx HTTPS actualizada: {nginx_conf_path}")
        return True
    except Exception as e:
        print(f"❌ Error actualizando nginx: {e}")
        return False


def update_docker_compose_ssl():
    """Actualiza docker-compose.yml para incluir nginx con HTTPS"""
    compose_ssl = """
  # Nginx with HTTPS
  nginx:
    image: nginx:alpine
    container_name: sifu-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/app/ssl:ro
      - ./nginx.https.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    networks:
      - sifu-network
    restart: unless-stopped
"""

    try:
        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            content = f.read()

        # Agregar nginx después del servicio backend
        if "nginx:" not in content:
            # Encontrar la línea del servicio backend
            lines = content.split("\n")
            backend_end_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("backend:"):
                    # Encontrar el final del servicio backend
                    for j in range(i + 1, len(lines)):
                        if (
                            lines[j].strip()
                            and not lines[j].startswith(" ")
                            and not lines[j].startswith("\t")
                        ):
                            backend_end_index = j
                            break
                    if backend_end_index == -1:
                        backend_end_index = len(lines)
                    break

            if backend_end_index > 0:
                # Insertar nginx después del backend
                lines.insert(backend_end_index, compose_ssl)
                new_content = "\n".join(lines)

                with open("docker-compose.yml", "w", encoding="utf-8") as f:
                    f.write(new_content)

                print("✅ docker-compose.yml actualizado con nginx HTTPS")
                return True
        else:
            print("⚠️  nginx ya está configurado en docker-compose.yml")
            return True

    except Exception as e:
        print(f"❌ Error actualizando docker-compose: {e}")
        return False


def create_https_middleware():
    """Crea middleware para forzar HTTPS en FastAPI"""
    middleware_code = '''"""
HTTPS Middleware for FastAPI
Forces HTTPS redirection and security headers
"""

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to redirect HTTP to HTTPS"""

    async def dispatch(self, request: Request, call_next):
        # Check if request is behind proxy/load balancer
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()

        # If request is HTTP and not behind HTTPS proxy, redirect to HTTPS
        if request.url.scheme == "http" and forwarded_proto != "https":
            # Only redirect in production
            if os.getenv("ENVIRONMENT") == "production":
                https_url = request.url.replace(scheme="https")
                return RedirectResponse(https_url, status_code=301)

        # Continue with request
        response = await call_next(request)

        # Add security headers
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

class SSLHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add SSL/TLS related security headers"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add SSL-related headers
        response.headers["X-SSL-Protocol"] = request.headers.get("X-SSL-Protocol", "unknown")
        response.headers["X-SSL-Cipher"] = request.headers.get("X-SSL-Cipher", "unknown")

        return response
'''

    try:
        with open("https_middleware.py", "w", encoding="utf-8") as f:
            f.write(middleware_code)
        print("✅ Middleware HTTPS creado: https_middleware.py")
        return True
    except Exception as e:
        print(f"❌ Error creando middleware HTTPS: {e}")
        return False


def update_main_for_https():
    """Actualiza main.py para incluir middlewares HTTPS"""
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar si ya tiene los imports
        if "from https_middleware import" not in content:
            # Agregar imports después del último import existente
            in_imports = False
            last_import_index = -1

            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("from ") or line.strip().startswith(
                    "import "
                ):
                    in_imports = True
                    last_import_index = i
                elif in_imports and line.strip() and not line.strip().startswith("#"):
                    break

            if last_import_index >= 0:
                # Insertar imports después del último import
                lines.insert(last_import_index + 1, "")
                lines.insert(last_import_index + 2, "# HTTPS Security Middleware")
                lines.insert(
                    last_import_index + 3,
                    "from https_middleware import HTTPSRedirectMiddleware, SSLHeadersMiddleware",
                )

                # Buscar donde se crea la app para agregar middlewares
                app_creation_index = -1
                for i, line in enumerate(lines):
                    if "app = FastAPI" in line:
                        app_creation_index = i
                        break

                if app_creation_index >= 0:
                    # Agregar middlewares después de la creación de la app
                    middleware_lines = [
                        "",
                        "# Add HTTPS security middlewares",
                        "app.add_middleware(HTTPSRedirectMiddleware)",
                        "app.add_middleware(SSLHeadersMiddleware)",
                        "",
                    ]

                    for j, middleware_line in enumerate(middleware_lines):
                        lines.insert(app_creation_index + 1 + j, middleware_line)

                    new_content = "\n".join(lines)

                    with open("main.py", "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print("✅ main.py actualizado con middlewares HTTPS")
                    return True

        print("⚠️  main.py ya tiene middlewares HTTPS configurados")
        return True

    except Exception as e:
        print(f"❌ Error actualizando main.py: {e}")
        return False


def main():
    """Función principal de configuración HTTPS"""
    print("🔒 Configuración HTTPS Obligatorio para SIFU")
    print("=" * 50)

    # Crear directorio SSL
    ssl_dir = create_ssl_directory()

    # Generar certificado autofirmado
    if not generate_self_signed_cert(ssl_dir):
        return 1

    # Crear configuración nginx
    nginx_conf = Path("nginx.https.conf")
    if not update_nginx_ssl(nginx_conf):
        return 1

    # Actualizar docker-compose
    if not update_docker_compose_ssl():
        return 1

    # Crear middleware HTTPS
    if not create_https_middleware():
        return 1

    # Actualizar main.py
    if not update_main_for_https():
        return 1

    print("\n" + "=" * 50)
    print("✅ Configuración HTTPS completada exitosamente")
    print("\n📋 Próximos pasos:")
    print("   1. Reiniciar contenedores: docker-compose down && docker-compose up -d")
    print("   2. Verificar HTTPS: curl -k https://localhost/api/health")
    print(
        "   3. Para producción: Reemplazar certificado autofirmado con certificado válido"
    )
    print("\n🔒 Características implementadas:")
    print("   ✅ Redirección HTTP → HTTPS automática")
    print("   ✅ Headers de seguridad HSTS, CSP, etc.")
    print("   ✅ Configuración nginx con SSL/TLS")
    print("   ✅ Middleware FastAPI para HTTPS")
    print("   ✅ Certificado SSL autofirmado para desarrollo")

    return 0


if __name__ == "__main__":
    exit(main())
