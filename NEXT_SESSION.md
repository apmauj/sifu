# Próxima Sesión - SIFU Roadmap & Planning

## 🧭 Nueva Iniciativa Activa (2026-04-19)

### Re-arquitectura incremental V2 (desde develop)

Estado: Fase 4 iniciada

- Rama programa: `chore/arch-reorg-v2`
- Roadmap: `docs/ARCH_REORG_V2_ROADMAP.md`
- Checklist Fase 0: `docs/ARCH_REORG_V2_PHASE0_CHECKLIST.md`

Objetivo:
- Consolidar fronteras de capas en `src/`, reducir acoplamiento y endurecer guardrails de arquitectura sin cambios big-bang.

Proximo paso operativo:
- Ejecutar cortes pequenos de cleanup para remover compatibilidad residual no usada (shims/aliases), manteniendo `src/domain/services.py` solo como capa transicional externa hasta su retiro final.
- Ruta UR completada: aliases `año/mes/valor` removidos de `URValue`/`URRecord`; tests y assertions legacy retirados.
- Guardia CI en `backend-tests` endurecida: no se permiten referencias legacy en tests.
- Changelog de remoción final (`v1.5.0`) agregado en `CHANGELOG_2026-04-19.md`.
- Cierre pendiente: ejecutar CI completa en PR.

## 🚨 P0 - Primera Tarea Pendiente (Node 24 en GitHub Actions)

Objetivo: migrar y validar workflows para ejecución estable con Node 24 antes de la fecha de corte de Node 20.

### Alcance inmediato (sesión siguiente)
1. Inventariar workflows que usan acciones JavaScript (`actions/checkout`, `actions/upload-artifact`, `actions/setup-*`). ✅
2. Actualizar versiones a releases compatibles con Node 24 en todos los workflows activos. ✅
3. Ejecutar prueba controlada con `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` para detectar incompatibilidades tempranas. ✅
4. Corregir warnings/fallos y volver a correr `CI/CD`, `Security Audit`, `Update Tunnel`, `Frontend-Backend Link Check`. ✅ Parcial (CI/CD y Security Audit verificados; pendientes validaciones manuales de workflows operativos no frecuentes)
5. Documentar resultado y cerrar con checklist de validación en roadmap técnico. ✅

### Criterio de cierre
- 0 warnings de deprecación Node 20 en jobs principales. ✅
- Workflows críticos en verde con SHA de la rama de migración. ✅

### Pendiente inmediato para cierre total de la migración
1. Abrir PR de la rama `chore/node24-actions-migration-plan` y solicitar aprobación.
2. Ejecutar una corrida manual de `update-tunnel.yml` en rama para certificar runtime Node 24 en recuperación de túnel.
3. Ejecutar corridas manuales de `frontend-backend-link-check.yml` y `brou-health-monitor.yml` (con flags habilitadas) para validación final operativa.

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

### ✅ Completado - Modernización Dashboard & I18n (2025-09-06)

#### Alcance
- Refactor completo de internacionalización en Dashboard (eliminación de cadenas hardcodeadas)
- Integración de patrón de traducción dinámica para mensajes backend (salud, cachés BCU/BROU, recursos del sistema)
- Fusión profunda (deep merge) de locales embebidos + remotos con modo determinista para tests (`forceEmbedded`)
- Capitalización y normalización de estados (Healthy/Warning/Critical) con nuevas keys `dashboard.status.*`
- Adición de tooltips explicativos (ℹ️) para secciones y cada check (`dashboard.tooltips.*`)
- Nuevo nombre y soporte visual para `brou_cache` en checks
- Localización de mensaje de éxito de base de datos (`database_ok`)
- Eliminación de panel redundante de “datos técnicos” y limpieza de claves huérfanas
- Layout compacto: estado general + última actualización en línea y grid responsivo
- Traducciones sincronizadas en `src/locales/*` y `public/i18n/*` manteniendo paridad y sin orphans

#### Archivos Clave Modificados
- `frontend/src/components/Dashboard.jsx`
- `frontend/src/contexts/I18nContext.jsx` (previa sesión, soporte patrones backend)
- `frontend/src/locales/{es,en,pt}.json` + `frontend/public/i18n/{es,en,pt}.json`
- Tests de arquitectura i18n (sin cambios funcionales, siguen pasando)

#### Resultados
- ✅ 100% de textos del Dashboard localizables
- ✅ Tooltips semánticos añadidos sin dependencias extras
- ✅ Sin claves huérfanas (tests de orphans/consistency green)
- ✅ Compatibilidad mantenida (sin ruptura de respuestas backend)
- ✅ Preparado para extender a otras vistas reutilizando patrón de tooltips

