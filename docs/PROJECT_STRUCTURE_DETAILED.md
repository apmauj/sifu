# Project Structure - Detailed Breakdown

## Complete Directory Tree (This Branch)

```
sifu/
│
├── 📁 src/                          ← BACKEND (Hexagonal - QW#7 ✅)
│   ├── api/
│   │   └── routers/
│   │       ├── ui.py                (UI Index endpoints)
│   │       ├── ur.py                (UR Calculation endpoints)
│   │       ├── exchange.py          (Exchange Rate endpoints)
│   │       ├── brou.py              (BROU Data endpoints)
│   │       └── system.py            (Health, Info, etc)
│   │
│   ├── domain/
│   │   ├── models.py                (SQLAlchemy ORM models)
│   │   ├── services.py              (Business logic)
│   │   ├── pydantic_models.py       (Request/Response models)
│   │   └── processors/
│   │       ├── brou_processor.py
│   │       ├── excel_processor.py
│   │       └── exchange_utils.py
│   │
│   ├── infrastructure/
│   │   ├── database.py              (DB connection)
│   │   ├── database_optimizer.py    (Performance)
│   │   ├── auth/
│   │   │   ├── auth_middleware.py
│   │   │   ├── auth_models.py
│   │   │   ├── auth_routes.py
│   │   │   └── auth_service.py
│   │   ├── middleware/
│   │   │   ├── correlation_middleware.py
│   │   │   ├── https_middleware.py
│   │   │   ├── rate_limit.py
│   │   │   ├── circuit_breaker.py
│   │   │   └── metrics_middleware.py
│   │   ├── health_checks.py
│   │   ├── metrics.py
│   │   └── observability/
│   │       └── opentelemetry_setup.py
│   │
│   ├── application/
│   │   ├── bootstrap.py             (App startup)
│   │   ├── config_validator.py      (Config validation)
│   │   ├── security/
│   │   │   ├── security_monitor.py
│   │   │   ├── security_utils.py
│   │   │   ├── secret_manager.py
│   │   │   └── generate_security_docs.py
│   │   ├── alerts.py                (Alert system)
│   │   └── observability/
│   │       └── secure_logging.py
│   │
│   └── utils/
│       ├── constants.py             (App constants)
│       └── error_model.py           (Error definitions)
│
├── 📁 frontend/                      ← FRONTEND (React - Separate ✅)
│   ├── src/
│   │   ├── components/              (React components)
│   │   ├── pages/                   (Page components)
│   │   ├── services/                (API services)
│   │   ├── hooks/                   (Custom hooks)
│   │   ├── utils/                   (Utilities)
│   │   ├── styles/                  (CSS/Tailwind)
│   │   └── App.jsx
│   ├── test/                        (Jest/Vitest tests)
│   ├── dist/                        (Built files)
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── 📁 tests/                         ← TESTS (Organized - QW#8 ✅)
│   ├── unit/                        (Fast, isolated tests)
│   │   ├── test_api.py
│   │   ├── test_services.py
│   │   ├── test_models.py
│   │   └── (15+ more unit tests)
│   ├── integration/                 (Slower, system tests)
│   │   ├── test_all_checks.py
│   │   ├── test_brou_monitoring.py
│   │   ├── test_health_checks.py
│   │   ├── test_server.py
│   │   └── (9 more integration tests)
│   ├── demo/                        (Demo/Example tests)
│   │   ├── async_test.py
│   │   ├── main_test.py
│   │   └── simple_test.py
│   ├── conftest.py                  (Pytest fixtures)
│   └── README.md                    (Test guide)
│
├── 📁 scripts/                       ← SCRIPTS (Organized - QW#8 ✅)
│   ├── deploy/
│   │   ├── deploy_frontend.ps1
│   │   ├── deploy_backend.ps1
│   │   ├── deploy_menu.ps1
│   │   └── update_tunnel_secret.ps1
│   ├── setup/                       ← NEW (QW#8)
│   │   ├── setup_https.py
│   │   ├── setup_production.py
│   │   ├── setup_rbac.py
│   │   ├── start_secure.py
│   │   ├── start_server.py
│   │   └── README.md
│   ├── monitoring/
│   │   ├── tunnel_monitor.py
│   │   ├── demo_monitoring.py
│   │   └── setup_monitoring.py
│   ├── util/
│   │   ├── install_all.sh
│   │   └── check_messages.py
│   ├── demo/                        ← NEW (QW#8)
│   │   ├── demo_performance_budget.py
│   │   └── README.md
│   ├── archive/
│   │   ├── docker_scripts.sh
│   │   └── docker_scripts.ps1
│   └── README.md
│
├── 📁 docs/                          ← DOCUMENTATION
│   ├── api/                         (API documentation)
│   ├── architecture/                (Architecture docs)
│   ├── deployment/                  (Deployment guides)
│   ├── security/                    (Security docs)
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── QUICK_WIN_7_HEXAGONAL_ARCHITECTURE.md
│   ├── QUICK_WIN_8_ROOT_ORGANIZATION.md
│   ├── ARCHITECTURE_ANALYSIS_CURRENT_vs_IDEAL.md
│   ├── ARCHITECTURE_VISUAL_DIAGRAMS.md
│   ├── ARCHITECTURE_COMPARISON_MASTER_vs_BRANCH.md
│   └── (20+ more documentation files)
│
├── 📁 config/                       ← CONFIGURATION
│   ├── monitoring_config.json
│   └── (other configs)
│
├── 📁 data/                         ← DATA
│   ├── (no organized structure yet)
│   └── Contains: *.db files, *.json responses
│
├── 📁 logs/                         ← LOGS
│   ├── app/
│   ├── security/
│   └── audit/
│
├── 📁 alembic/                      ← DATABASE MIGRATIONS
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── 📁 static/                       ← STATIC FILES
│
├── 📁 ssl/                          ← SSL CERTIFICATES
│
├── 📁 reports/                      ← TEST REPORTS
│
├── 📁 htmlcov/                      ← COVERAGE REPORTS
│
├── 📁 .github/                      ← GITHUB WORKFLOWS
│   └── workflows/
│       └── ci-cd.yml
│
├── 🐍 PYTHON ENTRY POINTS (in ROOT - ⚠️ Still cluttered)
│   └── main.py                      ✅ (Entry point - OK here)
│
├── ⚠️ SHIM FILES (35 - QW#7 Backward Compat - for cleanup in QW#10)
│   ├── alerts.py → src/application/alerts.py
│   ├── auth_middleware.py → src/infrastructure/auth/auth_middleware.py
│   ├── auth_models.py → src/infrastructure/auth/auth_models.py
│   ├── auth_routes.py → src/infrastructure/auth/auth_routes.py
│   ├── auth_service.py → src/infrastructure/auth/auth_service.py
│   ├── bootstrap.py → src/application/bootstrap.py
│   ├── brou_processor.py → src/domain/processors/brou_processor.py
│   ├── circuit_breaker.py → src/infrastructure/middleware/circuit_breaker.py
│   ├── config_validator.py → src/application/config_validator.py
│   ├── constants.py → src/utils/constants.py
│   ├── correlation_middleware.py → src/infrastructure/middleware/correlation_middleware.py
│   ├── dashboard.py → src/domain/dashboard.py
│   ├── database.py → src/infrastructure/database.py
│   ├── database_optimizer.py → src/infrastructure/database_optimizer.py
│   ├── error_model.py → src/utils/error_model.py
│   ├── excel_processor.py → src/domain/processors/excel_processor.py
│   ├── exchange_utils.py → src/domain/processors/exchange_utils.py
│   ├── generate_security_docs.py → src/application/security/generate_security_docs.py
│   ├── health_checks.py → src/infrastructure/health_checks.py
│   ├── https_middleware.py → src/infrastructure/middleware/https_middleware.py
│   ├── init_brou_table.py → src/domain/init_brou_table.py
│   ├── metrics.py → src/infrastructure/metrics.py
│   ├── metrics_middleware.py → src/infrastructure/middleware/metrics_middleware.py
│   ├── models.py → src/domain/models.py
│   ├── opentelemetry_setup.py → src/application/observability/opentelemetry_setup.py
│   ├── performance_budget.py → src/domain/performance_budget.py
│   ├── pydantic_models.py → src/domain/pydantic_models.py
│   ├── rate_limit.py → src/infrastructure/middleware/rate_limit.py
│   ├── secret_manager.py → src/application/security/secret_manager.py
│   ├── secure_logging.py → src/application/observability/secure_logging.py
│   ├── security_monitor.py → src/application/security/security_monitor.py
│   ├── security_utils.py → src/application/security/security_utils.py
│   ├── services.py → src/domain/services.py
│   ├── simple_totp.py → src/infrastructure/auth/simple_totp.py
│
├── ⚙️ CONFIGURATION FILES (in ROOT - for cleanup in QW#9)
│   ├── pytest.ini                   ✅ (Standard location - OK)
│   ├── alembic.ini                  ✅ (Standard location - OK)
│   ├── setup.cfg                    ⚠️ (Could move to config/)
│   ├── .env.example                 ⚠️ (Should be in config/env/)
│   ├── .env.docker                  ⚠️ (Should be in config/env/)
│   ├── .env.production              ⚠️ (Should be in config/env/)
│   ├── .env.template                ⚠️ (Should be in config/env/)
│   ├── nginx.conf                   ⚠️ (Should be in config/nginx/)
│   ├── nginx.https.conf             ⚠️ (Should be in config/nginx/)
│   ├── .pre-commit-config.yaml      ⚠️ (Could move to config/)
│
├── 🐳 DEPLOYMENT FILES (in ROOT - OK here as entry points)
│   ├── Dockerfile                   ✅
│   ├── docker-compose.yml           ✅ (main)
│   ├── docker-compose.simple.yml    ⚠️ (Could move to config/)
│   ├── docker-compose.gateway.yml   ⚠️ (Could move to config/)
│   ├── docker-compose.prod.yml      ⚠️ (Could move to config/)
│   └── docker-compose.tunnel.yml    ⚠️ (Could move to config/)
│
├── 📦 DEPENDENCY FILES (in ROOT - Standard locations ✅)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── requirements-core.txt
│   ├── requirements-excel.txt
│   └── package.json                 (frontend)
│
├── 💾 DATA FILES (in ROOT - ⚠️ Should be in data/)
│   ├── ui_data.db
│   ├── ui_data_backup_20250613_232108.db
│   ├── ui_data_backup_20250613_232242.db
│   ├── test_ur.db
│   └── ur_refresh_resp.json
│
└── 📚 OTHER FILES
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    ├── package-lock.json
    ├── .dockerignore
    └── (meta files)
```

