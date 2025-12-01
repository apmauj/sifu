# Current Project Architecture - Visual Overview

## Current Structure (This Branch - feature/architecture-compliance-audit-v1)

```mermaid
graph TB
    subgraph "📁 Root Directory (~90 files) ⚠️"
        Main["main.py<br/>(FastAPI Entry Point)"]
        Shims["35 Python Shims<br/>(Backward Compat Files)"]
        Config["Config Files<br/>(.env, pytest.ini,<br/>nginx.conf, etc)"]
        Docker["Docker Files<br/>(Dockerfile,<br/>docker-compose.*)"]
        Scripts["Scripts<br/>(.ps1, .bat)"]
        Data["Data Files<br/>(*.db, *.json)"]
        Docs["Docs<br/>(*.md files)"]
    end

    subgraph "🎯 Backend - src/ (Hexagonal - QW#7)"
        API["📡 api/routers/<br/>- ui.py<br/>- ur.py<br/>- exchange.py<br/>- brou.py<br/>- system.py"]
        Domain["🎯 domain/<br/>- models.py<br/>- services.py<br/>- pydantic_models.py<br/>- processors"]
        Infra["🔧 infrastructure/<br/>- database.py<br/>- auth_*.py<br/>- middleware/<br/>- health_checks.py<br/>- metrics.py"]
        App["⚡ application/<br/>- bootstrap.py<br/>- security_*<br/>- alerts.py<br/>- logging"]
        Utils["🛠️ utils/<br/>- constants.py<br/>- error_model.py"]
    end

    subgraph "🧪 Tests - tests/ (Organized - QW#8)"
        Unit["unit/"]
        Integration["integration/<br/>(13 files moved)"]
        Demo["demo/<br/>(3 files moved)"]
    end

    subgraph "📜 Scripts - scripts/ (Organized - QW#8)"
        Deploy["deploy/"]
        Setup["setup/<br/>(5 files moved)"]
        Monitoring["monitoring/"]
        DemoScripts["demo/<br/>(1 file moved)"]
    end

    subgraph "⚛️ Frontend - frontend/"
        FrontSrc["src/<br/>(React components)"]
        FrontTest["test/"]
        FrontDist["dist/<br/>(built)"]
    end

    subgraph "🗂️ Supporting Directories"
        Docs2["docs/"]
        Config2["config/"]
        Data2["data/"]
        Logs["logs/"]
        Alembic["alembic/"]
    end

    Main -->|imports from| Shims
    Shims -->|re-export| Domain
    API -->|uses| Domain
    API -->|uses| Infra
    Domain -->|uses| Utils
    Infra -->|uses| Domain
    App -->|configures| Infra
    
    Tests -->|test| API
    Tests -->|test| Domain
    Scripts -->|deploy| Docker

    style Shims fill:#ff9999
    style Root fill:#ffcc99
```

---

## Architecture Layers - Details

```mermaid
graph LR
    subgraph "External Clients"
        Web["🌐 Web Browser"]
        API_Client["📱 API Client"]
    end

    subgraph "Frontend Layer"
        React["⚛️ React App<br/>(frontend/src/)<br/>- Panels<br/>- Components<br/>- Services"]
    end

    subgraph "API Layer (src/api/)"
        Router["🔀 Routers<br/>- ui.py<br/>- ur.py<br/>- exchange.py<br/>- brou.py<br/>- system.py"]
    end

    subgraph "Application Layer (src/application/)"
        Bootstrap["Bootstrap"]
        Security["Security"]
        Alerts["Alerts"]
    end

    subgraph "Domain Layer (src/domain/)"
        Models["🗃️ Models<br/>(SQLAlchemy ORM)"]
        Services["⚙️ Services<br/>(Business Logic)"]
        Processors["🔄 Processors<br/>(BROU, Excel,<br/>Exchange Rates)"]
    end

    subgraph "Infrastructure Layer (src/infrastructure/)"
        Database["💾 Database<br/>(PostgreSQL/SQLite)"]
        Auth["🔐 Auth/RBAC"]
        Middleware["🔌 Middleware"]
        Health["❤️ Health Checks"]
        Metrics["📊 Metrics"]
    end

    subgraph "External Services"
        BROU["🏦 BROU API"]
        BCU["🏦 BCU API"]
        Excel["📊 Excel"]
    end

    Web -->|HTTP| React
    React -->|API Calls| Router
    API_Client -->|HTTP| Router
    
    Router -->|uses| Bootstrap
    Router -->|uses| Security
    Bootstrap -->|configures| Middleware
    
    Router -->|calls| Services
    Services -->|uses| Models
    Services -->|calls| Processors
    
    Models -->|queries| Database
    Processors -->|fetches| BROU
    Processors -->|fetches| BCU
    Processors -->|reads| Excel
    
    Auth -->|uses| Database
    Health -->|checks| Database
    Metrics -->|monitors| Middleware
```

---

## File Count Breakdown

```mermaid
pie title "Distribution of Files in Root (~90 files)"
    "Python Shims" : 35
    "Config Files" : 15
    "Docker/Deploy" : 8
    "Data (.db)" : 6
    "Scripts" : 5
    "Documentation" : 20
    "Other/Meta" : 6
```

---

## Technology Stack

```mermaid
graph TB
    subgraph "Backend"
        FastAPI["FastAPI 0.100+<br/>(Web Framework)"]
        SQLAlchemy["SQLAlchemy 2.0+<br/>(ORM)"]
        Pydantic["Pydantic 2.0+<br/>(Validation)"]
        Alembic["Alembic<br/>(Migrations)"]
        OTel["OpenTelemetry<br/>(Observability)"]
    end

    subgraph "Frontend"
        React["React 18+<br/>(UI Library)"]
        Vite["Vite<br/>(Build Tool)"]
        Tailwind["Tailwind CSS<br/>(Styling)"]
        RTL["React Testing Lib<br/>(Testing)"]
    end

    subgraph "Infrastructure"
        Docker["Docker<br/>(Containerization)"]
        Nginx["Nginx<br/>(Reverse Proxy)"]
        GitHub["GitHub Actions<br/>(CI/CD)"]
        Postgres["PostgreSQL<br/>(Database)"]
    end

    subgraph "Testing"
        Pytest["pytest<br/>(Backend Tests)"]
        Jest["Jest/Vitest<br/>(Frontend Tests)"]
    end

    FastAPI -->|server requests| Nginx
    React -->|calls| FastAPI
    FastAPI -->|queries| Postgres
    SQLAlchemy -->|ORM for| Postgres
    Pydantic -->|validates| FastAPI
    Alembic -->|manages| Postgres
    
    Docker -->|containerizes| FastAPI
    Docker -->|containerizes| React
    GitHub -->|deploys| Docker
```

---

## Current Issues

```mermaid
graph TB
    Issue1["❌ Root Too Cluttered<br/>(90 files)<br/>Should be ~15"]
    Issue2["❌ Shim Files<br/>(35 files)<br/>Backward compat cost"]
    Issue3["❌ Config Scattered<br/>(.env, nginx.conf,<br/>pytest.ini, etc)"]
    Issue4["❌ Data in Root<br/>(*.db files)"]
    Issue5["❌ Docs Scattered<br/>(20+ .md files)"]

    Issue1 -->|Caused by| Issue2
    Issue1 -->|Caused by| Issue3
    Issue1 -->|Caused by| Issue4
    Issue1 -->|Caused by| Issue5
    
    style Issue1 fill:#ff6666
    style Issue2 fill:#ff9999
    style Issue3 fill:#ffaa99
    style Issue4 fill:#ffbb99
    style Issue5 fill:#ffcc99
```
