# Changelog

All notable changes in SIFU are listed here in chronological order. Historical session notes that were previously standalone changelog files now live under [docs/archive/](docs/archive/).

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