---

## Statistics

### Lines of Code (Approximate)
| Component | Files | Lines | Type |
|-----------|-------|-------|------|
| Backend (src/) | 32 | 15,000+ | Python |
| Frontend | 50+ | 10,000+ | JavaScript/React |
| Tests | 40+ | 8,000+ | Python/JavaScript |
| Documentation | 30+ | 5,000+ | Markdown |

### File Count by Category
| Category | Count | Location | Status |
|----------|-------|----------|--------|
| Python source | 32 | src/ | ✅ OK |
| Python shims | 35 | root/ | ⚠️ QW#10 |
| React components | 50+ | frontend/ | ✅ OK |
| Test files | 40+ | tests/ | ✅ QW#8 |
| Scripts | 20+ | scripts/ | ✅ QW#8 |
| Documentation | 30+ | docs/ | ⚠️ Scattered |
| Config files | 15 | root/ + config/ | ⚠️ QW#9 |
| Data files | 6 | root/ + data/ | ⚠️ QW#9 |

---

## Organization Progress

```
MASTER (100+ files in root)
    ↓ QW#7: Backend organization
AFTER QW#7 (90 files in root, src/ organized)
    ↓ QW#8: Test/Script organization
AFTER QW#8 (90 files in root, tests/scripts organized) ← YOU ARE HERE
    ↓ QW#9: Config/Data organization
AFTER QW#9 (~45 files in root, config/data centralized)
    ↓ QW#10: Remove shims
IDEAL STATE (~15 files in root, professional structure)
```

---

## How Backend & Frontend Interact

```
Frontend (React) @ http://localhost:3000
    ↓
API Calls (fetch/axios)
    ↓
main.py (FastAPI app)
    ↓
src/api/routers/
    ├── ui.py
    ├── ur.py
    ├── exchange.py
    ├── brou.py
    └── system.py
    ↓
src/domain/services.py (Business Logic)
    ↓
src/domain/processors/ (Data Processing)
    ↓
src/infrastructure/ (External Services)
    ├── database.py (PostgreSQL)
    ├── auth/ (Authentication)
    └── health_checks.py (Monitoring)
```

This structure is **HEALTHY and PROFESSIONAL**.

The only remaining issue is the **90 files in root** that should be consolidated in **QW#9 & QW#10**.
