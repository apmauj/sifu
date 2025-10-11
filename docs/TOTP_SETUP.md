# TOTP Setup Guide - Monitoring Dashboard Access

Este documento explica cómo configurar el acceso protegido por TOTP (Time-based One-Time Password) para el dashboard de monitoreo de SIFU.

## 📋 Visión General

El sistema de TOTP protege el dashboard de monitoreo (`/api/monitoring/*`) sin requerir una base de datos de usuarios. Utiliza:

- **Un solo secreto compartido** (TOTP secret)
- **Códigos temporales de 6 dígitos** (válidos 30 segundos)
- **Sesiones temporales** (1 hora por defecto)
- **Apps de autenticación estándar** (Google Authenticator, Authy, etc.)

## 🔧 Setup Inicial (Primera Vez)

### Paso 1: Generar Secreto TOTP

```bash
# Opción A: Desde terminal
python -c "import pyotp; print(pyotp.random_base32())"

# Opción B: Usando el servicio
python -c "from simple_totp import SimpleTOTP; s = SimpleTOTP(); print(s.secret)"
```

**Ejemplo de salida:**
```
MI6GJIRKWYLBWDHCJW2JHC6TQYRIVH44
```

**⚠️ IMPORTANTE:** Guarda este secreto de forma segura. Lo necesitarás para configurar tus apps de autenticación.

### Paso 2: Agregar a Archivo .env

Edita tu archivo `.env`:

```bash
# TOTP secret for monitoring dashboard access
MONITORING_TOTP_SECRET=MI6GJIRKWYLBWDHCJW2JHC6TQYRIVH44

# Optional: Session duration (default: 1 hour)
MONITORING_SESSION_HOURS=1

# Enable development mode for setup
ENVIRONMENT=development
```

### Paso 3: Iniciar Backend

```bash
# Desde el directorio raíz
python main.py

# O con uvicorn
uvicorn main:app --reload
```

### Paso 4: Obtener QR Code

Visita el endpoint de setup (solo disponible en modo development):

```
http://localhost:8000/api/monitoring/setup
```

**Respuesta JSON:**
```json
{
  "uri": "otpauth://totp/SIFU%20Monitoring?secret=MI6GJIRKWYLBWDHCJW2JHC6TQYRIVH44&issuer=SIFU",
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "secret": "MI6GJIRKWYLBWDHCJW2JHC6TQYRIVH44",
  "warning": "Save this secret securely! Add to .env as MONITORING_TOTP_SECRET",
  "setup_instructions": [
    "1. Scan QR code with Google Authenticator or Authy",
    "2. Or manually enter the secret in your authenticator app",
    "3. Save the secret to .env file: MONITORING_TOTP_SECRET=<secret>",
    "4. Disable this endpoint in production (set ENVIRONMENT=production)"
  ]
}
```

### Paso 5: Configurar App de Autenticación

**Opción A: Escanear QR Code**
1. Abre Google Authenticator o Authy en tu móvil
2. Selecciona "Agregar cuenta" o "Escanear código QR"
3. Escanea el código QR mostrado en la respuesta JSON (campo `qr_code`)
4. La cuenta aparecerá como "SIFU Monitoring"

**Opción B: Entrada Manual**
1. Abre tu app de autenticación
2. Selecciona "Entrada manual" o "Enter setup key"
3. Ingresa:
   - **Account name:** SIFU Monitoring
   - **Secret key:** MI6GJIRKWYLBWDHCJW2JHC6TQYRIVH44
   - **Time-based:** Sí (30 segundos)

### Paso 6: Verificar Funcionamiento

```bash
# Obtener código actual de tu app de autenticación (ej: 935188)
# Luego probar el endpoint de verificación:

curl -X POST "http://localhost:8000/api/monitoring/verify?code=935188"
```

**Respuesta exitosa:**
```json
{
  "access": "granted",
  "session_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "expires_in": 3600,
  "message": "Access granted to monitoring dashboard"
}
```

### Paso 7: Deshabilitar Endpoint de Setup (Producción)

En tu archivo `.env` de producción:

```bash
# Cambiar a production para deshabilitar /api/monitoring/setup
ENVIRONMENT=production
```

El endpoint `/api/monitoring/setup` devolverá 404 en modo producción.

## 🔐 Uso Diario

### 1. Obtener Código de Acceso

Abre tu app de autenticación (Google Authenticator, Authy, etc.) y busca "SIFU Monitoring". Verás un código de 6 dígitos que cambia cada 30 segundos.

### 2. Verificar Código y Obtener Token

```bash
# Reemplaza 123456 con el código actual de tu app
curl -X POST "http://localhost:8000/api/monitoring/verify?code=123456"
```

**Respuesta:**
```json
{
  "access": "granted",
  "session_token": "550e8400-e29b-41d4-a716-446655440000",
  "expires_in": 3600,
  "message": "Access granted to monitoring dashboard"
}
```

Guarda el `session_token` - lo necesitarás para las siguientes requests.

### 3. Acceder al Dashboard de Monitoreo

```bash
# Usar el session_token en el query parameter
curl "http://localhost:8000/api/monitoring/status?session_token=550e8400-e29b-41d4-a716-446655440000"
```

