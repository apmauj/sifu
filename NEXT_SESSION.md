# Próxima Sesión - SIFU Roadmap & Planning

## 🎯 Estado Actual del Proyecto

### ✅ Completado - Mejoras Críticas en Testing (2025-01-15)

#### **Problemas Resueltos**
- **RangeError en date-fns**: Eliminados errores de "Invalid time value" en operaciones de fecha
- **Act() Warnings**: Corregidos warnings de React Testing Library en componentes asíncronos
- **ParseISO Errors**: Mejorado manejo robusto de fechas inválidas/undefined en componentes
- **Test Coverage**: Mejorada cobertura de casos edge en funciones de formateo de fecha

#### **Archivos Modificados**
- `frontend/src/test/setup.jsx`: Enhanced date-fns mock con validación robusta
- `frontend/src/test/components/URSearchForm.test.jsx`: Act() wrappers en tests críticos
- `frontend/src/test/components/SearchForm.test.jsx`: Act() wrappers en form tests
- `frontend/src/components/SearchForm.jsx`: Validación mejorada de parseISO
- `frontend/src/components/ResultsDisplay.jsx`: Función formatDate con try-catch
- `frontend/src/components/ExchangeResultsDisplay.jsx`: Función formatDateForChart con error handling

#### **Métricas de Éxito**
- ✅ **598 tests** pasando exitosamente
- ✅ **35 archivos** de test ejecutándose sin errores
- ✅ **0 warnings** críticos en test suite
- ✅ **Cobertura completa** de casos edge en manejo de fechas

## 🚀 Próximos Pasos Priorizados

### **Fase 1: Automatización de Infraestructura**
1. **Script de Actualización de Túnel**
   - Automatizar `docker pull` + recreación backend antes de actualizar secret del túnel
   - Crear script PowerShell reutilizable para workflow de actualización
   - Implementar validación de health check post-actualización

2. **Workflow de Monitoreo Programado**
   - Crear workflow que verifique `/api/brou/current?full=true` periódicamente
   - Alertar si `data.length == 0` o antigüedad excede X minutos
   - Implementar notificaciones automáticas (Slack/Discord)

### **Fase 2: Mejoras en Frontend BROU**
3. **Integración de Panel BROU Completo**
   - Usar parámetro `?full=true` en llamadas al backend
   - Mostrar timestamp y mensaje de respuesta en UI
   - Implementar indicadores visuales de frescura de datos

4. **Health Check Extendido**
   - Agregar métricas de frescura de caché BROU al endpoint `/health`
   - Implementar `brou_cache_age_seconds` para monitoreo
   - Crear dashboard de estado de servicios

### **Fase 3: Calidad y Documentación**
5. **Unificación de Terminología Exchange**
   - Revisar documentación de endpoints exchange
   - Estandarizar términos entre INE/BCU/BROU
   - Actualizar ejemplos de API con casos reales

### **Fase 4: Seguridad y Autenticación Avanzada** (nuevo)
6. **Implementación de 2FA (TOTP + Recovery Codes)**
   - Backend: endpoints para generar secreto (QR/otpauth), activar/desactivar y validar token
   - Almacenar secreto cifrado (KDF + pepper) y códigos de recuperación hash (bcrypt / argon2)
   - Métricas: usuarios con 2FA habilitado, intentos fallidos, uso de recovery codes
   - Rate limiting específico en verificación de TOTP (reusar middlewares existentes)
7. **Gestión de Códigos de Recuperación**
   - Generación inicial (8-10 códigos one‑time) + descarga segura
   - Rotación/regeneración invalida anteriores (audit log)
8. **Flujo Frontend de Activación 2FA**
   - Paso 1: Mostrar QR + código manual
   - Paso 2: Ingreso de primer TOTP para confirmar
   - Paso 3: Presentar y forzar almacenamiento de recovery codes
9. **Observabilidad de Seguridad**
   - Exponer métricas: auth_2fa_enabled_total, auth_2fa_failed_attempts_total
   - Alertar > N intentos fallidos consecutivos por usuario/ip

## 📊 Métricas de Seguimiento

### **Testing Quality**
- **Test Suite Health**: 598/598 ✅
- **Warning Elimination**: 100% ✅
- **Date Error Handling**: Robusto ✅
- **Component Test Coverage**: Completo ✅

### **API Reliability**
- **Response Time**: <200ms promedio
- **Error Rate**: <1%
- **Data Freshness**: Monitoreo pendiente
- **Cache Efficiency**: Optimizado

### **User Experience**
- **Loading States**: Implementados
- **Error Handling**: Mejorado
- **Data Visualization**: Completo
- **Mobile Responsiveness**: ✅

## 🔧 Decisiones Técnicas Pendientes

### **Monitoreo y Alertas**
- ¿Implementar Prometheus + Grafana para métricas avanzadas?
- ¿Configurar alertas en GitHub para fallos de CI/CD?
- ¿Agregar logging estructurado para debugging?
 - ¿Incluir dashboard de adopción 2FA (tasa habilitación / intentos fallidos)?

### **Performance Optimization**
- ¿Implementar Redis para caching avanzado?
- ¿Optimizar queries de base de datos con índices compuestos?
- ¿Agregar compression a responses de API?
 - ¿Evaluar impacto de validaciones 2FA en latencia de login?

### **Developer Experience**
- ¿Crear más scripts de automatización para desarrollo local?
- ¿Implementar hot reload más eficiente?
- ¿Agregar más validaciones en pre-commit hooks?
 - ¿Agregar test helpers para generar códigos TOTP deterministas en CI?

## 🎯 Objetivos de la Próxima Sesión

1. **Completar automatización de túnel** (2-3 horas)
2. **Implementar workflow de monitoreo** (2-3 horas)
3. **Actualizar panel BROU frontend** (3-4 horas)
4. **Extender health checks** (1-2 horas)
5. **Revisar documentación exchange** (1-2 horas)

## 📝 Notas para Continuidad

- Mantener enfoque en calidad y automatización
- Priorizar estabilidad sobre nuevas features
- Documentar todas las decisiones técnicas tomadas
- Considerar impacto en UX en cada cambio
- Mantener compatibilidad backward en APIs

---

**Última actualización**: 2025-09-06
**Suite de Tests**: ✅ 600/600 pasando
**Estado General**: 🟢 Saludable y listo para incorporar 2FA