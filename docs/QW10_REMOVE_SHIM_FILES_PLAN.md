# QW#10 - Remove Shim Files Plan

**Status:** Planning Phase  
**Branch:** `feature/architecture-compliance-audit-v1`  
**Estimated Duration:** 1-2 hours  
**Risk Level:** Medium (many imports to update)  
**Prerequisites:** QW#9 completed first

---

## 📋 Objective

Remove 35 shim files from root directory and update all imports to use `src/` directly.

**Current State:** 45 files in root (after QW#9)  
**Target State:** 15 files in root (professional!) ✅

---

## 🔍 Phase 1: Identify Shim Files

### 1.1 All 35 Shim Files to Remove

These files are in root and re-export from `src/`:

**Authentication (5 files):**
```
auth_middleware.py      → src/infrastructure/middleware/auth_middleware.py
auth_models.py          → src/infrastructure/auth/models.py
auth_routes.py          → src/api/routers/auth_routes.py
auth_service.py         → src/infrastructure/auth/auth_service.py
secret_manager.py       → src/infrastructure/auth/secret_manager.py
```

**Core Domain (6 files):**
```
constants.py            → src/utils/constants.py
services.py             → src/domain/services.py
models.py               → src/domain/models.py
pydantic_models.py      → src/domain/pydantic_models.py
dashboard.py            → src/domain/dashboard.py
metrics.py              → src/infrastructure/metrics/metrics.py
```

**Data & Exchange (5 files):**
```
excel_processor.py      → src/domain/excel_processor.py
exchange_utils.py       → src/domain/exchange/exchange_utils.py
brou_processor.py       → src/domain/brou_processor.py
database.py             → src/infrastructure/database/database.py
brou_cache.py           → (IF EXISTS) src/infrastructure/cache/brou_cache.py
```

**Infrastructure (8 files):**
```
circuit_breaker.py      → src/infrastructure/resilience/circuit_breaker.py
rate_limit.py           → src/infrastructure/middleware/rate_limit.py
alerts.py               → src/application/alerts.py
health_checks.py        → src/infrastructure/health/health_checks.py
metrics_middleware.py   → src/infrastructure/middleware/metrics_middleware.py
correlation_middleware.py → src/infrastructure/middleware/correlation_middleware.py
https_middleware.py     → src/infrastructure/middleware/https_middleware.py
secure_logging.py       → src/infrastructure/logging/secure_logging.py
```

**Application/Setup (5 files):**
```
bootstrap.py            → src/application/bootstrap.py
security_utils.py       → src/infrastructure/security/security_utils.py
security_monitor.py     → src/infrastructure/security/security_monitor.py
config_validator.py     → src/application/config_validator.py
database_optimizer.py   → src/infrastructure/database/database_optimizer.py
```

**Total: 35 files**

---

## 🎯 Phase 2: Find All Import References

### 2.1 Search Patterns

**Pattern 1: Direct imports from root**
```python
from constants import MSG_*
from services import UIService
from models import User
from auth_middleware import *
```

**Pattern 2: In main.py**
```python
from constants import *
from services import *
import middleware modules
```

**Pattern 3: In Docker/scripts**
```
COPY main.py /app
RUN python main.py
```

### 2.2 Files That Import Shims

Use grep to find all imports:

```powershell
# Find all Python imports from shim files
grep -r "from (constants|services|models|auth_|dashboard|metrics|excel_|exchange_|brou_|circuit_|rate_|alerts|health_|.*_middleware|secure_logging|bootstrap|security_|config_validator|database)" --include="*.py"

# Find all in main.py
grep -E "^(from|import)" main.py

# Find in tests
grep -r "from (constants|services|models)" tests/ --include="*.py"

# Find in frontend
find frontend/ -name "*.js" -o -name "*.jsx" | xargs grep -l "api\|backend"
```

### 2.3 Import Update Locations

These files will need updates:

**Backend (Priority 1 - Must Update):**
- [ ] `main.py` - Central entry point
- [ ] `src/api/routers/*.py` - All router files
- [ ] `src/domain/*.py` - All domain files
- [ ] `src/infrastructure/**/*.py` - All infra files
- [ ] `src/application/*.py` - All app files
- [ ] `tests/**/*.py` - All test files

**Docker (Priority 2 - Must Update):**
- [ ] `config/docker/Dockerfile`
- [ ] `config/docker/docker-compose.yml`
- [ ] `config/docker/docker-compose.prod.yml`
- [ ] `docker_update_tunnel_secret.ps1`

**Scripts (Priority 3 - May Update):**
- [ ] `scripts/deploy/*.ps1`
- [ ] `scripts/setup/*.ps1`
- [ ] `scripts/monitoring/*.py`

**Frontend (Priority 4 - Verify):**
- [ ] `frontend/src/services/*.js`
- [ ] `frontend/vite.config.js`

---

## 🔄 Phase 3: Update All Imports

### 3.1 Import Replacement Patterns

**Old Style (from root):**
```python
from constants import MSG_SUCCESS, MSG_ERROR
from services import UIService, URService
from models import User, Exchange
from auth_middleware import check_token
from bootstrap import app
```

**New Style (from src/):**
```python
from src.utils.constants import MSG_SUCCESS, MSG_ERROR
from src.domain.services import UIService, URService
from src.domain.models import User, Exchange
from src.infrastructure.middleware.auth_middleware import check_token
from src.application.bootstrap import app
```

### 3.2 Files to Update - Exact List

**CRITICAL - Update first:**
1. `main.py`
   - Replace all root imports with `src/` imports
   - Keep entry point logic same

2. `src/api/routers/ui_router.py`
   - Update: `from services import UIService` → `from src.domain.services import UIService`

3. `src/api/routers/ur_router.py`
   - Update: `from services import URService` → `from src.domain.services import URService`

4. `src/api/routers/exchange_router.py`
   - Update: `from services import ExchangeRateService` → `from src.domain.services import ExchangeRateService`

5. `src/api/routers/brou_router.py`
   - Update: `from brou_processor import *` → `from src.domain.brou_processor import *`

6. `src/domain/services.py`
   - Update: `from models import *` → `from src.domain.models import *`
   - Update: `from constants import *` → `from src.utils.constants import *`

7. `src/infrastructure/database/database.py`
   - Already internal - minimal changes needed

8. `src/infrastructure/auth/auth_service.py`
   - Update: `from models import *` → `from src.domain.models import *`

**IMPORTANT - Update all tests:**
9. `tests/conftest.py`
   - Update: `from constants import *` → `from src.utils.constants import *`

10. `tests/**/*.py` (all test files)
    - Update all imports to use `src/` path

**Docker Files:**
11. `config/docker/Dockerfile`
    - Ensure WORKDIR is set correctly
    - Verify PYTHONPATH includes `/app`

12. `config/docker/docker-compose.yml`
    - Add PYTHONPATH if needed: `PYTHONPATH=/app`

### 3.3 Automated Update Strategy

**Option 1: Using sed/grep (PowerShell)**
```powershell
# Find and replace pattern in all Python files
$files = Get-ChildItem -Path . -Include "*.py" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName
    
    # Replace patterns
    $content = $content -replace 'from constants import', 'from src.utils.constants import'
    $content = $content -replace 'from services import', 'from src.domain.services import'
    $content = $content -replace 'from models import', 'from src.domain.models import'
    # ... etc for all 35 shims
    
    Set-Content $file.FullName $content
}
```

**Option 2: Manual via Editor Search & Replace**
- Use VS Code Find & Replace (Ctrl+H)
- Replace each pattern systematically
- Verify each change

---

## ✅ Phase 4: Verification

### 4.1 Pre-Deletion Checklist

- [ ] All import changes documented
- [ ] Backup current state (branch already saved)
- [ ] Identify all 35 shim files
- [ ] Search complete for all references
- [ ] Create list of all files to update

### 4.2 Deletion Steps

```powershell
# After all imports are updated, delete shim files:
Remove-Item auth_middleware.py
Remove-Item auth_models.py
Remove-Item auth_routes.py
Remove-Item auth_service.py
Remove-Item secret_manager.py
Remove-Item constants.py
Remove-Item services.py
Remove-Item models.py
Remove-Item pydantic_models.py
Remove-Item dashboard.py
Remove-Item metrics.py
Remove-Item excel_processor.py
Remove-Item exchange_utils.py
Remove-Item brou_processor.py
Remove-Item database.py
Remove-Item circuit_breaker.py
Remove-Item rate_limit.py
Remove-Item alerts.py
Remove-Item health_checks.py
Remove-Item metrics_middleware.py
Remove-Item correlation_middleware.py
Remove-Item https_middleware.py
Remove-Item secure_logging.py
Remove-Item bootstrap.py
Remove-Item security_utils.py
Remove-Item security_monitor.py
Remove-Item config_validator.py
Remove-Item database_optimizer.py
# ... and 6 more

# Or: git rm auth_middleware.py auth_models.py ... (keeps git history)
```

### 4.3 Post-Deletion Testing

**Run comprehensive tests:**

```powershell
# 1. Backend unit tests
pytest tests/unit/ -v

# 2. Backend integration tests
pytest tests/integration/ -v

# 3. All backend tests
pytest tests/ -v

# 4. Start server
python main.py

# 5. Check imports
python -c "from src.utils.constants import MSG_SUCCESS; print('Imports OK')"

# 6. Frontend build
cd frontend
npm run build

# 7. Docker build
docker build -t sifu:latest .
```

### 4.4 Git Verification

```powershell
# Verify deleted files
git status | grep deleted

# View what will be committed
git diff --cached

# Show final root directory
Get-ChildItem -Path . | Where-Object {$_.PSIsContainer -eq $false} | Measure-Object | Select-Object Count
```

---

## 📊 Expected Result

### Before QW#10
```
ROOT: 45 files
├─ 35 Shim files ← TO DELETE
├─ 5 Config files (after QW#9)
├─ 20+ Documentation files
└─ 5+ Other files
```

### After QW#10
```
ROOT: 15 files (PROFESSIONAL!)
├─ main.py                          (entry point)
├─ requirements.txt                 (dependencies)
├─ requirements-core.txt            (core deps)
├─ requirements-dev.txt             (dev deps)
├─ requirements-excel.txt           (excel deps)
├─ setup.py                         (package setup)
├─ pytest.ini                       (MOVED to config/)
├─ LICENSE                          (license)
├─ README.md                        (readme)
├─ .gitignore                       (.gitignore)
├─ CHANGELOG.md                     (changelog)
├─ Dockerfile                       (MOVED to config/docker/)
├─ docker-compose.yml               (MOVED to config/docker/)
└─ 2-3 other essential files
```

**No more shim files!** ✅  
**Clean root directory!** ✅

---

## 🔗 Related Quick Wins

- **QW#7:** Hexagonal architecture (src/ with 5 layers) ✅
- **QW#8:** Root file organization (tests/scripts moved) ✅
- **QW#9:** Configuration & data organization (before this)
- **QW#10:** Remove shim files (THIS ONE)

---

## ⚠️ Risk Assessment

**Risk Level:** Medium

**Risks:**
- [ ] Breaking imports if not all files updated
- [ ] Circular import issues in src/ files
- [ ] Docker build failing if PYTHONPATH not set
- [ ] Tests failing if fixtures not updated

**Mitigations:**
- [ ] Run tests after each major update
- [ ] Use IDE's "Find References" feature
- [ ] Commit after each phase
- [ ] Keep old branch as backup (git has full history)

---

## ⏱️ Time Estimate

| Phase | Time |
|-------|------|
| Find all imports (search) | 10 min |
| Update import statements | 40 min |
| Delete shim files | 2 min |
| Run comprehensive tests | 15 min |
| Fix any issues | 10 min |
| Git cleanup & commit | 5 min |
| **TOTAL** | **82 min** (1h 22m) |

---

## 📌 Implementation Order

1. **QW#9** (FIRST) - Organize config/data
   - This is prerequisite
   - Low risk
   - 30-45 min

2. **QW#10** (SECOND) - Remove shims
   - Depends on QW#9 completion
   - Medium risk
   - 1-2 hours

3. **Merge to Master** (AFTER BOTH)
   - QW#7 + QW#8 + QW#9 + QW#10 all combined
   - Comprehensive testing done
   - Professional structure!

---

## 🎯 Next Steps

1. **NOW:** Review this plan
2. **Then:** Execute QW#9 (config/data organization)
3. **Then:** Execute QW#10 (remove shims)
4. **Then:** Comprehensive testing
5. **Then:** Ready for merge to master!

---

## 📚 Reference: Import Mapping

Complete mapping of all 35 shim files:

```
authentication/
├─ auth_middleware.py       ← src/infrastructure/middleware/auth_middleware.py
├─ auth_models.py           ← src/infrastructure/auth/models.py
├─ auth_routes.py           ← src/api/routers/auth_routes.py
├─ auth_service.py          ← src/infrastructure/auth/auth_service.py
└─ secret_manager.py        ← src/infrastructure/auth/secret_manager.py

core/
├─ constants.py             ← src/utils/constants.py
├─ services.py              ← src/domain/services.py
├─ models.py                ← src/domain/models.py
├─ pydantic_models.py       ← src/domain/pydantic_models.py
└─ dashboard.py             ← src/domain/dashboard.py

data/
├─ excel_processor.py       ← src/domain/excel_processor.py
├─ brou_processor.py        ← src/domain/brou_processor.py
├─ database.py              ← src/infrastructure/database/database.py
└─ exchange_utils.py        ← src/domain/exchange/exchange_utils.py

infrastructure/
├─ circuit_breaker.py       ← src/infrastructure/resilience/circuit_breaker.py
├─ rate_limit.py            ← src/infrastructure/middleware/rate_limit.py
├─ health_checks.py         ← src/infrastructure/health/health_checks.py
├─ metrics.py               ← src/infrastructure/metrics/metrics.py
├─ metrics_middleware.py    ← src/infrastructure/middleware/metrics_middleware.py
├─ correlation_middleware.py ← src/infrastructure/middleware/correlation_middleware.py
├─ https_middleware.py      ← src/infrastructure/middleware/https_middleware.py
└─ secure_logging.py        ← src/infrastructure/logging/secure_logging.py

application/
├─ bootstrap.py             ← src/application/bootstrap.py
├─ alerts.py                ← src/application/alerts.py
├─ config_validator.py      ← src/application/config_validator.py
├─ security_utils.py        ← src/infrastructure/security/security_utils.py
├─ security_monitor.py      ← src/infrastructure/security/security_monitor.py
└─ database_optimizer.py    ← src/infrastructure/database/database_optimizer.py

TOTAL: 35 shim files
```
