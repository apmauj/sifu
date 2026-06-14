# SIFU — Guía de Deploy en Render ($0/mes)

## Arquitectura final

```
GitHub (repo público)
  ├─ Push a master → deploy automático a GitHub Pages (frontend)
  └─ Cron cada 14 min → keep-alive ping al backend

Frontend  → GitHub Pages           🆓
Backend   → Render Free Tier       🆓
Database  → SQLite (efímero)       🆓
Scheduler → APScheduler (built-in) 🆓
Keepalive → GitHub Actions         🆓

Costo total: $0/mes
```

## Archivos nuevos/modificados

| Archivo | Acción | Descripción |
|---|---|---|
| `render.yaml` | Nuevo | Blueprint de Render para deploy automático |
| `.github/workflows/keep-alive.yml` | Nuevo | Ping cada 14 min para evitar sleep |
| `src/utils/constants.py` | Modificado | `DATABASE_CONNECT_ARGS` compatible con PostgreSQL |

---

## Paso 1: Crear cuenta en Render

1. Ir a [render.com](https://render.com) y crear cuenta
2. Conectar con GitHub y dar acceso al repo `apmauj/sifu`

## Paso 2: Crear el Web Service

1. En Render Dashboard → **New** → **Web Service**
2. Seleccionar el repo `apmauj/sifu`
3. Render detectará el `render.yaml` automáticamente
4. Verificar la configuración:
   - **Name**: `sifu-backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Configurar las variables de entorno:

| Variable | Valor | Notas |
|---|---|---|
| `PYTHONPATH` | `/app` | |
| `PYTHONUNBUFFERED` | `1` | |
| `DATABASE_PATH` | `/tmp/sifu_data.db` | `/tmp` es escribible en Render free |
| `SCHEDULER_ENABLED` | `true` | APScheduler corre mientras el servicio esté despierto |
| `SCHEDULER_TIMEZONE` | `America/Montevideo` | |
| `ENVIRONMENT` | `production` | |
| `ALLOW_ORIGINS` | `https://apmauj.github.io` | URL del frontend en GH Pages |
| `JWT_SECRET_KEY` | *(generar uno aleatorio)* | Obligatorio en production |
| `MONITORING_TOTP_SECRET` | *(opcional)* | Si querés 2FA en monitoring |

6. Click **Create Web Service**
7. Esperar a que termine el build (~3-5 min primer deploy)
8. Anotar la URL del servicio: `https://sifu-backend.onrender.com`

## Paso 3: Configurar el keep-alive

1. Ir a GitHub → repo `apmauj/sifu` → **Settings** → **Secrets and variables** → **Actions**
2. Crear una **repository variable** (o secret):
   - **Name**: `RENDER_BACKEND_URL`
   - **Value**: `https://sifu-backend.onrender.com`
3. El workflow `.github/workflows/keep-alive.yml` usará esta variable para hacer ping cada 14 minutos

## Paso 4: Actualizar el frontend para apuntar a Render

1. Ir a GitHub → repo `apmauj/sifu` → **Settings** → **Secrets and variables** → **Actions**
2. Actualizar el secret existente:
   - **Name**: `VITE_PUBLIC_API_URL`
   - **Value**: `https://sifu-backend.onrender.com/api`
3. Esto hará que el próximo deploy del frontend apunte al backend de Render en vez del túnel de Cloudflare

## Paso 5: Disparar redeploy del frontend

Para que el frontend tome la nueva URL del backend:

1. Ir a **Actions** → **CI/CD** → **Run workflow**
2. Marcar `force_frontend_deploy` = `true`
3. Ejecutar

O alternativamente, hacer un push a `master` que toque archivos del frontend.

## Paso 6: Verificar que todo funciona

1. **Backend directo**: Visitar `https://sifu-backend.onrender.com/api/health` → debe devolver `ok`
2. **Frontend**: Visitar `https://apmauj.github.io/sifu` → debe cargar con datos
3. **Keep-alive**: En **Actions** → **Keep Render Awake**, verificar que el workflow corre cada 14 min
4. **Datos**: Verificar que los endpoints devuelven datos reales (UI, UR, BROU)

## Paso 7: Limpiar lo que ya no se necesita (opcional)

Una vez verificado que Render funciona:

1. **Detener el Docker en el NUC** — Ya no necesitas el backend local
2. **Eliminar el runner self-hosted** — Si ya no lo usás para otros proyectos
3. **Simplificar CI/CD** — El workflow `ci-cd.yml` usa `self-hosted, sifu-local` runners. Considerar migrar a `ubuntu-latest` ya que el NUC ya no es necesario
4. **Eliminar workflows de túnel** — `update-tunnel.yml` y el tunnel-guard ya no son necesarios
5. **Eliminar el secret del túnel** — `VITE_PUBLIC_API_URL` ya apunta a Render

---

## Notas importantes

### Cold start
- Si el keep-alive falla o se desactiva, el servicio duerme tras 15 min sin tráfico
- Al despertar: ~30-60s de cold start + ~10-20s de bootstrap (descarga Excel y reconstruye SQLite)
- La animación de carga del frontend cubre este gap

### SQLite efímero
- El filesystem de Render free se pierde en cada deploy/restart
- El bootstrap reconstruye la DB desde las fuentes oficiales (INE, BHU, BCU)
- No hay datos de usuario que se pierdan — todo se puede recomponer

### Render free tier límites
- 750 horas/mes (alcanza para 1 servicio 24/7 con keep-alive)
- 512 MB RAM
- Se apaga tras 15 min sin tráfico (mitigado con keep-alive)
- No hay persistencia de disco entre deploys

### Si algún día necesitás más
- **Starter ($7/mes)**: Always-on, sin cold start, 2 GB RAM
- **Standard ($25/mes)**: 4 GB RAM, más CPU
- **PostgreSQL Starter ($7/mes)**: Si la efimeridad de SQLite molesta