**Respuesta:**
```json
{
  "dashboard": { ... },
  "metrics": { ... },
  "health": { ... },
  "alerts": [ ... ],
  "circuit_breakers": { ... },
  "session_info": {
    "active_sessions": 1,
    "session_duration_hours": 1,
    "totp_interval_seconds": 30
  }
}
```

### 4. Verificar Estado de Sesión

```bash
curl "http://localhost:8000/api/monitoring/session?session_token=550e8400-e29b-41d4-a716-446655440000"
```

### 5. Cerrar Sesión (Logout)

```bash
curl -X DELETE "http://localhost:8000/api/monitoring/session?session_token=550e8400-e29b-41d4-a716-446655440000"
```

## 🌐 Integración Frontend

### Ejemplo con React

```jsx
// MonitoringAccess.jsx
import { useState } from 'react';

const MonitoringAccess = () => {
  const [code, setCode] = useState('');
  const [sessionToken, setSessionToken] = useState(
    sessionStorage.getItem('monitoring_token')
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(
        `/api/monitoring/verify?code=${code}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        const data = await response.json();
        setSessionToken(data.session_token);
        sessionStorage.setItem('monitoring_token', data.session_token);
        // Redirigir al dashboard
      } else {
        alert('Código inválido o expirado');
      }
    } catch (error) {
      console.error('Error verificando código:', error);
    }
  };

  if (sessionToken) {
    return <MonitoringDashboard token={sessionToken} />;
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Acceso a Monitoreo</h3>
      <input
        type="text"
        placeholder="Código TOTP (6 dígitos)"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        maxLength={6}
        pattern="\d{6}"
      />
      <button type="submit">Verificar</button>
    </form>
  );
};
```

### Protección de Rutas

```jsx
// Verificar sesión antes de mostrar contenido sensible
const checkSession = async (token) => {
  const response = await fetch(
    `/api/monitoring/session?session_token=${token}`
  );
  const data = await response.json();
  return data.valid;
};
```

## 🔒 Seguridad

### Rate Limiting

El endpoint `/api/monitoring/verify` está protegido con rate limiting:
- **Máximo:** 5 intentos por minuto por IP
- **Ventana:** 60 segundos

Si excedes el límite:
```json
{
  "detail": "Rate limit exceeded. Too many requests."
}
```

### Expiración de Sesiones

- **Duración por defecto:** 1 hora (3600 segundos)
- **Configurable:** Variable `MONITORING_SESSION_HOURS` en `.env`
- **Limpieza automática:** Las sesiones expiradas se eliminan periódicamente

### Validación de Códigos

- **Formato:** 6 dígitos numéricos
- **Validez:** ±30 segundos (ventana de 1 slot antes/después)
- **Algoritmo:** TOTP estándar (RFC 6238)

## 🔧 Troubleshooting

### Error: "Invalid or expired TOTP code"

**Causas posibles:**
1. Código expirado (> 30 segundos)
2. Reloj del servidor desincronizado
3. Secret incorrecto en `.env`

**Solución:**
```bash
# Verificar que el secret en .env coincida con el de tu app
# Verificar hora del sistema
date
```

### Error: "Endpoint not available in production"

El endpoint `/api/monitoring/setup` solo funciona con `ENVIRONMENT=development`.

**Solución:**
- Cambiar temporalmente a `ENVIRONMENT=development`
- O usar el URI manualmente: `otpauth://totp/SIFU%20Monitoring?secret=YOUR_SECRET&issuer=SIFU`

### Sesión Expirada Constantemente

**Solución:**
Aumentar duración de sesión en `.env`:
```bash
MONITORING_SESSION_HOURS=2  # 2 horas en vez de 1
```

### Rate Limit Exceeded

**Solución:**
Esperar 60 segundos antes de intentar nuevamente.

## 📚 Referencias

- [TOTP RFC 6238](https://tools.ietf.org/html/rfc6238)
- [PyOTP Documentation](https://pyauth.github.io/pyotp/)
- [Google Authenticator](https://support.google.com/accounts/answer/1066447)
- [Authy](https://authy.com/)

## 🔄 Rotación de Secretos

### Cuándo Rotar

- Cada 90-180 días (recomendado)
- Si el secreto fue comprometido
- Si un miembro del equipo pierde acceso

### Cómo Rotar

1. Generar nuevo secreto
2. Actualizar `.env` con nuevo secreto
3. Reconfigurar todas las apps de autenticación
4. Reiniciar backend

```bash
# Generar nuevo secret
python -c "import pyotp; print(pyotp.random_base32())"

# Actualizar .env
MONITORING_TOTP_SECRET=NEW_SECRET_HERE

# Reiniciar
systemctl restart sifu  # O docker-compose restart
```

## 🤝 Compartir Acceso (Equipo)

Para dar acceso a múltiples personas:

1. Compartir el **mismo secreto** de forma segura (password manager, encriptado)
2. Cada persona configura su propia app de autenticación con el secreto compartido
3. Todos generarán el **mismo código** al mismo tiempo

**Alternativa (más segura):**
- Implementar múltiples secretos (requiere modificar `simple_totp.py`)
- Usar un sistema completo de usuarios si el equipo crece

## 📝 Notas Adicionales

- El sistema **no requiere base de datos de usuarios**
- Las sesiones se mantienen **en memoria** (se pierden al reiniciar)
- Para persistencia de sesiones, considerar Redis en producción
- El secreto se puede almacenar en un **secret manager** (AWS Secrets Manager, Azure Key Vault, etc.)