#### Mejora Adicional (Post refinamiento cache panel - 2025-09-06)
Implementadas optimizaciones puntuales tras la modernización principal:
- Panel unificado de cachés BROU + BCU (eliminando cards duplicadas y ruído visual)
- Cabeceras totalmente internacionalizadas (`dashboard.cache_panel.headers.*`)
- Edad de caché mostrada en formato relativo localizado (`dashboard.cache_panel.age_relative`) sin exponer TTL duro
- Formato horario 24h forzado en zona América/Montevideo (UTC‑3) para coherencia operativa
- Limpieza de claves huérfanas heredadas de paneles previos (suite vuelve a verde 600/600)
- Base preparada para eventualmente añadir métrica backend explícita de edad si se requiere (actualmente calculado en frontend)

#### Próximas Oportunidades Relacionadas (No ejecutadas aún)
- Añadir monitoreo de latencia por check y exponer thresholds en UI
- Internacionalizar mensajes en otros paneles menores (si quedan rezagos)
- Generar documentación automática de claves i18n críticas para QA

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

### **Fase 2: Mejoras en Frontend BROU / Cache**
3. **Detalle BROU Full (pendiente)**
   - Consumir `?full=true` (solo se usa modo compacto actualmente)
   - Mostrar metadata adicional (fuente / mensaje backend si aplica)
   - Opcional: badge diferenciando origen (cache vs fresh fetch)

4. **Métricas de Edad de Caché (parcial)**
   - FRONTEND: Edad relativa ya implementada ✅
   - BACKEND: Exponer `brou_cache_age_seconds` y `bcu_cache_age_seconds` en `/api/metrics` (pendiente)
   - Health: confirmar si freshness ya cacheada 30s cubre necesidad o añadir warning thresholds configurables

### **Fase 3: Calidad y Documentación**
5. **Unificación de Terminología Exchange**
   - Revisar documentación de endpoints exchange
   - Estandarizar términos entre INE/BCU/BROU
   - Actualizar ejemplos de API con casos reales

### **Fase 4: Seguridad y Autenticación Avanzada**

#### ✅ **6. Implementación de 2FA (TOTP) - COMPLETADO (2025-10-11)**
   
   **Alcance Implementado:**
   - ✅ Backend SimpleTOTP: verificación de códigos de 6 dígitos con ventana de 30s
   - ✅ 5 endpoints REST: `/api/monitoring/verify`, `/api/monitoring/status`, `/api/monitoring/setup`, `/api/monitoring/health`, `/api/monitoring/session`
   - ✅ Gestión de sesiones en memoria (UUID tokens, 1 hora de duración configurable)
   - ✅ 20 tests backend pasando (verificación, sesiones, rate limiting)
   - ✅ Frontend: Modal `MonitoringAccess` integrado con click en ❤️ del footer
   - ✅ i18n completo: traducciones en ES/EN/PT para modal y mensajes
   - ✅ Página de setup estática: `/static/totp-setup.html` con QR code y prueba de códigos
   - ✅ Protección producción: endpoint `/setup` solo disponible en `ENVIRONMENT=development`
   - ✅ Documentación completa: `TOTP_SETUP.md` con instrucciones dev/prod, configuración Authy/Google Authenticator
   - ✅ Session storage: tokens persisten 1 hora en cliente, verificación automática antes de mostrar dashboard
   
   **Enfoque Simplificado:**
   - Sin base de datos de usuarios (authentication sin autorización granular)
   - Secret único compartido (apropiado para uso personal/admin único)
   - Rate limiting mediante middleware existente (no específico TOTP)
   
   **Archivos Clave:**
   - Backend: `simple_totp.py` (198 líneas), endpoints en `main.py` (líneas 1978-2094)
   - Frontend: `MonitoringAccess.jsx` + `MonitoringAccess.css`, integración en `App.jsx`
   - Tests: `tests/test_simple_totp.py` (20 tests)
   - Docs: `TOTP_SETUP.md`, secrets en `.env` y `.env.docker`
   - i18n: `frontend/src/locales/{es,en,pt}.json` (sección `monitoring`)
   
   **Pendiente (Opcional):**
   - Recovery codes (no implementado por simplicidad del caso de uso)
   - Tests frontend para `MonitoringAccess` component
   - Almacenamiento persistente de sesiones (actualmente en memoria, se pierden al restart)
   
   **Referencias:**
   - Documentación setup: `TOTP_SETUP.md`
   - Dependencias: `pyotp==2.9.0`, `qrcode[pil]==7.4.2` en `requirements-core.txt`
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
- **Test Suite Health**: 600/600 ✅ (incluye nuevas claves i18n y refactor Dashboard)
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
3. **Actualizar panel BROU frontend** (3-4 horas) – incorporar frescura cache y reutilizar tooltips
4. **Exponer métricas edad caché** (1-2 horas) – `*_cache_age_seconds` en `/api/metrics` y usar thresholds para color de estado
5. **Revisar documentación exchange** (1-2 horas) – reflejar nuevos estados y naming unificado
6. (Opcional) **Generar script de auditoría i18n** que liste claves sin uso y diferencias entre src/public

