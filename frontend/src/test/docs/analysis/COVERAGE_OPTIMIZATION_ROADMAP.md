# 🚀 Roadmap de Optimización de Coverage - Objetivo 95-100%

## 📊 **Estado Actual del Coverage (Enero 2025)**

### **Métricas Actuales**
- **Statements**: **92.37%** (Objetivo: 95%+ | Gap: **2.63%**)
- **Branches**: **68.59%** (Objetivo: 80%+ | Gap: **11.41%**)
- **Functions**: **77.03%** (Objetivo: 85%+ | Gap: **7.97%**)
- **Lines**: **92.37%** (Objetivo: 95%+ | Gap: **2.63%**)

### **Tests Status**
- **Test Files**: 21 passed ✅
- **Tests**: 637 passed ✅
- **Failed Tests**: 0 ✅
- **Execution Time**: ~18.5 segundos

---

## 🎯 **Análisis de Oportunidades por Componente**

### **🔴 PRIORIDAD CRÍTICA - App.jsx (70.48% statements)**

**Impacto**: Este componente tiene el mayor potencial de mejora (708 líneas)

**Líneas sin cobertura identificadas:**
- **369-372, 385-388, 401-404, 407-420**: Funcionalidades específicas de refresh
- **428-436**: Estados de carga de i18n más complejos  
- **512, 517-522**: Paneles de información y error específicos

**Estrategia de Mejora:**
```javascript
// Tests adicionales necesarios:
1. Estados edge de refresh con errores específicos
2. Combinaciones de datos de app info incompletos
3. Estados de i18n loading con diferentes timeouts
4. Error boundaries con diferentes tipos de errores
5. Navegación con estados de error persistentes
```

**Estimación de Impacto**: +5-8% en coverage general

---

### **🟡 PRIORIDAD ALTA - ExchangeResultsDisplay.jsx (90.21% statements)**

**Líneas sin cobertura:**
- **56-64**: Lógica `groupByCurrency` con casos edge
- **151-198**: Vista mobile con diferentes configuraciones
- **565**: Condicionales de average rate

**Estrategia:**
```javascript
// Tests específicos para mobile view
describe('Mobile View Edge Cases', () => {
  it('should handle groupByCurrency with mixed currencies', () => {
    // Test con datos complejos de múltiples monedas
  })
  
  it('should handle mobile responsive breakpoints', () => {
    // Test con diferentes screen sizes
  })
})
```

**Estimación de Impacto**: +1-2% en coverage general

---

### **🟡 PRIORIDAD ALTA - SearchForm.jsx (94.59% statements)**

**Líneas sin cobertura:**
- **203-204, 207-208**: Validaciones edge
- **221-224**: Manejo de fechas límite
- **238, 254-255, 260**: Estados de error específicos
- **272-275, 289**: Cleanup y edge cases

**Problemas Identificados:**
- ⚠️ **Warnings de `act()`**: Múltiples warnings sobre state updates
- Necesita wrapping con `act()` en tests de state changes

**Estrategia:**
```javascript
// Corregir warnings de act()
await act(async () => {
  fireEvent.change(dateInput, { target: { value: '2024-01-01' } })
})
```

**Estimación de Impacto**: +1% en coverage general

---

### **🟡 PRIORIDAD MEDIA - URSearchForm.jsx (91.32% statements)**

**Líneas sin cobertura:**
- **442-443, 455-458**: Validaciones de período
- **473, 495-496**: Estados edge
- **507-510, 517-518, 525**: Cleanup y error handling

**Problemas Similares**: También tiene warnings de `act()`

**Estimación de Impacto**: +0.5% en coverage general

---

## 🔧 **Análisis de Services (89.67% promedio)**

### **api.js (86.66% statements)**
**Líneas sin cobertura**: 12-13, 52-53, 61-74
- Manejo de errores de configuración
- Fallback mechanisms no testeados completamente

### **exchangeService.js (90.21% statements)**  
**Líneas sin cobertura**: 11-12, 51-52, 60-73
- Error handling específico
- Edge cases de conexión

