# SIFU - Sistema de Índices Financieros del Uruguay

[![Deploy Frontend](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/deploy-frontend.yml)
[![Backend CI](https://github.com/apmauj/sifu/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/ci-backend.yml)
[![Publish Backend Image](https://github.com/apmauj/sifu/actions/workflows/publish-backend-image.yml/badge.svg)](https://github.com/apmauj/sifu/actions/workflows/publish-backend-image.yml)

Sistema web para consulta de índices financieros y tasas de cambio en Uruguay.

## 🚀 Características

- **Backend**: FastAPI con Python
- **Frontend**: React con Vite
- **Base de Datos**: PostgreSQL
- **Contenedores**: Docker y Docker Compose
- **Internacionalización**: Soporte multiidioma (ES, EN, PT)

## 📋 Prerrequisitos

- Docker y Docker Compose
- Node.js 24+ (para desarrollo local y alineación con GitHub Actions)
- Python 3.11+ (para desarrollo local)

## 🛠️ Instalación y Uso

### Con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd sifu

# Iniciar todos los servicios
docker-compose up -d

# Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Gateway: http://localhost:8080
```

### Desarrollo Local (Windows)

```powershell
# Backend (raíz del repo)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

### Probar el build de Pages en local

Para reproducir GitHub Pages (base "/sifu/") en local:

```powershell
npm --prefix frontend run build
npm --prefix frontend exec npx serve -s dist -l 5174
# Abrir: http://localhost:5174/sifu/
```

## 📁 Estructura del Proyecto

```text
.
├── main.py              # FastAPI app (endpoints + lifespan)
├── services.py          # Lógica de negocio UI/UR/Exchange/BROU
├── models.py            # Pydantic / ORM models
├── brou_processor.py    # Scraper/processor BROU
├── excel_processor.py   # Procesamiento Excel (UI/UR)
├── database.py          # Conexión y helpers DB
├── constants.py         # Mensajes y tags centralizados
├── requirements.txt     # Dependencias
├── docker-compose.yml   # Stack principal
├── frontend/            # React (Vite)
└── docs/                # Documentación adicional
```

## 🌐 Endpoints API (Resumen)

Ver documentación interactiva en `/docs`.

### Principales:
- `GET /api/ui/latest` – Última UI
- `GET /api/ur/latest` – Última UR
- `GET /api/brou/current` – Cotizaciones actuales BROU (lista simple por defecto). `?full=true` añade `{ message, timestamp }`.
- `GET /api/exchange-rate/current` – Panel tiempo real BCU/INE
- `GET /api/exchange-rate/history` – Históricos por moneda/rango
- `POST /api/refresh/*` – Forzar actualización (UI, UR, exchange)

### Monitoreo (protegido con 2FA):
- `POST /api/monitoring/verify` – Verificar código TOTP de 6 dígitos
- `GET /api/monitoring/status` – Dashboard de monitoreo (requiere sesión)
- `GET /api/monitoring/setup` – Generar QR para configurar autenticador (solo development)
- `GET /api/monitoring/health` – Estado de autenticación actual
- `GET /api/monitoring/metrics` – Métricas de autenticación (intentos, éxitos, fallos por IP)
- `DELETE /api/monitoring/session` – Cerrar sesión

**Notas BROU:**
- Siempre retorna lista si no se pide `full` (retro‑compatible).
- Campo `preferential` marca `USD_EBROU` cuando existe.
- Fallback automático con datos de muestra si la fuente real falla (evita lista vacía).

## 🔐 Autenticación 2FA (TOTP)

El acceso al dashboard de monitoreo está protegido con autenticación de dos factores (TOTP).

### Setup Rápido:

1. **En Development:**
   ```bash
   # Acceder a la página de setup
   http://localhost:8000/static/totp-setup.html
   
   # Escanear el QR code con tu app de autenticación
   # (Google Authenticator, Authy, etc.)
   ```

2. **Configurar secret en `.env`:**
   ```bash
   MONITORING_TOTP_SECRET=tu-secret-aqui
   ENVIRONMENT=development  # 'production' en prod
   ```

3. **Acceder al dashboard:**
   - Hacer click en el **❤️** del footer del sitio
   - Ingresar código de 6 dígitos de tu app de autenticación
   - Sesión válida por 1 hora

### Features Incluidas:

- ✅ **Auditoría completa:** Todos los intentos de autenticación se registran en `logs/totp_audit.log`
- ✅ **Métricas en tiempo real:** `/api/monitoring/metrics` expone estadísticas de éxito/fallo
- ✅ **Detección de ataques:** Trackeo de intentos fallidos por IP
- ✅ **Tests comprehensivos:** 20 tests backend + 40 tests frontend
- ✅ **i18n completo:** Soporte para ES/EN/PT
- ✅ **Sesiones temporales:** 1 hora de duración (configurable)

### Documentación Completa:

Ver **[TOTP_SETUP.md](TOTP_SETUP.md)** para:
- Instrucciones detalladas de configuración
- Setup en producción
- Configuración de Authy/Google Authenticator
- Troubleshooting
- Regeneración de secrets

**Características:**
- ✅ Códigos TOTP de 6 dígitos (cambian cada 30 segundos)
- ✅ Sesiones de 1 hora (configurable)
- ✅ Endpoint de setup desactivado automáticamente en producción
- ✅ Rate limiting integrado
- ✅ Sin base de datos de usuarios (simplificado para admin único)

## 🔧 Scripts Útiles

### PowerShell (Windows)

```powershell
# Iniciar todo el stack
.\start_app.ps1

# Solo backend
.\run_backend.ps1

# Solo frontend
.\run_frontend.ps1

# Detener servicios
.\stop_services.ps1
```

## 🐳 Docker

### Servicios Disponibles

- **backend**: FastAPI en puerto 8000
- **frontend**: React en puerto 3000
- **gateway**: Nginx proxy en puerto 8080
- **database**: PostgreSQL (opcional)

### Comandos Docker

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir sin cache
docker-compose build --no-cache
```

## 🌍 Internacionalización

El proyecto soporta múltiples idiomas:

- Español (ES)
- Inglés (EN)
- Portugués (PT)

Los archivos de traducción se sirven desde `frontend/public/i18n` en producción (Pages) y se incluyen fallbacks embebidos en `frontend/src/locales` por si el hosting no entrega `/i18n/*.json`.

## 🧪 Testing

```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

## ✅ Calidad & CI

- Workflow Backend CI: ejecuta pytest y `scripts/check_messages.py` en cada push/PR.
- Workflow Deploy Frontend: build + deploy a GitHub Pages con API URL normalizada.
- Workflow Publish Backend Image: construye y publica imagen Docker (tags latest, fecha y SHA) en Docker Hub.
- Mensajes y tags centralizados en `constants.py` para respuestas homogéneas.
- Script de control de duplicados: `python scripts/check_messages.py` (añade exit code 1 si encuentra repeticiones).

### Historial y Planificación

- Para cambios completados y releases: ver `CHANGELOG_2026-04-18.md` y `CHANGELOG_2025-10-11.md`.
- Para planes operativos de continuidad: ver `NEXT_SESSION.md` y `docs/NEXT_SESSION.MD`.

### Automatización de túnel temporal (Pages → Backend local)

Para regenerar una URL pública y actualizar el secret `VITE_PUBLIC_API_URL`:

```powershell
# Método completo (levanta backend local + túnel ngrok/cloudflared)
./run_tunnel_backend.ps1 -TunnelProvider cloudflared -UpdateSecret -TriggerDeploy

# Solo recrear túnel cloudflared con docker-compose.tunnel.yml y actualizar secret + redeploy
./docker_update_tunnel_secret.ps1 -TriggerDeploy
```

Tras unos ~60s el frontend en Pages se redeploya y comienza a usar la nueva URL.


## 📊 Monitoreo

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **ReDoc**: `GET /redoc`

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas, por favor abre un issue en el repositorio.

---

### Desarrollado con ❤️ para Uruguay

---

### GitHub Pages

El frontend se publica automáticamente en GitHub Pages en cada push a `master` dentro de `frontend/`.

- URL: <https://apmauj.github.io/sifu/>
- Backend configurable con `VITE_PUBLIC_API_URL` (secret del repo) si no se sirve en `/sifu/api`.

Por qué no corre el backend en Pages: GitHub Pages solo sirve archivos estáticos. El backend (FastAPI/Python) debe hospedarse aparte y exponerse por HTTPS. Luego el frontend se construye con `VITE_PUBLIC_API_URL` apuntando a `https://TU-BACKEND/api`.

Guía: ver `docs/DEPLOY_BACKEND.md` para opciones rápidas (Render, VPS con Docker Compose o túnel temporal).

#### Conectar el frontend de GitHub Pages a un backend local (desde tu PC)

Si querés que la versión publicada en GitHub Pages (`https://apmauj.github.io/sifu/`) use **tu backend corriendo en esta PC**, necesitás exponer temporalmente el puerto 8000 a Internet mediante un túnel seguro y luego reconstruir el frontend indicando esa URL pública.

Pasos rápidos:

1. Iniciar backend local con CORS correcto (opcional porque por defecto es `*`):
	```powershell
	# (Dentro del repo raíz)
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	# (Opcional) Limitar orígenes permitidos solo a GitHub Pages
	$env:ALLOW_ORIGINS="https://apmauj.github.io"
	uvicorn main:app --host 0.0.0.0 --port 8000
	```

2. Crear un túnel público (elige uno):
	- **ngrok**:
	  ```powershell
	  # Instalar si no lo tenés (https://ngrok.com/download) y luego:
	  ngrok http 8000
	  ```
	  Te dará una URL como `https://abcd-1234.ngrok-free.app`.
	- **Cloudflare Tunnel (cloudflared)**:
	  ```powershell
	  cloudflared tunnel --url http://localhost:8000
	  ```
	  Obtendrás una URL `https://<algo>.trycloudflare.com`.

3. Probar la URL del túnel: abrí `https://TU-TUNEL/api/health` en el navegador; deberías ver `{ "status": "ok", ... }`.

4. Configurar el frontend para usarla: en GitHub repositorio → Settings → Secrets and variables → Actions → New repository secret:
	- Name: `VITE_PUBLIC_API_URL`
	- Value: `https://TU-TUNEL/api`

5. Forzar un redeploy del frontend: hacé un commit mínimo (por ejemplo actualizar este README) o re‑ejecutá el workflow `Deploy Frontend to GitHub Pages`.

6. Una vez publicado nuevamente, abrí `https://apmauj.github.io/sifu/` y verificá en la consola de red del navegador que las requests van a tu dominio del túnel (`/api/...`).

Notas importantes:
- Cada vez que reinicies el túnel, la URL cambia (salvo cuenta paga); deberás actualizar el secret y redeploy.
- No uses esto para producción real; es solo para demostraciones o debugging rápido.
- Alternativa sin rebuild: levantar localmente el frontend (`npm run dev`) y abrirlo en tu máquina; esa versión puede apuntar directamente a `http://localhost:8000/api` via proxy ya configurado en `vite.config.js`.
 - Script auxiliar: `./run_tunnel_backend.ps1 -TunnelProvider ngrok -UpdateSecret -TriggerDeploy` automatiza backend + túnel + secret + redeploy.

#### Modo totalmente Docker (backend + túnel sin scripts locales)

Si preferís no instalar ngrok/cloudflared ni correr Python directamente en tu host:

1. Usá el nuevo archivo `docker-compose.tunnel.yml`:
	```powershell
	docker compose -f docker-compose.tunnel.yml up -d --build
	```
2. Ver logs del túnel (cloudflared por defecto) para obtener la URL pública:
	```powershell
	docker logs -f sifu-tunnel | Select-String trycloudflare
	```
	Verás una línea con `https://<algo>.trycloudflare.com`.
3. Probar health:
	```powershell
	curl https://<algo>.trycloudflare.com/api/health
	```
4. Actualizar el secret `VITE_PUBLIC_API_URL` en GitHub con `https://<algo>.trycloudflare.com/api` y redeploy del frontend.
5. Cuando cambie la URL (reinicio del túnel), repetir solo pasos 2–4.

Notas:
- Alternativa ngrok: descomentá el servicio `ngrok` en `docker-compose.tunnel.yml`, definí `NGROK_AUTHTOKEN` en un `.env` y comentá el servicio `tunnel` de cloudflared.
- Para producción real preferí un dominio propio + reverse proxy (ver `docker-compose.gateway.yml`).
- Podés ajustar CORS cambiando `ALLOW_ORIGINS` en el servicio `backend`.

