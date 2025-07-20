# Corrección de Problema de Zona Horaria

## 🕐 Problema Identificado

**Fecha**: 16 de junio de 2025, 21:24 (UTC-3)
**Síntoma**: El botón "Hoy" en las acciones rápidas mostraba el 17 de junio en lugar del 16 de junio.

## 🔍 Análisis del Problema

### Causa Raíz
- **Backend**: Usa `datetime.utcnow()` que devuelve tiempo UTC
- **Frontend**: Usaba `new Date().toISOString().split('T')[0]` que convierte la hora local a UTC
- **Zona Horaria**: Uruguay (UTC-3) → 21:24 local se convierte a 00:24 UTC del día siguiente

### Evidencia
```bash
# Hora local del sistema
lunes, 16 de junio de 2025, 21:25:35 -03

# Backend (UTC)
{"status": "ok", "timestamp": "2025-06-17T00:25:54.355299"}

# Frontend (antes de la corrección)
Frontend (local): 2025-06-17  # ❌ Incorrecto
Frontend (UTC): 2025-06-17T00:25:57.569Z
Timezone offset: 180  # 3 horas
```

## ✅ Solución Implementada

### 1. Creación de Utilidades de Fecha
**Archivo**: `frontend/src/utils/dateUtils.js`

```javascript
// Obtiene fecha actual en zona horaria local
export const getTodayLocal = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Calcula fechas pasadas en zona horaria local
export const getDaysAgoLocal = (days) => {
  const result = new Date();
  result.setDate(result.getDate() - days);
  return formatDateLocal(result);
};
```

### 2. Componentes Actualizados
- `SearchForm.jsx`
- `QuickSelectors.jsx`
- `ExchangeSearchForm.jsx`
- `App.jsx`

### 3. Cambios Realizados
```javascript
// ❌ ANTES (problemático)
const today = new Date().toISOString().split('T')[0];

// ✅ DESPUÉS (correcto)
const today = getTodayLocal();
```

## 🧪 Verificación

```bash
# Resultado después de la corrección
Fecha local (nueva función): 2025-06-16  # ✅ Correcto
Fecha UTC (método anterior): 2025-06-17   # ❌ Problemático
```

## 📋 Archivos Modificados

1. **Nuevo archivo**: `frontend/src/utils/dateUtils.js`
2. **Actualizados**:
   - `frontend/src/components/SearchForm.jsx`
   - `frontend/src/components/QuickSelectors.jsx`
   - `frontend/src/components/ExchangeSearchForm.jsx`
   - `frontend/src/App.jsx`

## 🎯 Impacto

### Funcionalidades Corregidas
- ✅ Botón "Hoy" en acciones rápidas de UI
- ✅ Botón "Hoy" en acciones rápidas de Cotizaciones
- ✅ Selectores rápidos (ayer, última semana, etc.)
- ✅ Validaciones de fechas máximas
- ✅ Inicialización de fechas por defecto

### Zonas Horarias Afectadas
- **Uruguay (UTC-3)**: Problema principal resuelto
- **Argentina (UTC-3)**: También se beneficia
- **Otras zonas**: Mejora general en consistencia

## 🔧 Consideraciones Técnicas

### Backend
- Mantiene `datetime.utcnow()` para consistencia de base de datos
- Los timestamps internos siguen siendo UTC (correcto para logs y auditoría)

### Frontend
- Usa zona horaria local para interfaz de usuario
- Mantiene compatibilidad con APIs que esperan formato YYYY-MM-DD
- No afecta cálculos de fechas en el servidor

## 🚀 Beneficios

1. **Experiencia de Usuario**: Fechas coherentes con la zona horaria local
2. **Precisión**: Eliminación de confusión de fechas
3. **Mantenibilidad**: Funciones centralizadas para manejo de fechas
4. **Escalabilidad**: Fácil extensión para otras zonas horarias si es necesario

## 📝 Notas para Desarrolladores

- Usar siempre `getTodayLocal()` en lugar de `new Date().toISOString().split('T')[0]`
- Para cálculos de fechas pasadas, usar `getDaysAgoLocal(n)`
- El backend mantiene UTC para consistencia de datos
- Las utilidades están en `frontend/src/utils/dateUtils.js` 