### **urService.js (92.3% statements)**
**Líneas sin cobertura**: 28-34, 48-49
- Configuración de endpoints
- Timeout handling

**Estrategia para Services:**
```javascript
// Tests de error scenarios más completos
describe('Service Error Handling', () => {
  it('should handle timeout scenarios', () => {
    globalThis.setupBranchTest('timeout')
    // Test timeout específico
  })
  
  it('should handle connection refused', () => {
    globalThis.setupBranchTest('network_error')
    // Test network errors
  })
})
```

---

## 📈 **Estrategia de Mejora de Branch Coverage (68.59% → 80%+)**

### **Análisis de Branches No Cubiertas**

**Principales oportunidades:**
1. **Condicionales de Error**: Muchos `if/else` de error handling no testeados
2. **Estados de Loading**: Combinaciones de loading states
3. **Validaciones**: Edge cases en validaciones de formularios
4. **Responsive Logic**: Branches de desktop/mobile no completamente cubiertas

### **Técnicas para Mejorar Branch Coverage**

**1. Usar Flags Globales del Setup.jsx:**
```javascript
// Aprovechar el sistema existente en setup.jsx
globalThis.setupBranchTest('network_error')
globalThis.setupBranchTest('server_error')
globalThis.setupBranchTest('timeout')
globalThis.setupBranchTest('i18n_loading')
```

**2. Tests de Estados Combinados:**
```javascript
describe('Combined State Testing', () => {
  it('should handle loading + error state', () => {
    // Test estados combinados
  })
  
  it('should handle mobile + error + loading', () => {
    // Test múltiples branches simultáneas
  })
})
```

**3. Validaciones Edge Case:**
```javascript
describe('Validation Edge Cases', () => {
  it('should handle null/undefined inputs', () => {
    // Test branches de validación
  })
  
  it('should handle malformed data', () => {
    // Test error branches
  })
})
```

---

## 🛠️ **Plan de Implementación Detallado**

### **FASE 1: App.jsx Optimization (Semana 1)**
**Objetivo**: 70.48% → 85%+ statements

**Tareas Específicas:**
1. **Expandir tests de refresh** (líneas 369-372, 385-388, 401-404, 407-420)
   ```javascript
   describe('Refresh Edge Cases', () => {
     it('should handle partial refresh failures')
     it('should handle refresh timeout scenarios')
     it('should handle refresh with invalid responses')
   })
   ```

2. **Tests de i18n loading states** (líneas 428-436)
   ```javascript
   describe('I18n Loading States', () => {
     it('should handle i18n loading timeout')
     it('should handle i18n loading errors')
     it('should handle i18n partial loading')
   })
   ```

3. **Tests de app info panels** (líneas 512, 517-522)
   ```javascript
   describe('App Info Display Edge Cases', () => {
     it('should handle incomplete app info')
     it('should handle malformed app info')
     it('should handle app info errors')
   })
   ```

**Estimación**: 3-4 días de trabajo

---

### **FASE 2: Form Components Optimization (Semana 2)**
**Objetivo**: Resolver warnings de `act()` y mejorar coverage

**Tareas:**
1. **Corregir warnings de act() en SearchForm.jsx**
2. **Corregir warnings de act() en URSearchForm.jsx**
3. **Agregar tests de edge cases específicos**

**Template para correcciones:**
```javascript
// ANTES (con warning)
fireEvent.change(input, { target: { value: 'test' } })

// DESPUÉS (sin warning)
await act(async () => {
  fireEvent.change(input, { target: { value: 'test' } })
})
```

**Estimación**: 2-3 días de trabajo

---

### **FASE 3: Services & Branch Coverage (Semana 3)**
**Objetivo**: 89.67% → 95%+ en services, 68.59% → 80%+ en branches

**Tareas:**
1. **Completar coverage de api.js, exchangeService.js, urService.js**
2. **Implementar tests de error scenarios completos**
3. **Tests de branch coverage usando flags globales**

**Estimación**: 2-3 días de trabajo

---

