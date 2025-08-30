# 🗂️ Plan de Organización del Proyecto SIFU

**Fecha:** 2025-08-30
**Versión:** 1.0
**Estado:** Planificación

## 🎯 Objetivos

- Organizar archivos según mejores prácticas de estructura de proyectos Python
- Eliminar archivos duplicados y legacy
- Implementar principios DRY (Don't Repeat Yourself)
- Mejorar mantenibilidad y navegación del código
- Preparar base para escalabilidad futura

## 📁 Estructura Propuesta

```
sifu/
├── config/                    # 🆕 Archivos de configuración
│   ├── env/
│   │   ├── .env
│   │   ├── .env.production
│   │   └── .env.template
│   └── nginx/
│       ├── nginx.conf
│       └── nginx.https.conf
├── docs/                      # 📚 Documentación organizada
│   ├── api/
│   ├── architecture/
│   ├── deployment/
│   ├── security/
│   └── user-guides/
├── logs/                      # 📋 Logs y auditoría
│   ├── app/
│   ├── security/
│   └── audit/
├── scripts/                   # 🛠️ Scripts organizados
│   ├── deploy/
│   ├── setup/
│   ├── util/
│   └── archive/
├── src/                       # 🆕 Código fuente organizado
│   ├── api/
│   ├── core/
│   ├── services/
│   └── utils/
├── tests/                     # 🧪 Tests organizados
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
└── [archivos root esenciales]
```

## 🔄 Cambios Específicos

### 📋 **ORG-001: Scripts de Despliegue**
**Archivos a mover:**
- `docker_update_tunnel_secret.ps1` → `scripts/deploy/`
- `run_tunnel_backend.ps1` → `scripts/deploy/`
- `setup_https.py` → `scripts/setup/`
- `setup_production.py` → `scripts/setup/`
- `setup_rbac.py` → `scripts/setup/`
- `start_secure.py` → `scripts/setup/`
- `validate_deploy.py` → `scripts/setup/`
- `verify_security.py` → `scripts/setup/`

### 📚 **ORG-002: Documentación**
**Archivos a mover:**
- `SECURITY_CONFIG.md` → `docs/security/`
- `NEXT_SESSION.md` → `docs/` (eliminar duplicado)
- `pip_audit_*.json` → `docs/security/`

**Archivos a convertir:**
- `IMPROVEMENT_PLAN.xml` → `docs/PLAN_ACCION_README.md`
- `PLAN_ACCION.xml` → Markdown

### 🧪 **ORG-003: Archivos de Testing**
**Archivos a mover:**
- `async_test.py` → `tests/unit/`
- `main_test.py` → `tests/unit/`
- `simple_test.py` → `tests/unit/`
- `test_all_checks.py` → `tests/integration/`
- `test_brou_monitoring.py` → `tests/integration/`
- `test_coverage_report.py` → `tests/unit/`
- `test_health_checks.py` → `tests/unit/`
- `test_run_all.py` → `tests/integration/`
- `test_security.py` → `tests/unit/`
- `test_server.py` → `tests/integration/`

### ⚙️ **ORG-004: Configuración y Logs**
**Nuevas carpetas:**
- `config/env/` - Todos los archivos `.env*`
- `config/nginx/` - Configuración nginx
- `logs/app/` - Logs de aplicación
- `logs/security/` - Logs de seguridad
- `logs/audit/` - Archivos de auditoría

### 🔧 **ORG-005: Optimización DRY**

#### Constantes a Consolidar:
```python
# En constants.py - Consolidar:
EXCHANGE_RATES = {
    'USD': 'Dólar USA',
    'EUR': 'Euro',
    'ARS': 'Peso Arg.',
    'BRL': 'Real'
}

# En lugar de tenerlos duplicados en:
# - exchange_processor.py
# - models.py
# - frontend constants
```

#### Helpers a Crear:
```python
# src/utils/date_utils.py
def format_date_for_display(date_str):
    """Formato consistente para fechas en UI"""

# src/utils/validation_utils.py
def validate_currency_code(code):
    """Validación centralizada de códigos de moneda"""

# src/utils/api_utils.py
def make_external_request(url, timeout=30):
    """Wrapper consistente para requests externos"""
```

### 🧹 **ORG-006: Limpieza de Archivos**

#### Archivos a Eliminar:
- `NEXT_SESSION.md` (duplicado)
- `package-lock.json` (pertenece al frontend)
- Archivos temporales de debugging
- Scripts legacy no utilizados

#### Archivos a Revisar:
- `sifu.log` → `logs/app/`
- `security_audit.log` → `logs/security/`
- `test_security.log` → `logs/`

### 📖 **ORG-007: Documentación de Arquitectura**

Actualizar `docs/ARCHITECTURE.md` con:
- Nueva estructura de carpetas
- Convenciones de nomenclatura
- Guías de contribución
- Decisiones de diseño DRY

## ✅ Checklist de Verificación

### 📁 Estructura
- [ ] Todas las carpetas creadas según plan
- [ ] Archivos movidos correctamente
- [ ] Imports actualizados en todo el código
- [ ] Tests pasan después de reorganización

### 🔧 DRY Implementation
- [ ] Constantes consolidadas en `constants.py`
- [ ] Helpers reutilizables creados
- [ ] Código duplicado eliminado
- [ ] Funciones utilitarias documentadas

### 🧹 Limpieza
- [ ] Archivos legacy eliminados
- [ ] Duplicados removidos
- [ ] `.gitignore` actualizado
- [ ] Documentación actualizada

## 📊 Métricas de Éxito

- **Estructura clara:** 100% de archivos en carpetas apropiadas
- **DRY Score:** > 90% de código reutilizable
- **Archivos eliminados:** > 20 archivos legacy/duplicados
- **Tiempo de navegación:** Reducido en > 50%

## ⚠️ Riesgos y Mitigaciones

### 🚨 **Riesgo: Imports rotos**
**Mitigación:** Ejecutar tests completos después de cada cambio, actualizar imports sistemáticamente

### 🚨 **Riesgo: Funcionalidad perdida**
**Mitigación:** Backup completo antes de cambios, validación funcional en cada paso

### ⚠️ **Riesgo: Tiempo de reorganización**
**Mitigación:** Hacer cambios incrementales, commit frecuente, rollback plan

## 📅 Plan de Implementación

### Semana 13: Estructura Base
1. Crear nuevas carpetas
2. Mover scripts de despliegue
3. Reorganizar documentación
4. Mover archivos de test

### Semana 14: Optimización
1. Implementar DRY en constantes
2. Crear helpers reutilizables
3. Limpiar archivos legacy
4. Actualizar documentación

## 🎯 Beneficios Esperados

- **Mantenibilidad:** +60% más fácil encontrar archivos
- **Colaboración:** Estructura clara para nuevos developers
- **Productividad:** -40% tiempo buscando código
- **Calidad:** -30% bugs por código duplicado
- **Escalabilidad:** Base sólida para crecimiento futuro

---

*Plan de organización generado para roadmap SIFU - Fase ORG (Semanas 13-14)*
