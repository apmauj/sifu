# SIFU Backend - Hexagonal Architecture Structure

**Date:** 2025-10-15  
**Status:** ✅ Implemented  
**Backward Compatibility:** ✅ 100% (via compatibility shims)

---

## 🏗️ Architecture Overview

SIFU backend has been reorganized into a **hexagonal (ports & adapters) architecture** following Domain-Driven Design (DDD) principles. This provides clear separation of concerns, improved testability, and better maintainability.

### Directory Structure

```
sifu/
├── src/                           # ⭐ NEW: Hexagonal architecture layers
│   ├── __init__.py
│   │
│   ├── api/                       # 🔌 Ports: REST API
│   │   ├── __init__.py
│   │   └── routers/               # Domain-based HTTP routers
│   │       ├── __init__.py
│   │       ├── ui.py              # Unidad Indexada endpoints
│   │       ├── ur.py              # Unidad Reajustable endpoints
│   │       ├── exchange.py        # Exchange rate endpoints
│   │       ├── brou.py            # BROU endpoints
│   │       └── system.py          # Health, metrics, debug endpoints
│   │
│   ├── domain/                    # 💼 Core business logic
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── pydantic_models.py     # Request/response Pydantic models
│   │   ├── services.py            # Domain services (UIService, URService, ExchangeRateService)
│   │   ├── brou_processor.py      # BROU data processor
│   │   ├── excel_processor.py     # Excel file parser
│   │   └── exchange_utils.py      # Exchange rate utilities
│   │
│   ├── infrastructure/            # 🔌 Adapters: External integrations
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy session & engine
│   │   ├── database_optimizer.py  # DB optimization utilities
│   │   ├── auth_middleware.py     # Authentication middleware
│   │   ├── auth_models.py         # Auth ORM models
│   │   ├── auth_routes.py         # Auth endpoints
│   │   ├── auth_service.py        # Authentication service
│   │   ├── https_middleware.py    # HTTPS & CSP middleware
│   │   ├── metrics_middleware.py  # Metrics collection middleware
│   │   ├── correlation_middleware.py  # Request correlation
│   │   ├── rate_limit.py          # Rate limiting
│   │   ├── circuit_breaker.py     # Circuit breaker pattern
│   │   ├── health_checks.py       # Health check implementations
│   │   └── metrics.py             # Prometheus metrics
│   │
│   ├── application/               # 🎯 Application layer
│   │   ├── __init__.py
│   │   ├── alerts.py              # Alert management
│   │   ├── bootstrap.py           # App initialization
│   │   ├── config_validator.py    # Configuration validation
│   │   ├── secret_manager.py      # Secret management
│   │   ├── secure_logging.py      # Structured logging
│   │   ├── security_monitor.py    # Security monitoring
│   │   ├── security_utils.py      # Security utilities
│   │   ├── opentelemetry_setup.py # OTel initialization
│   │   ├── generate_security_docs.py  # Security docs generation
│   │   ├── validate_deploy.py     # Deployment validation
│   │   └── verify_security.py     # Security verification
│   │
│   └── utils/                     # 🛠️ Shared utilities
│       ├── __init__.py
│       ├── constants.py           # Configuration constants
│       └── error_model.py         # RFC7807 error responses
│
├── api/                           # ⚙️ COMPATIBILITY LAYER: Re-exports from src/api/routers/
│   ├── __init__.py
│   ├── ui.py
│   ├── ur.py
│   ├── exchange.py
│   ├── brou.py
│   └── system.py
│
├── main.py                        # 🚀 Entry point (unchanged, uses shims for backward compat)
├── constants.py                   # ⚙️ SHIM: Re-exports from src/utils/constants
├── error_model.py                 # ⚙️ SHIM: Re-exports from src/utils/error_model
├── models.py                      # ⚙️ SHIM: Re-exports from src/domain/models
├── services.py                    # ⚙️ SHIM: Re-exports from src/domain/services
├── database.py                    # ⚙️ SHIM: Re-exports from src/infrastructure/database
├── [32 other shim files]          # ⚙️ SHIM: Compatibility layer
│
├── tests/                         # 📋 Test suite (unchanged)
├── scripts/                       # 📝 Utility scripts
├── docs/                          # 📚 Documentation
└── [other root files]
```

---

## 🎯 Layer Responsibilities

### **API Layer** (`src/api/routers/`)

**Purpose:** HTTP REST endpoint handlers  
**Responsibility:** Request/response conversion, basic validation, routing to services

Files:
- `ui.py`: Unidad Indexada (UI) endpoints
- `ur.py`: Unidad Reajustable (UR) endpoints  
- `exchange.py`: Exchange rate endpoints
- `brou.py`: BROU data endpoints
- `system.py`: Health, metrics, debug endpoints

