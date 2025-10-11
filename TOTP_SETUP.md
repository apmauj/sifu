# 🔐 TOTP 2FA Setup Guide para SIFU

## 📋 Resumen

SIFU implementa autenticación TOTP (Time-based One-Time Password) para proteger el acceso al dashboard de monitoreo. Este sistema usa códigos de 6 dígitos que cambian cada 30 segundos, similares a los que usan bancos y servicios como Google, GitHub, etc.

## 🎯 Flujo de Usuario

1. Usuario hace click en el ❤️ del footer
2. Si no tiene sesión válida → aparece modal pidiendo código TOTP
3. Usuario abre app de autenticación (Google Authenticator, Authy, etc.)
4. Ingresa el código de 6 dígitos actual
5. Si es válido → obtiene sesión de 1 hora y accede al dashboard

---

## 🛠️ Setup en Development

### 1. Generar Secret TOTP

El endpoint `/api/monitoring/setup` **solo funciona en development** (`ENVIRONMENT=development`).

**Abrir en navegador:**
```
http://localhost:8000/static/totp-setup.html
```

Esta página mostrará:
- ✅ QR code para escanear
- ✅ Secret en texto (por si prefieres ingresarlo manualmente)
- ✅ Botón para probar códigos
- ✅ Instrucciones de configuración

### 2. Configurar en App de Autenticación

**Opción A: Escanear QR**
1. Abre Google Authenticator o Authy
2. Selecciona "Añadir cuenta" o "+"
3. Escanea el QR code mostrado en la página
4. La entrada se guardará como "SIFU Monitoring"

**Opción B: Ingresar manualmente**
1. Abre Google Authenticator o Authy
2. Selecciona "Ingresar código manualmente"
3. Copia el secret mostrado en la página (ej: `FBWPEUU7LFOX3UASHYC3EUH3U63SWOEV`)
4. Nombre de la cuenta: `SIFU Monitoring`
5. Tipo: `Time-based` (basado en tiempo)

### 3. Guardar Secret en .env

El secret ya se encuentra en tu archivo `.env`:
```bash
MONITORING_TOTP_SECRET=FBWPEUU7LFOX3UASHYC3EUH3U63SWOEV
```

⚠️ **IMPORTANTE**: Este secret debe ser el mismo en development y production si quieres usar la misma entrada en tu app de autenticación.

### 4. Probar Funcionamiento

En la página de setup:
1. Click en "Test Your Code"
2. Ingresa el código actual de 6 dígitos de tu app
3. Deberías ver: ✅ Success con session token

---

## 🚀 Setup en Production

### 1. Copiar Secret a Production

**El mismo secret debe estar en el `.env` de producción:**

```bash
# En .env de producción
MONITORING_TOTP_SECRET=FBWPEUU7LFOX3UASHYC3EUH3U63SWOEV
ENVIRONMENT=production  # ⚠️ CRÍTICO: Esto desactiva /api/monitoring/setup
```

### 2. ¿Cómo agregar a Authy en producción?

**NO necesitas volver a escanear un QR nuevo.** Si usas el **mismo secret** en dev y prod:

✅ **Ya tienes la entrada en tu app** - El código TOTP es el mismo para development y production porque usan el mismo secret.

**Si necesitas agregar la entrada en otro dispositivo:**

**Opción 1: Copiar desde app existente** (Authy/Google Authenticator)
- Authy permite sincronizar cuentas entre dispositivos
- Google Authenticator permite exportar/importar cuentas

**Opción 2: Crear entrada manual nueva**
1. Abre Authy o Google Authenticator
2. "Add Account" → "Enter key manually"
3. **Account name:** `SIFU Production` (o el nombre que prefieras)
4. **Key/Secret:** `FBWPEUU7LFOX3UASHYC3EUH3U63SWOEV` (el mismo de .env)
5. **Type:** `Time-based`

### 3. Desactivar Endpoint de Setup

En producción, el endpoint `/api/monitoring/setup` **NO debe estar disponible** por seguridad.

**En main.py** (línea ~2031):
```python
@app.get("/api/monitoring/setup", tags=["Monitoring"])
async def get_monitoring_setup():
    """
    Get TOTP setup information (QR code and secret).
    Only available in development environment.
    """
    if not IS_DEVELOPMENT:
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
```

Esto se controla automáticamente con `ENVIRONMENT=production` en el `.env`.

