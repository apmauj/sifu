# QW#9 - Configuration & Data Organization Plan

**Status:** Planning Phase  
**Branch:** `feature/architecture-compliance-audit-v1`  
**Estimated Duration:** 30-45 minutes  
**Risk Level:** Low

---

## 📋 Objective

Move configuration and data files from root directory to organized subdirectories:
- `.env` files → `config/env/`
- Nginx configs → `config/nginx/`
- Database files → `data/`
- Other config files → `config/`

**Result:** Root directory goes from 90 → 45 files ✅

---

## 🎯 Phase 1: File Movement

### 1.1 Configuration Files to Move

```
ROOT (.env, .env.* files)
├─ .env                          → config/env/.env
├─ .env.production              → config/env/.env.production
├─ .env.staging                 → config/env/.env.staging
├─ .env.local                   → config/env/.env.local
└─ .env.example                 → config/env/.env.example

ROOT (nginx config)
├─ nginx.conf                   → config/nginx/nginx.conf
├─ nginx.https.conf             → config/nginx/nginx.https.conf
└─ [ADD: nginx.http.conf if exists]

ROOT (other config)
├─ pytest.ini                   → config/pytest.ini
├─ alembic.ini                  → config/alembic.ini
├─ pyproject.toml               → config/pyproject.toml
├─ monitoring_config.json       → config/monitoring_config.json
└─ docker-compose*.yml          → config/docker/docker-compose*.yml

DATA Files to Move
├─ *.db files                   → data/
├─ ur_refresh_resp.json         → data/cache/
└─ [ADD: Any generated data files]
```

### 1.2 Directory Structure to Create

```
config/
├─ env/
│  ├─ .env
│  ├─ .env.production
│  ├─ .env.staging
│  ├─ .env.local
│  └─ .env.example
├─ nginx/
│  ├─ nginx.conf
│  └─ nginx.https.conf
├─ docker/
│  ├─ docker-compose.yml
│  ├─ docker-compose.prod.yml
│  ├─ docker-compose.simple.yml
│  ├─ docker-compose.tunnel.yml
│  ├─ docker-compose.gateway.yml
│  └─ Dockerfile (or config/docker/Dockerfile)
├─ pytest.ini
├─ alembic.ini
├─ pyproject.toml
└─ monitoring_config.json

data/
├─ cache/
│  └─ ur_refresh_resp.json
├─ *.db files
└─ [other data files]
```

---

## 🔄 Phase 2: Code Updates

### 2.1 Python Code Updates

**Files to update:**
- `main.py` - Update environment variable paths
- `bootstrap.py` - Update config file references
- `database.py` - Update SQLite DB path if applicable
- `secure_logging.py` - Update log directory references
- `Dockerfile` - Update WORKDIR and volume mounts
- All config loading code in `src/application/`

**Pattern to replace:**

```python
# OLD
load_dotenv(".env")
config = load_yaml("alembic.ini")
database_path = "sifu.db"

# NEW
load_dotenv("config/env/.env")
config = load_yaml("config/alembic.ini")
database_path = "data/sifu.db"
```

### 2.2 Docker Files Updates

**`Dockerfile`:**
```dockerfile
# OLD
COPY . /app
RUN pip install -r requirements.txt

# NEW
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
# Update volume mounts to use config/env/.env instead of .env
```

**`docker-compose.yml` (if uses .env):**
```yaml
# OLD
env_file: .env

# NEW
env_file: config/env/.env

# OR use explicit environment variables
environment:
  - DATABASE_URL=postgresql://...
```

### 2.3 Script Updates

**PowerShell scripts in `scripts/deploy/` & `scripts/setup/`:**
- Update references to `.env` files
- Update references to `Dockerfile`
- Update references to `docker-compose` locations

### 2.4 Frontend Updates

**`frontend/` build config (if hardcodes any paths):**
- Check if Vite config has any absolute paths
- Update `.env` references if frontend uses environment files

### 2.5 Documentation Updates

**Update in docs:**
- `README.md` - Update setup instructions
- `DEPLOY_BACKEND.md` - Update deployment steps
- `docs/*.md` - Any references to config file locations

---

## ✅ Phase 3: Verification

### 3.1 Pre-Move Checklist

- [ ] Backup current `.env` files
- [ ] Search codebase for all `.env` references: `grep -r "\.env" --include="*.py" --include="*.sh" --include="*.ps1"`
- [ ] Search for hardcoded paths: `grep -r "alembic.ini\|pytest.ini\|nginx.conf" --include="*.py"`
- [ ] List all config files: `ls -la *.env *.ini *.conf docker-compose*.yml`
- [ ] List all data files: `ls -la *.db *.json` (in root)