**Example:**
```python
from src.api.routers import ui_router  # In main.py
app.include_router(ui_router)
```

### **Domain Layer** (`src/domain/`)

**Purpose:** Core business logic & rules  
**Responsibility:** Data processing, validation, service-level operations

Files:
- `models.py`: SQLAlchemy ORM models (UIRecord, URRecord, ExchangeRateRecord, BROURecord)
- `pydantic_models.py`: Request/response validation models
- `services.py`: Business service implementations (UIService, URService, ExchangeRateService)
- `brou_processor.py`: BROU data scraping & parsing
- `excel_processor.py`: Excel file parsing for UI, UR, Exchange data
- `exchange_utils.py`: Exchange rate calculation utilities

**Example:**
```python
from src.domain.services import UIService
service = UIService(db)
latest = service.get_latest()
```

### **Infrastructure Layer** (`src/infrastructure/`)

**Purpose:** External system adapters  
**Responsibility:** Database, authentication, middleware, external service calls

**Categories:**

1. **Database & ORM**
   - `database.py`: SQLAlchemy engine, session factory
   - `database_optimizer.py`: Query optimization utilities

2. **Authentication & Authorization**
   - `auth_middleware.py`: JWT validation middleware
   - `auth_models.py`: Auth ORM models
   - `auth_service.py`: Login, token generation
   - `auth_routes.py`: Auth endpoints

3. **HTTP Middleware**
   - `https_middleware.py`: HTTPS redirect, CSP headers
   - `metrics_middleware.py`: Prometheus metrics collection
   - `correlation_middleware.py`: Request correlation ID tracking

4. **Cross-cutting Concerns**
   - `rate_limit.py`: Rate limiting (slowapi)
   - `circuit_breaker.py`: Circuit breaker for external APIs
   - `health_checks.py`: Liveness, readiness probes
   - `metrics.py`: Prometheus metrics & scraping endpoint

### **Application Layer** (`src/application/`)

**Purpose:** App-level orchestration & cross-domain concerns  
**Responsibility:** Configuration, security, monitoring, bootstrapping

Files:
- `bootstrap.py`: App initialization, scheduler setup
- `config_validator.py`: Configuration validation at startup
- `opentelemetry_setup.py`: OTel SDK initialization, instrumentation
- `alerts.py`: Alert rule management
- `security_monitor.py`: Security event monitoring
- `security_utils.py`: Input validation, security helpers
- `secure_logging.py`: Structured logging with secrets redaction
- `secret_manager.py`: Environment variable loading
- `generate_security_docs.py`: Auto-generate security docs
- `validate_deploy.py`: Pre-deployment checks
- `verify_security.py`: Security verification script

### **Utils Layer** (`src/utils/`)

**Purpose:** Shared, domain-agnostic utilities  
**Responsibility:** Constants, error models, common functions

Files:
- `constants.py`: Configuration constants, message templates
- `error_model.py`: RFC7807 Problem Details error responses

---

## 🔄 Dependency Flow

```
HTTP Request
    ↓
API Router (src/api/routers/*.py)
    ├─→ extracts & validates input
    ├─→ authenticates (via middleware)
    ├─→ calls Domain Service
    │
Domain Service (src/domain/services.py)
    ├─→ applies business logic
    ├─→ uses Domain Models
    ├─→ calls Infrastructure layer
    │
Infrastructure (src/infrastructure/)
    ├─→ Database operations (via SQLAlchemy)
    ├─→ External API calls (BROU, BCU, INE)
    ├─→ Cache management
    ├─→ Logging & metrics
    │
Response Models (src/domain/pydantic_models.py)
    ├─→ serialization
    ├─→ RFC7807 error wrapping (via src/utils/error_model.py)
    ↓
HTTP Response
```

---

## 🔌 Backward Compatibility (Shims)

To ensure zero breaking changes, all files remain in root with **compatibility shims**:

```python
# Root file: constants.py
"""
Compatibility shim: Re-exports from src.utils.constants
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.utils.constants import *
"""
from src.utils.constants import *
__all__ = [name for name in dir() if not name.startswith("_")]
```

**Benefits:**
- ✅ Existing imports (`from constants import ...`) work unchanged
- ✅ `main.py` requires zero changes
- ✅ Tests pass without modification
- ✅ Gradual migration: new code can import from `src/` directly

**Migration Strategy:**
1. Phase 1 (Now): Shims allow both old & new import styles
2. Phase 2 (Future): Update test imports to use `src/` paths
3. Phase 3: Remove shims after all code migrated

---

## 📊 Import Patterns

### **Old Style (Still Works)**
```python
from constants import DATABASE_URL
from models import UIRecord
from services import UIService
from database import get_db
```