### 4. Verificar Configuración

**Backend logs al iniciar:**
```
INFO:simple_totp:SimpleTOTP initialized successfully
```

✅ Si ves este mensaje → el secret se cargó correctamente

❌ Si ves warning:
```
WARNING:simple_totp:No MONITORING_TOTP_SECRET found. Generated new secret: ...
```
→ El secret NO está en .env o `load_dotenv()` no se ejecutó

---

## 🔒 Seguridad

### Protección del Secret

1. **Nunca commitear .env** con secrets reales
2. **No compartir el secret** públicamente (GitHub issues, logs, etc.)
3. **Usar secrets diferentes** entre development y staging si tienes ambientes separados

### Regenerar Secret (si se compromete)

Si el secret se filtra, regenerar:

```bash
# En Python (o usar página de setup en dev)
import pyotp
new_secret = pyotp.random_base32()
print(f"MONITORING_TOTP_SECRET={new_secret}")
```

Luego:
1. Actualizar `.env` con el nuevo secret
2. **Re-escanear QR code** en todas las apps de autenticación
3. Reiniciar backend

---

## 🧪 Testing

### Test Endpoint Directamente

```bash
# Obtener código actual de tu app (ej: 123456)
curl -X POST "http://localhost:8000/api/monitoring/verify?code=123456"

# Respuesta esperada (200 OK):
{
  "access": "granted",
  "session_token": "uuid-aqui",
  "expires_in": 3600
}
```

### Test con Session Token

```bash
# Usar token en headers
curl -H "Authorization: Bearer <session_token>" \
  "http://localhost:8000/api/monitoring/status"
```

---

## 📊 Configuración Avanzada

### Variables de Entorno Disponibles

```bash
# Secret TOTP (REQUERIDO)
MONITORING_TOTP_SECRET=tu-secret-aqui

# Duración de sesión en horas (default: 1 hora)
MONITORING_SESSION_HOURS=1

# Environment (controla disponibilidad de /setup)
ENVIRONMENT=development  # o production
```

### Cambiar Duración de Sesión

En `.env`:
```bash
MONITORING_SESSION_HOURS=2  # Sesiones de 2 horas
```

⚠️ **Consideración de seguridad**: Sesiones más largas = mayor ventana si el dispositivo se compromete.

---

## 🆘 Troubleshooting

### "Field required" o 422 errors

**Causa:** El código no se está enviando correctamente
**Solución:** Asegurar que el código tiene exactamente 6 dígitos numéricos

### "Invalid or expired code"

**Causa:** El código expiró (cambian cada 30 segundos) o el reloj del servidor está desincronizado
**Solución:** 
1. Verificar que el reloj del servidor esté sincronizado (NTP)
2. Usar código fresco (esperar nuevo código si está por expirar)

### "No MONITORING_TOTP_SECRET found"

**Causa:** El secret no está en .env o no se cargó
**Solución:**
1. Verificar que existe `MONITORING_TOTP_SECRET=...` en `.env`
2. Verificar que `load_dotenv()` se ejecuta en `main.py` (línea ~18)
3. Reiniciar backend

### El modal no aparece al hacer click en ❤️

**Causa:** Session storage tiene sesión válida previa
**Solución:**
1. Abrir DevTools → Application → Session Storage
2. Eliminar `monitoring_session_token` y `monitoring_session_expires`
3. Hacer click en ❤️ de nuevo

---

## 📱 Apps de Autenticación Recomendadas

### Google Authenticator
- ✅ Gratis, simple, confiable
- ✅ iOS y Android
- ❌ No sincroniza entre dispositivos automáticamente

### Authy
- ✅ Gratis, sincroniza entre dispositivos
- ✅ iOS, Android, Desktop
- ✅ Backups encriptados en la nube
- ✅ **Recomendado**

### Microsoft Authenticator
- ✅ Gratis, sincroniza con cuenta Microsoft
- ✅ iOS y Android
- ✅ Integración con ecosistema Microsoft

### 1Password / Bitwarden
- ✅ Gestor de contraseñas + TOTP integrado
- 💰 Requiere suscripción (1Password)
- ✅ Bitwarden tiene plan gratis con TOTP

---

## 🔄 Flujo de Deployment

### Development → Production

1. **Generar secret en dev:**
   ```bash
   # Abrir http://localhost:8000/static/totp-setup.html
   # Copiar secret mostrado
   ```