### 3.2 Post-Move Testing

- [ ] Run backend tests: `pytest tests/ -v`
- [ ] Start server locally: `python main.py`
- [ ] Check that environment variables load correctly
- [ ] Verify database connection works
- [ ] Run Docker build: `docker build -t sifu .`
- [ ] Run docker-compose: `docker-compose -f config/docker/docker-compose.yml up`
- [ ] Frontend still builds: `cd frontend && npm run build`

### 3.3 Git Verification

- [ ] All moved files tracked in git
- [ ] `.gitignore` updated if needed
- [ ] `data/` directory added to `.gitignore` with proper patterns
- [ ] No broken symlinks or references

---

## 📝 Implementation Steps

### Step 1: Create New Directory Structure
```powershell
mkdir config/env
mkdir config/nginx
mkdir config/docker
mkdir data/cache
```

### Step 2: Move Configuration Files
```powershell
# .env files
Move-Item .env config/env/
Move-Item .env.* config/env/

# Nginx config
Move-Item nginx.conf config/nginx/
Move-Item nginx.https.conf config/nginx/

# Other config
Move-Item pytest.ini config/
Move-Item alembic.ini config/
Move-Item docker-compose*.yml config/docker/
Move-Item Dockerfile config/docker/
Move-Item monitoring_config.json config/
```

### Step 3: Move Data Files
```powershell
Move-Item *.db data/
Move-Item ur_refresh_resp.json data/cache/
```

### Step 4: Update Python Code
Search and replace patterns in:
- `main.py`
- `bootstrap.py`
- `database.py`
- `src/application/` files
- `src/infrastructure/` files

### Step 5: Update Dockerfile
```dockerfile
# Update paths for config/docker/Dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt

# Reference config files correctly
COPY config/ ./config/
```

### Step 6: Update Docker Compose
```yaml
# If using env_file:
env_file: config/env/.env

# Or use volume mounts:
volumes:
  - ./config/env/.env:/app/.env
```

### Step 7: Update Scripts
- Review all PowerShell scripts
- Update environment file paths
- Update docker-compose references

### Step 8: Update Documentation
- Update README setup instructions
- Update deployment guides
- Update any environment variable documentation

---

## 📊 Expected Result

### Before QW#9
```
ROOT: 90 files
├─ 35 Shim files
├─ 15 Config files (.env, nginx.conf, etc.) ← TO MOVE
├─ 20+ Documentation files
├─ 6 Database files ← TO MOVE
└─ 8+ Other files
```

### After QW#9
```
ROOT: 45 files
├─ 35 Shim files (still here - will remove in QW#10)
├─ 5 Config files (essential: main.py, requirements.txt, setup.py, LICENSE, README.md)
├─ 20+ Documentation files
└─ 5+ Other files

NEW STRUCTURE:
config/
├─ env/ (all .env files)
├─ nginx/ (all nginx config)
├─ docker/ (docker-compose, Dockerfile)
├─ pytest.ini
├─ alembic.ini
├─ monitoring_config.json
└─ pyproject.toml

data/
├─ cache/ (ur_refresh_resp.json)
└─ (any .db files)
```

---

## 🔗 Related Quick Wins

- **QW#7:** Hexagonal architecture (src/ with 5 layers) ✅
- **QW#8:** Root file organization (tests/scripts moved) ✅
- **QW#9:** Configuration & data organization (THIS ONE)
- **QW#10:** Remove shim files (next after QW#9)

---

## 📌 Notes

- **Low Risk:** We're only moving files and updating paths
- **Easy to Rollback:** If something breaks, just move files back
- **Tests Verify:** Running tests will catch any path issues
- **Git Tracks:** All moves tracked in git history

---

## ⏱️ Time Estimate

| Phase | Time |
|-------|------|
| Create directories | 2 min |
| Move files | 5 min |
| Update Python code | 15 min |
| Update Docker files | 5 min |
| Update scripts | 5 min |
| Test & verify | 10 min |
| **TOTAL** | **42 min** |

---

## 🎯 Next Steps

After QW#9 is complete and tested:
1. Commit with message: `QW#9: Organize configuration and data files`
2. Create QW#10 plan (remove 35 shim files)
3. Root directory will be down to 45 files (from 90)
4. After QW#10: Only 15 files in root (professional!)
