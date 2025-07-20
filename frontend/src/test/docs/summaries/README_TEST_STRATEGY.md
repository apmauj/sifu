# Estrategia de Fechas Dinámicas en Tests

## Problema Identificado

Inicialmente, los tests tenían fechas hardcodeadas como `'2025-06-17'`, lo que causaba varios problemas:

1. **Tests frágiles**: Los tests fallarían cuando esa fecha ya no fuera relevante
2. **Mantenimiento manual**: Requería actualización constante de fechas
3. **Falta de realismo**: No reflejaba el comportamiento real del componente

## Solución Implementada

### 1. Mocks Dinámicos en `setup.js`

**dateUtils Mock:**
```javascript
// ESTRATEGIA DE FECHAS PARA TESTS:
// Usar la fecha actual para que los tests sean dinámicos y no fallen
// cuando cambien las fechas. Esto evita tener que actualizar manualmente
// las fechas hardcodeadas en el futuro.
const today = new Date();
const todayString = today.getFullYear() + '-' + 
  String(today.getMonth() + 1).padStart(2, '0') + '-' + 
  String(today.getDate()).padStart(2, '0');

return {
  getTodayLocal: () => todayString,
  // ... otros métodos usando fecha dinámica
};
```

**date-fns Mock:**
```javascript
// ESTRATEGIA DE FECHAS PARA TESTS:
// Usar fecha actual para consistencia con el mock de dateUtils.
// Esto evita problemas de fechas hardcodeadas que fallan en el futuro.
const today = new Date();
```

### 2. Beneficios de la Estrategia

#### ✅ **Sostenibilidad a Largo Plazo**
- Los tests funcionarán mañana, la semana próxima, y el año próximo
- No requieren mantenimiento manual de fechas
- Se adaptan automáticamente al paso del tiempo

#### ✅ **Realismo**
- Los componentes reciben fechas que reflejan el comportamiento real
- Los tests validan la lógica, no datos específicos
- Mayor confianza en que el código funciona en producción

#### ✅ **Consistencia**
- Todos los mocks usan la misma fecha base (fecha actual)
- Eliminación de conflictos entre diferentes librerías de fechas
- Comportamiento predecible en todos los tests

### 3. Casos Especiales

Para tests que requieren fechas específicas (ej: validar formateo de fechas históricas), se mantienen valores fijos pero documentados:

```javascript
// Para fechas específicas de test, devolver valores consistentes
const dateStr = date.toISOString();
if (dateStr.includes('2024-01-01')) return '01/01/2024';
if (dateStr.includes('2024-12-25')) return '24/12/2024';
```

### 4. Mejores Prácticas Aplicadas

1. **DRY (Don't Repeat Yourself)**: Lógica de fecha centralizada en mocks
2. **YAGNI (You Aren't Gonna Need It)**: No over-engineering, solución simple
3. **Mantenibilidad**: Código que se mantiene solo
4. **Testabilidad**: Tests que validan comportamiento, no datos específicos

### 5. Alternativas Consideradas

#### ❌ **Fechas Hardcodeadas**
```javascript
// Problemático:
getTodayLocal: () => '2025-06-17'
```
**Problemas**: Frágil, requiere mantenimiento manual

#### ❌ **Mocks Complejos con Variables de Entorno**
```javascript
// Over-engineering:
const testDate = process.env.TEST_DATE || getCurrentDate();
```
**Problemas**: Complejidad innecesaria, dificulta debugging

#### ✅ **Fechas Dinámicas Simples** (Solución Elegida)
```javascript
// Óptimo:
const today = new Date();
const todayString = formatDate(today);
```
**Beneficios**: Simple, mantenible, realista

## Conclusión

Esta estrategia asegura que los tests:
- **Funcionen indefinidamente** sin mantenimiento manual
- **Reflejen el comportamiento real** del código en producción  
- **Sean mantenibles** y fáciles de entender
- **Sigan las mejores prácticas** de testing

Los tests ahora validan la **lógica y comportamiento** de los componentes, no datos específicos, lo que es exactamente lo que deben hacer. 