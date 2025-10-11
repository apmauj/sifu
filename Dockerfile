# Usar Python 3.11 slim como imagen base
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y certificados CA actualizados
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar todos los archivos de dependencias (requirements.txt incluye -r requirements-core.txt y -r requirements-excel.txt)
COPY requirements*.txt ./

# Instalar dependencias de Python y actualizar certifi para certificados SSL recientes
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade certifi

# Copiar código fuente
COPY *.py ./
COPY auth_*.py ./
COPY https_middleware.py ./
COPY performance_budget.py ./
COPY metrics.py ./
COPY alerts.py ./
COPY README.md ./

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Exponer el puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]