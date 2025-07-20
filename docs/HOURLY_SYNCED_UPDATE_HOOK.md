# Hook Personalizado: useHourlySyncedUpdate

## 📋 Descripción General

El hook `useHourlySyncedUpdate` es una utilidad personalizada que permite ejecutar una función automáticamente cada hora, sincronizada con el **minuto cero** de cada hora (1:00, 2:00, 3:00, etc.).

## 🎯 Problema Resuelto

**Antes**: Código duplicado en múltiples componentes para sincronización horaria
```javascript
// ❌ Duplicado en ExchangeRatePanel.jsx
useEffect(() => {
  fetchCurrentRates();
  const getTimeToNextHour = () => { /* lógica duplicada */ };
  const timeToNextHour = getTimeToNextHour();
  const syncTimeout = setTimeout(() => { /* más lógica duplicada */ }, timeToNextHour);
  return () => { /* cleanup duplicado */ };
}, []);

// ❌ Duplicado en BROUPanel.jsx  
useEffect(() => {
  fetchBROURates();
  const getTimeToNextHour = () => { /* misma lógica duplicada */ };
  // ... más código duplicado
}, []);
```

**Después**: Hook reutilizable que respeta DRY
```javascript
// ✅ Un solo lugar para la lógica
const fetchCurrentRates = useCallback(async () => {
  // Lógica específica del componente
}, [t]);

useHourlySyncedUpdate(fetchCurrentRates);
```

## 🔧 API del Hook

### Sintaxis
```javascript
const cleanup = useHourlySyncedUpdate(updateFunction, enabled);
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `updateFunction` | `Function` | - | **Requerido**. Función a ejecutar cada hora |
| `enabled` | `boolean` | `true` | **Opcional**. Si el hook está habilitado |

### Valor de Retorno

| Tipo | Descripción |
|------|-------------|
| `Function` | Función de cleanup manual (opcional) |

## 📖 Ejemplos de Uso

### 1. Uso Básico
```javascript
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';

const MyComponent = () => {
  const fetchData = useCallback(async () => {
    console.log('Actualizando datos...');
    // Lógica de actualización
  }, []);

  // Se ejecuta inmediatamente y luego cada hora en punto
  useHourlySyncedUpdate(fetchData);

  return <div>Mi Componente</div>;
};
```

### 2. Con Parámetro Enabled
```javascript
const MyComponent = () => {
  const [isOnline, setIsOnline] = useState(true);
  
  const fetchData = useCallback(async () => {
    // Solo actualizar si estamos online
  }, []);

  // Solo sincronizar si estamos online
  useHourlySyncedUpdate(fetchData, isOnline);

  return <div>Mi Componente</div>;
};
```

### 3. Con Cleanup Manual
```javascript
const MyComponent = () => {
  const fetchData = useCallback(async () => {
    // Lógica de actualización
  }, []);

  const cleanup = useHourlySyncedUpdate(fetchData);

  const handleStopUpdates = () => {
    cleanup(); // Detener manualmente las actualizaciones
  };

  return (
    <div>
      <button onClick={handleStopUpdates}>Detener Actualizaciones</button>
    </div>
  );
};
```

## 🕐 Comportamiento Temporal

### Ejemplo Práctico
Si el componente se monta a las **14:23:45**:

1. **Inmediato**: Ejecuta `updateFunction()` a las 14:23:45
2. **Sincronización**: Calcula que faltan 36m 15s para las 15:00:00
3. **Primera Sync**: Ejecuta `updateFunction()` a las 15:00:00
4. **Intervalos**: Ejecuta cada hora exacta: 16:00:00, 17:00:00, etc.

### Cálculo del Tiempo
```javascript
const getTimeToNextHour = () => {
  const now = new Date();
  const nextHour = new Date(now);
  nextHour.setHours(now.getHours() + 1, 0, 0, 0); // Próxima hora en punto
  return nextHour.getTime() - now.getTime();
};
```

## 🔄 Ciclo de Vida

### Montaje del Componente
1. ✅ Ejecuta `updateFunction` inmediatamente
2. ✅ Calcula tiempo hasta próxima hora
3. ✅ Programa `setTimeout` para sincronización
4. ✅ Retorna función de cleanup

### Durante la Vida del Componente
1. ✅ Espera hasta el minuto cero de la próxima hora
2. ✅ Ejecuta `updateFunction` en la hora exacta
3. ✅ Configura `setInterval` para repetir cada hora

### Desmontaje del Componente
1. ✅ Limpia `setTimeout` si está pendiente
2. ✅ Limpia `setInterval` si está activo
3. ✅ Libera referencias para evitar memory leaks

## 🧪 Testing

### Setup del Test
```javascript
import { renderHook, act } from '@testing-library/react';
import { useHourlySyncedUpdate } from '../hooks/useHourlySyncedUpdate';
import { vi, describe, it, expect } from 'vitest';

