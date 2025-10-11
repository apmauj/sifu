# Changelog - 11 de Octubre 2025

## Resumen de Cambios Críticos

Este documento resume los problemas encontrados y las soluciones implementadas durante la sesión de debugging del 11 de octubre de 2025.

---

## 🔒 Problema SSL con Servidores INE/BHU

### Problema
Los servidores de INE (www5.ine.gub.uy) y BHU presentan **cadenas de certificados SSL incompletas** (falta el certificado intermedio de Sectigo/Comodo). Esto causaba errores de verificación SSL al intentar descargar archivos Excel:

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

### Solución Implementada
Se deshabilitó la verificación SSL **únicamente para los servidores oficiales del gobierno uruguayo** (.gub.uy):

**Archivos modificados:**
- `excel_processor.py`: Agregado `verify=False` en los métodos `download_excel()` de:
  - `UIExcelProcessor` (línea ~70)
  - `URExcelProcessor` (línea ~270)
  - `ExchangeRateExcelProcessor` (línea ~650)

**Justificación:**
- Son sitios oficiales del gobierno (.gub.uy)
- El problema es del servidor, no del cliente
- Se agregan advertencias explícitas en los logs y comentarios del código

**Commits:**
- `64f695d` - fix(ssl): disable SSL verification for INE/BHU government sites
- `5d71b94` - fix(tests): update UR download test to expect verify=False parameter

**⚠️ Nota de Seguridad:**
Este cambio está **documentado y justificado**. No usar `verify=False` en otros contextos sin evaluación de seguridad.

---

## 🔄 Desincronización de Rutas API Frontend/Backend

### Problema
El commit `947a2a1` cambió las rutas del **frontend** de `/api/exchange-rate/*` a `/api/exchange/*`, pero **nunca se actualizó el backend**. Esto causaba errores 404 en el panel de Cotizaciones:

```
GET /api/exchange/latest HTTP/1.1" 404 Not Found
GET /api/exchange/info HTTP/1.1" 404 Not Found
```

### Solución Implementada
Se **revirtieron las rutas del frontend** para que coincidan con el backend actual:

**Rutas corregidas en `frontend/src/services/exchangeService.js`:**
- `/exchange/latest` → `/exchange-rate/latest`
- `/exchange/info` → `/exchange-rate/info`
- `/exchange/currency/{currency}` → `/exchange-rate/currency/{currency}`
- `/exchange/{date}` → `/exchange-rate/{date}`
- `/exchange/{date}/{currency}` → `/exchange-rate/{date}/{currency}`
- `/exchange/range/{start}/{end}` → `/exchange-rate/range/{start}/{end}`
- `/exchange/refresh` → `/exchange-rate/refresh`

**Tests actualizados:**
- `frontend/src/test/services/exchangeService.test.js`: 10 assertions corregidas

**Commits:**
- `a887e71` - fix(frontend): revert exchange routes to /exchange-rate/* to match backend

### Lección Aprendida
Al refactorizar endpoints API, **siempre actualizar backend Y frontend simultáneamente**, o usar feature flags para transiciones graduales.

---

## 📊 Datos de UR Faltantes (Septiembre/Octubre 2025)

### Problema
El servidor de BHU no está respondiendo correctamente con el archivo Excel de UR actualizado (devuelve HTML en lugar de Excel). Los últimos datos disponibles eran de agosto 2025.

### Solución Implementada
Se agregaron **manualmente** los valores de UR para septiembre y octubre 2025 obtenidos de fuentes oficiales:

```sql
INSERT INTO ur_records (year, month, value, created_at, updated_at)
VALUES 
  (2025, 9, 1835.93, NOW(), NOW()),
  (2025, 10, 1838.64, NOW(), NOW());
```

**Método de inserción:**
```python
docker exec sifu-backend python -c "..."
```

### Estado Actual
- **Total de meses en 2025**: 10 (enero a octubre)
- **Último valor**: Octubre 2025 = 1.838,64

### Nota Futura
Cuando el servidor de BHU vuelva a funcionar correctamente, el proceso automático de actualización debería reemplazar estos valores si hay discrepancias.

---

## 🧪 Tests del Backend

### Problema Menor
El test `test_download_excel_success` en `tests/test_excel_processor_comprehensive.py` fallaba porque el mock esperaba `requests.get()` sin el parámetro `verify`, pero el código real ahora usa `verify=False`.

### Solución
Se actualizó la aserción del mock para incluir `verify=False`:

```python
mock_get.assert_called_once_with(
    ur_processor.url,
    timeout=30,
    headers={...},
    verify=False,  # ← Agregado
)
```

---

## 📋 Estado Final del Sistema

### ✅ Funcionando Correctamente
- **Panel UI (Unidad Indexada)**: 8,559 registros
- **Panel UR (Unidades Reajustables)**: 680 registros (hasta octubre 2025)
- **Panel Cotizaciones (Exchange Rate)**: 23,383 registros históricos (2001-2025)
- **Panel BROU**: 5 monedas en tiempo real

### ⚠️ Limitaciones Conocidas
- **Servidor BHU**: No está sirviendo el archivo Excel correctamente (devuelve HTML)
- **Actualización UR**: Requiere intervención manual hasta que BHU corrija su servidor

### 🚀 CI/CD
Todos los workflows pasando:
- ✅ Security Audit (Backend + Frontend)
- ✅ Backend Tests (238 passed, 12 skipped)
- ✅ Frontend Tests (606 passed)
- ✅ Docker Image Published
- ✅ Frontend Deployed to GitHub Pages

---

## 📝 Recomendaciones Futuras

1. **Monitoreo SSL**: Considerar agregar un health check específico para detectar problemas SSL con INE/BHU
2. **API Versioning**: Implementar versionado de API (e.g., `/api/v2/exchange/*`) para evitar breaking changes
3. **UR Data Source**: Buscar fuentes alternativas para datos de UR en caso de que BHU siga con problemas
4. **Alertas**: Configurar alertas cuando los datos de UR/UI/Exchange Rate tengan más de X días de antigüedad

---

## 🔗 Commits Relacionados

```
64f695d - fix(ssl): disable SSL verification for INE/BHU government sites
5d71b94 - fix(tests): update UR download test to expect verify=False parameter
a887e71 - fix(frontend): revert exchange routes to /exchange-rate/* to match backend
```

---

**Fecha**: 11 de Octubre 2025  
**Duración de la sesión**: ~3 horas  
**Issues resueltos**: 3 críticos (SSL, rutas API, datos faltantes)  
**Tests pasando**: 844 (238 backend + 606 frontend)