### **New Style (Recommended)**
```python
from src.utils.constants import DATABASE_URL
from src.domain.models import UIRecord
from src.domain.services import UIService
from src.infrastructure.database import get_db
```

### **API Routers (Use New Style)**
```python
# src/api/routers/ui.py
from src.utils.constants import TAG_UI
from src.domain.models import UIResponse
from src.domain.services import UIService
from src.infrastructure.database import get_db
```

---

## 🧪 Testing Improvements

With clear layer separation, testing becomes easier:

```python
# Test domain service without API layer
from src.domain.services import UIService
from src.infrastructure.database import SessionLocal

def test_get_latest_ui():
    db = SessionLocal()
    service = UIService(db)
    result = service.get_latest()
    assert result is not None
```

```python
# Mock infrastructure, test domain logic
from unittest.mock import Mock
from src.domain.services import UIService

def test_ui_service_with_mock_db():
    mock_db = Mock()
    service = UIService(mock_db)
    # ... test business logic without real DB
```

---

## 🚀 Deployment Notes

### **Docker**
- Entry point remains: `python main.py`
- All imports work transparently via shims
- No changes to Dockerfile

### **CI/CD**
- pytest tests run unchanged
- alembic migrations reference `src/infrastructure/database.py`
- No changes to workflow

### **Performance**
- No runtime overhead (shims are pure re-exports)
- Python's import caching handles the single extra import
- ~1ms added per cold import (negligible)

---

## 📈 Benefits of Hexagonal Architecture

| Benefit | Realization |
|---------|-------------|
| **Clear separation of concerns** | Each layer has single responsibility |
| **Testability** | Easy to mock infrastructure, test business logic |
| **Maintainability** | Obvious where to add new features |
| **Scalability** | Can split layers into microservices later |
| **Compliance** | Matches architecture audit requirements (no src/ structure → now has it) |
| **Zero breaking changes** | Shims provide transparent compatibility |

---

## 🔍 File Mapping Reference

### From Root to src/
```
constants.py              → src/utils/constants.py
error_model.py            → src/utils/error_model.py
models.py                 → src/domain/models.py
pydantic_models.py        → src/domain/pydantic_models.py
services.py               → src/domain/services.py
brou_processor.py         → src/domain/brou_processor.py
excel_processor.py        → src/domain/excel_processor.py
exchange_utils.py         → src/domain/exchange_utils.py
database.py               → src/infrastructure/database.py
database_optimizer.py     → src/infrastructure/database_optimizer.py
auth_*.py                 → src/infrastructure/auth_*.py
*_middleware.py           → src/infrastructure/*_middleware.py
rate_limit.py             → src/infrastructure/rate_limit.py
circuit_breaker.py        → src/infrastructure/circuit_breaker.py
health_checks.py          → src/infrastructure/health_checks.py
metrics.py                → src/infrastructure/metrics.py
alerts.py                 → src/application/alerts.py
bootstrap.py              → src/application/bootstrap.py
config_validator.py       → src/application/config_validator.py
secret_manager.py         → src/application/secret_manager.py
secure_logging.py         → src/application/secure_logging.py
security_*.py             → src/application/security_*.py
opentelemetry_setup.py    → src/application/opentelemetry_setup.py
generate_security_docs.py → src/application/generate_security_docs.py
validate_deploy.py        → src/application/validate_deploy.py
verify_security.py        → src/application/verify_security.py
api/                      → src/api/routers/
```

---

## ✅ Verification

After restructuring, verify everything works:

```bash
# Import core modules
python -c "from src.domain.services import UIService; print('✓ Domain imports')"
python -c "from src.infrastructure.database import SessionLocal; print('✓ Infrastructure imports')"
python -c "from src.api.routers import ui_router; print('✓ API routers')"

# Old-style imports still work
python -c "from constants import DATABASE_URL; print('✓ Backward compat')"

# App starts
python main.py &  # Check http://localhost:8000/api/docs
```

---

## 📝 Summary

SIFU backend now follows **hexagonal architecture** with:
- ✅ Clear layer separation (API, Domain, Infrastructure, Application, Utils)
- ✅ Domain-driven design principles
- ✅ 100% backward compatibility via shims
- ✅ Zero breaking changes
- ✅ Improved testability & maintainability
- ✅ Compliance with architecture audit (addresses "no src/ structure" gap)

This structure enables:
- Easier onboarding for new developers
- Better code organization as complexity grows
- Foundation for future microservices split
- Clear testing boundaries

---

**Branch:** `feature/architecture-compliance-audit-v1`  
**Previous commits:** 7 (RFC7807, OTel, Alembic, CSP+JWT, Router split, CI/CD updates, Documentation)  
**This commit:** Hexagonal architecture restructuring + full backward compatibility

