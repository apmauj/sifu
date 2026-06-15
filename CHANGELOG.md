# Changelog

All notable changes in SIFU are listed here in chronological order. Historical session notes that were previously standalone changelog files now live under [docs/archive/](docs/archive/).

## 2026-06-15

### v2.0.0 - Migration to Cloud Hosting ($0/month)

Complete migration from self-hosted NUC (Docker + Cloudflare Tunnel) to free cloud hosting.

**Hosting changes:**
- Frontend: GitHub Pages (static, auto-deploy on push to master)
- Backend: Render Free Tier (auto-deploy from repo, hibernates after 15 min inactivity)
- Database: SQLite on Render's ephemeral filesystem (/tmp/sifu_data.db)
- Keep-alive: GitHub Actions workflow pings backend during business hours (Mon-Fri 7-21 UY)

**Backend changes:**
- Removed `src/infrastructure/https_middleware.py` — Render terminates TLS at load balancer; HTTP-to-HTTPS redirect unnecessary. Security headers (HSTS, CSP, X-Frame-Options, etc.) moved inline into `main.py` as `SecurityHeadersMiddleware`.
- Removed `src/application/secret_manager.py` — Secrets managed via Render Dashboard → Environment, not local .env files.
- Removed `scripts/setup/setup_https.py`, `scripts/setup/setup_rbac.py`, `scripts/setup/start_secure.py` — Docker/NUC-specific scripts no longer applicable.
- Rewrote `src/application/config_validator.py` — Uses `os.getenv()` directly instead of `secret_manager`. Updated validations for Render environment (DATABASE_PATH, MONITORING_TOTP_SECRET, etc.).
- Rewrote `src/application/verify_security.py` — Replaced `secret_manager` dependency with direct `os.getenv()` checks.
- Added `BackendWakeOverlay` component — Shows informative overlay during Render cold starts (~30s first request).
- Fixed stale closure bug in `App.jsx` — `setShowWakeOverlay(false)` called unconditionally to prevent invisible overlay blocking all UI.
- Added `render.yaml` and `runtime.txt` for Render deployment configuration.
- Updated `validate_deploy.py` for Render (checks env vars, requirements.txt, render.yaml instead of Docker artifacts).

**Frontend changes:**
- Fixed Husky pre-commit hooks on Windows — `npx --no-install` prefix for ESLint resolution, pinned `eslint@8.57.1` for peer dep compatibility.
- Optimized lint-staged — Removed full test suite (627 tests, ~2min) from pre-commit; only ESLint (~15s). Tests run in CI instead.
- Fixed `App.test.jsx` — `getAllByText()` instead of `getByText()` for elements appearing in both overlay and footer.

**CI/CD changes:**
- Updated all GitHub Actions workflows to `setup-node@v5`, `upload-pages-artifact@v4`, `deploy-pages@v5` — Addresses Node.js 20 deprecation warnings.
- Removed `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` env var from workflows.
- Removed Docker Hub publish workflow (no longer needed).
- Removed self-hosted runner workflow (no longer needed).
- Removed tunnel-guard workflow (no longer needed).

**Documentation:**
- Rewrote `README.md` — Reflects current architecture (GitHub Pages + Render), removes Docker/tunnel references, adds Render env vars table.
- Updated `CHANGELOG.md` — This entry.

**Deleted files:**
- `src/application/secret_manager.py`
- `src/application/generate_security_docs.py`
- `src/infrastructure/https_middleware.py`
- `scripts/setup/setup_https.py`
- `scripts/setup/setup_rbac.py`
- `scripts/setup/start_secure.py`
- `config/docker/` directory
- `pip_audit_*.json` files

## 2026-04-19

### v1.5.0 - UR Alias Retirement (Release)

- Removed legacy UR field aliases used by compatibility layers and request-body mapping (`año_inicio`, `mes_inicio`, `año_fin`, `mes_fin`, plus prior UR model aliases) and standardized on canonical `year/month/value`.
- Kept public UR routes unchanged (for example, `/api/ur/latest`, `/api/ur/range`); impact is on payload/model aliases and compatibility helpers.
- Cleaned up domain and persistence models to be canonical-only for UR records.
- Tightened CI guardrails to fail on legacy alias regressions.

### v1.4.0 - Architecture V2 Phase 4 Hardening (Changelog-only milestone)

- Completed phase 4 hardening path for architecture V2 with CI guardrails and canonical UR test migration.
- This milestone is intentionally documented in changelog only (no public tag/release), because there is no clean isolated commit boundary before the final v1.5.0 alias-removal cut.

### v1.3.0 - Python 3.12 Baseline Promotion (Release)

- Promoted Python 3.12 as the official runtime baseline for backend docs, Docker, and CI.
- Updated backend CI and security workflows to use explicit Python 3.12 setup.
- Added impact measurement guidance for the Python 3.12 upgrade.

## 2026-04-18

### v1.2.0 - Node 24 Migration, CI Stabilization, and Workflow Hardening

- Migrated GitHub Actions workflows to Node 24-compatible action majors.
- Added explicit Node 24 opt-in flags to key workflows during validation.
- Stabilized frontend builds in CI using deterministic installs.
- Hardened tunnel recovery and deployment behavior to avoid loops and accidental redeploys.
- Updated backend async test execution in CI and removed flaky demo-test contamination.
- Refreshed release/version guidance and backend prerequisites in the main README.

## 2025-12-01

### v1.1.0 - Architecture Adjustments and Improvements

- Published architecture refactoring batch (QW#1-10) focused on layered organization, structure cleanup, and compatibility consolidation.

## 2025-10-11

### Debugging Session - Critical Fixes

- Fixed SSL verification issues for INE/BHU source downloads by scoping `verify=False` to the affected government hosts.
- Reverted frontend exchange-rate routes to match the backend contract and avoid 404s.
- Backfilled missing UR values for September and October 2025 when BHU source data was unavailable.
- Corrected backend tests to expect the `verify=False` parameter.

### Status

- This entry documents a debugging and stabilization session rather than a product release.

## 2025-07-20

### v1.0.0 - Initial Baseline (Release)

- Initial project baseline: FastAPI backend, React frontend, containerization, i18n, tests, and base documentation.