vi.useFakeTimers();

describe('useHourlySyncedUpdate', () => {
  let mockUpdateFunction;

  beforeEach(() => {
    mockUpdateFunction = vi.fn();
    vi.clearAllTimers();
  });
});
```

### Casos de Prueba
```javascript
it('debería ejecutar la función inmediatamente al montar', () => {
  renderHook(() => useHourlySyncedUpdate(mockUpdateFunction));
  expect(mockUpdateFunction).toHaveBeenCalledTimes(1);
});

it('no debería ejecutar si enabled es false', () => {
  renderHook(() => useHourlySyncedUpdate(mockUpdateFunction, false));
  expect(mockUpdateFunction).not.toHaveBeenCalled();
});
```

## 🏗️ Implementación Interna

### Estructura del Hook
```javascript
export const useHourlySyncedUpdate = (updateFunction, enabled = true) => {
  const timeoutRef = useRef(null);
  const intervalRef = useRef(null);

  const getTimeToNextHour = () => {
    // Cálculo del tiempo hasta próxima hora
  };

  const cleanup = () => {
    // Limpieza de timers
  };

  useEffect(() => {
    // Lógica principal del hook
    return cleanup;
  }, [updateFunction, enabled]);

  return cleanup;
};
```

### Gestión de Referencias
- **`timeoutRef`**: Referencia al timeout de sincronización inicial
- **`intervalRef`**: Referencia al interval de repetición horaria
- **Cleanup automático**: Via `useEffect` return
- **Cleanup manual**: Via función retornada

## ✅ Beneficios

### 1. **DRY (Don't Repeat Yourself)**
- ✅ Elimina código duplicado entre componentes
- ✅ Lógica centralizada y reutilizable
- ✅ Mantenimiento simplificado

### 2. **Separation of Concerns**
- ✅ Hook se encarga solo de la sincronización temporal
- ✅ Componentes se enfocan en su lógica específica
- ✅ Testeo independiente de cada parte

### 3. **Performance**
- ✅ Cleanup automático previene memory leaks
- ✅ Referencias optimizadas con `useRef`
- ✅ Dependencies correctas en `useEffect`

### 4. **Developer Experience**
- ✅ API simple y intuitiva
- ✅ TypeScript-friendly
- ✅ Documentación completa

## 🚀 Casos de Uso

### Ideales para este Hook
- ✅ **Cotizaciones de monedas** (ExchangeRatePanel, BROUPanel)
- ✅ **Datos de mercado** que se actualizan cada hora
- ✅ **Reportes periódicos** con sincronización horaria
- ✅ **Dashboards** que necesitan datos frescos cada hora

### No Recomendado para
- ❌ **Actualizaciones en tiempo real** (usar WebSockets)
- ❌ **Intervalos menores a 1 hora** (usar `setInterval` directo)
- ❌ **Actualizaciones irregulares** (usar eventos específicos)

## 📁 Estructura de Archivos

```
frontend/src/
├── hooks/
│   └── useHourlySyncedUpdate.js     # Hook principal
├── test/hooks/
│   └── useHourlySyncedUpdate.test.js # Tests del hook
├── components/
│   ├── ExchangeRatePanel.jsx        # Usa el hook
│   └── BROUPanel.jsx               # Usa el hook
└── docs/
    └── HOURLY_SYNCED_UPDATE_HOOK.md # Esta documentación
```

## 🔮 Futuras Mejoras

### Posibles Extensiones
- [ ] **Configuración de intervalo**: Permitir otros intervalos (30min, 2h, etc.)
- [ ] **Timezone awareness**: Sincronización con zonas horarias específicas
- [ ] **Retry logic**: Reintentos automáticos en caso de error
- [ ] **Pause/Resume**: Pausar y reanudar actualizaciones
- [ ] **Analytics**: Tracking de ejecuciones y errores

---

**El hook `useHourlySyncedUpdate` es un ejemplo de cómo aplicar buenas prácticas de React para crear código reutilizable, testeable y mantenible.** 🎉 