2. **Configurar en app de autenticación:**
   - Escanear QR o ingresar secret manualmente
   - Guardar como "SIFU Production"

3. **Copiar secret a .env de producción:**
   ```bash
   MONITORING_TOTP_SECRET=<secret-de-dev>
   ENVIRONMENT=production
   ```

4. **Deploy y verificar:**
   ```bash
   # Verificar logs de backend
   docker logs <container> | grep "SimpleTOTP initialized"
   
   # Test con código actual
   curl -X POST "https://your-prod-url.com/api/monitoring/verify?code=123456"
   ```

---

## � Monitoreo y Auditoría

### Logs de Auditoría

Todos los eventos de autenticación se registran en:
```
logs/totp_audit.log
```

**Formato de logs estructurado:**
```
2025-10-11 14:23:45 | INFO | TOTP_AUTH_SUCCESS | session=1c14de14 | ip=127.0.0.1 | expires=2025-10-11T15:23:45
2025-10-11 14:24:10 | WARNING | TOTP_AUTH_FAILED | session=a3f9b8c2 | ip=192.168.1.5 | reason=invalid_code | failed_attempts=1
2025-10-11 14:24:35 | INFO | TOTP_SESSION_LOGOUT | session=1c14de14 | ip=127.0.0.1
2025-10-11 14:25:00 | INFO | TOTP_SESSION_EXPIRED | session=9d7e2f4a
```

**Eventos registrados:**
- `TOTP_AUTH_SUCCESS`: Verificación exitosa con sesión creada
- `TOTP_AUTH_FAILED`: Código inválido o expirado
- `TOTP_AUTH_ERROR`: Error en proceso de verificación
- `TOTP_SESSION_LOGOUT`: Logout manual (DELETE /session)
- `TOTP_SESSION_EXPIRED`: Sesión expiró automáticamente

### Métricas de Autenticación

Endpoint para monitoreo en tiempo real:
```
GET /api/monitoring/metrics
```

**Respuesta:**
```json
{
  "total_attempts": 15,
  "successful_authentications": 12,
  "failed_authentications": 3,
  "success_rate_percent": 80.0,
  "failed_attempts_by_ip": {
    "192.168.1.5": 2,
    "10.0.0.8": 1
  },
  "ips_with_failures": 2,
  "active_sessions": 2
}
```

**Métricas incluidas:**
- Total de intentos de autenticación
- Conteo de éxitos y fallos
- Tasa de éxito porcentual
- Fallos agrupados por IP (para detectar ataques)
- IPs con fallos recientes
- Sesiones activas actualmente

**Uso típico:**
```bash
# Ver métricas actuales
curl http://localhost:8000/api/monitoring/metrics

# Monitoreo continuo (cada 5 segundos)
watch -n 5 'curl -s http://localhost:8000/api/monitoring/metrics | jq'
```

---

## �📚 Referencias

- **pyotp docs:** https://pyauth.github.io/pyotp/
- **TOTP RFC 6238:** https://datatracker.ietf.org/doc/html/rfc6238
- **QR code generation:** https://github.com/lincolnloop/python-qrcode

---

## ✅ Checklist de Implementación

### Development
- [x] Instalar `pyotp` y `qrcode[pil]`
- [x] Crear `simple_totp.py`
- [x] Agregar endpoints en `main.py`
- [x] Crear `static/totp-setup.html`
- [x] Agregar `MONITORING_TOTP_SECRET` a `.env`
- [x] Probar generación y verificación de códigos
- [x] Integrar modal en frontend (`MonitoringAccess.jsx`)
- [x] Conectar click de ❤️ con modal TOTP
- [x] Tests backend (20 passing)

### Production
- [ ] Copiar mismo `MONITORING_TOTP_SECRET` a `.env` de prod
- [ ] Configurar `ENVIRONMENT=production` en prod
- [ ] Verificar que `/api/monitoring/setup` retorna 404 en prod
- [ ] Agregar entrada en Authy con el mismo secret
- [ ] Probar autenticación en prod
- [ ] Documentar secret en gestor de secretos (Vault/AWS Secrets/etc.)
- [ ] Configurar alertas basadas en métricas (opcional)
- [ ] Revisar logs de auditoría periódicamente

---

**🎉 ¡Listo! Tu sistema TOTP está configurado y funcionando.**