## 📝 Notas para Continuidad

- Mantener enfoque en calidad y automatización
- Priorizar estabilidad sobre nuevas features
- Documentar todas las decisiones técnicas tomadas
- Considerar impacto en UX en cada cambio
- Mantener compatibilidad backward en APIs

---

### ✅ Completado - Ingesta Continua Fines de Semana + Corrección Datos Faltantes (2025-09-07)

#### Alcance
- Ajuste de `job_ui_refresh` eliminando restricción de días hábiles (antes se salteaban sábados/domingos generando huecos)
- Ajuste de `data_guard` para considerar fines de semana (si `latest_ui.date < today` después de 02:30 se fuerza refresh)
- Verificación manual de Excel INE: presencia de filas 2025-09-05..08 (valores existentes no insertados previamente)
- Script interno ejecutado dentro del contenedor para refrescar e insertar registros faltantes (30 nuevos registros procesados)
- Confirmada persistencia de 2025-09-06, 2025-09-07 y 2025-09-08 tras refresh manual
- Revisión de por qué curl externo fallaba: puerto 8000 no estaba publicado; se decidió mantener aislamiento local

#### Cambios Clave
- `main.py`: eliminado early-return por non-business-day en `job_ui_refresh`
- `main.py`: remoción de condición `weekday() < 5` en data guard UI
- `docker-compose.yml`: binding de backend limitado a loopback `127.0.0.1:8000` para evitar acceso externo accidental

#### Resultado
- Gaps de fines de semana eliminados (ingesta futura cubrirá sábados y domingos)
- Base lista para mostrar siempre valor de “hoy” si publicado por INE aun en fin de semana
- Riesgo de inconsistencia entre entorno local y producción reducido (documentado el ajuste necesario para imagen publicada)

### 📌 Ajustes Pendientes / Nueva Prioridad (Rebalanceado 2025-09-07)
1. Externalizar validación de continuidad de fechas UI (script que alerta si falta un día dentro de últimos 14) – priorizar Fase 1.1
2. Añadir métrica `ui_latest_age_seconds` y `ui_gap_detected` a `/api/metrics` para dashboards futuros
3. Endpoint debug opcional `/api/ui/gaps/recent` (solo si se detectan huecos) – detrás de flag

---

**Última actualización**: 2025-09-07 (post corrección fines de semana & aislamiento puerto)
**Suite de Tests**: ✅ 600/600 pasando
**Estado General**: 🟢 Saludable; siguiente foco: automatización túnel + monitoreo + métricas de frescura

---

### ✅ Completado - Monitoreo de Frescura UI (2025-09-07)

#### Alcance
- Nuevo health check `ui_freshness` en backend (`health_checks.py`) con reglas:
   - Healthy: valor de hoy presente, o valor de ayer antes de ventana 03:00 local, o fechas futuras (permitidas).
   - Warning: falta valor de hoy pasada la ventana (gap = 1 día).
   - Critical: gap de 2+ días o sin registros.
- Métricas añadidas en `/api/metrics`: bloque `ui_freshness` (`ui_latest_date`, `ui_dias_gap`, `ui_latest_age_seconds`, `ui_gap_detected`, `future`, `ui_dias_ahead`).
- Panel frontend dedicado “Frescura UI” (tabla compacta) en `Dashboard.jsx` reutilizando estilos de paneles de caché.
- Traducciones e i18n: claves añadidas `dashboard.checks.names.ui_freshness`, `dashboard.tooltips.ui_freshness`, y bloque `dashboard.ui_freshness_panel.*` en `es/en/pt`.
- Exclusión del check `ui_freshness` de la lista genérica de “Detalles” para evitar duplicación visual.
- Política final: cualquier fecha futura se considera válida (no warning) y se expone `dias_ahead`.

#### Cambios Clave
- `health_checks.py`: función `check_ui_freshness` + registro en `health_checker`.
- `metrics_middleware.py`: agregado bloque UI freshness lightweight.
- `frontend/src/components/Dashboard.jsx`: nuevo panel y filtrado del check en detalles.
- `frontend/src/locales/{es,en,pt}.json`: nuevas claves de nombre, tooltips y encabezados panel.

#### Resultados
- Observabilidad directa de frescura UI sin sobrecargar panel principal.
- Compatible con datasets que publican valores futuros (no genera falsos positivos).
- Base lista para extender a frescura UR / Exchange en panel conjunto futuro.

#### Próximas Extensiones (No ejecutadas aún)
1. Añadir checks análogos para UR y Exchange consolidando “Panel Fuentes Planillas”.
2. Endpoint opcional `/api/ui/gaps/recent` (solo si se detectan huecos) para soporte.
3. Alerting ligero: script o workflow que lea `/api/metrics` y notifique si `ui_gap_detected=true`.

---

**Última actualización**: 2025-09-07 (tras inclusión monitoreo frescura UI)