### **FASE 4: ExchangeResultsDisplay & Polish (Semana 4)**
**Objetivo**: Completar componentes restantes y optimización final

**Tareas:**
1. **Mobile view testing completo**
2. **GroupByCurrency edge cases**
3. **Optimización final y documentación**

**Estimación**: 1-2 días de trabajo

---

## 📋 **Recursos y Herramientas Disponibles**

### **Patrones Exitosos Documentados**
- ✅ **BROUPanel**: 100% coverage (20/20 tests) - Usar como referencia
- ✅ **Setup.jsx**: Sistema de flags globales para branch testing
- ✅ **es.json**: Constantes de internacionalización reales
- ✅ **Documentación**: 20+ documentos de patrones exitosos

### **Herramientas del Setup.jsx**
```javascript
// Sistema de flags para branch testing
globalThis.setupBranchTest(scenario)
globalThis.__TEST_NETWORK_ERROR__
globalThis.__TEST_SERVER_ERROR__
globalThis.__TEST_I18N_LOADING__
// ... y más flags disponibles
```

### **Mocks Inteligentes Disponibles**
- ✅ **Axios mock** con scenarios realistas
- ✅ **I18n mock** con traducciones reales
- ✅ **Toast mock** con error handling
- ✅ **Date-fns mock** con casos edge
- ✅ **React-hook-form mock** funcional

---

## 🎯 **Objetivos Cuantificados**

### **Objetivo Final (4 semanas)**
- **Statements**: 92.37% → **98%+** (+5.63%)
- **Branches**: 68.59% → **85%+** (+16.41%)
- **Functions**: 77.03% → **90%+** (+12.97%)
- **Lines**: 92.37% → **98%+** (+5.63%)

### **Hitos Intermedios**
- **Semana 1**: Statements 92.37% → 95%+
- **Semana 2**: Statements 95%+ → 96%+, Branches 68% → 75%+
- **Semana 3**: Branches 75%+ → 80%+, Functions 77% → 85%+
- **Semana 4**: Pulimiento final hacia 98%+ en todas las métricas

---

## ⚠️ **Riesgos y Consideraciones**

### **Riesgos Identificados**
1. **Warnings de act()**: Pueden generar ruido en los tests
2. **Timing issues**: Tests asincrónicos pueden ser frágiles
3. **Mocks complejos**: Pueden ocultar bugs reales

### **Mitigaciones**
1. **Seguir patrones documentados** en `/docs/success-reports/`
2. **Usar flags globales** del setup.jsx para consistencia
3. **Testear incrementalmente** para evitar regresiones

### **Criterios de Éxito**
- ✅ **0 tests fallando**
- ✅ **0 warnings de act()**
- ✅ **Tiempo de ejecución < 25 segundos**
- ✅ **Coverage > 95% statements**
- ✅ **Coverage > 80% branches**

---

## 📊 **Métricas de Seguimiento**

### **Dashboard de Progreso**
```bash
# Comando para tracking diario
npm run test:coverage | grep -E "(All files|% Stmts|% Branch)"

# Objetivo diario
echo "Target: Statements 95%+, Branches 80%+, Functions 85%+"
```

### **Reportes Semanales**
- **Lunes**: Baseline y objetivos de la semana
- **Miércoles**: Checkpoint intermedio
- **Viernes**: Reporte de progreso y ajustes

---

## 🏆 **Conclusión**

El proyecto está **muy cerca del objetivo del 95%** con un excelente foundation:
- ✅ **637 tests pasando**
- ✅ **21 archivos de test funcionando**
- ✅ **Sistema de mocks robusto**
- ✅ **Documentación completa de patrones exitosos**

**El gap de solo 2.63% en statements es completamente alcanzable** siguiendo los patrones exitosos ya establecidos y documentados en el proyecto.

**Próximo paso inmediato**: Comenzar con la optimización de App.jsx que tiene el mayor impacto potencial.

---

*Documento creado: Enero 2025*  
*Basado en: Coverage actual 92.37%, Documentación existente, Patrones exitosos de BROUPanel* 