# SIFU – Architecture Compliance Audit and Action Plan

Date: 2025-10-15

This document reviews the current repository against the guidelines in `docs/Arqui.txt` and the Copilot Workspace Instructions. It highlights what’s compliant, partial, or missing, then proposes a prioritized plan.

## Summary at a glance

- Overall: Strong alignment for a single FastAPI service with observability, security middleware, caching, jobs, and CI/CD. Frontend follows Vite + modular panels with i18n and theming system.
- Biggest gaps: Monolith service layout (no src/ hexagonal structure), DB per-service not enforced (SQLite default, Postgres optional), lack of OpenAPI design-first and RFC7807 error shape, limited tracing (no OpenTelemetry), Docker image hardening, and missing contract tests.

Legend: [OK] compliant • [~] partial • [–] missing

## 1) Principles and microservices practices

- Domain boundaries (DDD): [~] Single service aggregates UI/UR/Exchange/BROU. Clear service classes exist (`UIService`, `URService`, `ExchangeRateService`), but code is in flat root; not hexagonal src-layout.
- API-first contracts (OpenAPI/AsyncAPI): [~] FastAPI auto-docs, tags and models exist; no separate design-first OpenAPI nor SDK generation.
- Autonomy and CI: [OK] Unified CI with separate jobs; backend image built and tagged.
- Backward compatibility: [OK] Notable for `/api/brou/current` with `full=true` option.

## 2) Communication between services

- Sync REST with timeouts/retry/circuit-breaker: [OK] Circuit breakers for INE/BHU/BROU/BCU used in processors. Retries/backoff not centralized; requests use timeouts.
- Async/eventing/outbox: [–] No messaging or outbox/CDC.

## 3) Resilience and reliability

- Idempotency: [–] No Idempotency-Key handling on POST endpoints.
- Patterns: [OK] Circuit breaker; [OK] rate limit; [OK] timeouts; [~] retry/jitter not standardized.
- Health/metrics: [OK] `/api/health/*`, metrics middleware, advanced health with cache freshness, DB checks.
- Uniform error management (RFC7807): [–] Uses JSON with custom shapes, not problem+json.

## 4) Config, packaging, deploy

- 12-Factor: [~] Many env vars present; CORS, scheduler, URLs via env. Some defaults permissive; secrets (JWT key) defaulting to generated key in dev.
- Containers: [~] Dockerfile exists; image hardening (non-root user, slim base, multi-stage) not fully verified.
- IaC/K8s: [–] No Helm/Kustomize/Terraform in repo.
- Release strategies: [~] CI supports image tags; no canary/feature flags infra.

## 5) Observability

- Traces/metrics/logs: [~] Metrics middleware present. Correlation ID middleware exists and headers set; structured logging partially. No OpenTelemetry export.
- Correlation IDs: [OK] Added to responses and logging filter setup.
- Dashboards/alerts: [OK] In-app dashboard and alert manager with rules.

## 6) Security

- AuthZ/AuthN: [~] JWT demo auth; TOTP guard for monitoring. No OIDC provider integration.
- TLS/headers: [OK] HTTPS redirect and security headers in prod; BROU/INE/INE-UR requests use verify=False with justified comment (gov hosts) but still risky.
- Secrets: [~] JWT secret via env with dev fallback; no vault integration.
- Scans: [OK] CI has pip-audit and npm audit jobs.
- CORS/CSP: [~] CORS restrictive by default; no CSP.

## 7) Governance and cadence

- SemVer/Commits/Changelog: [~] Changelog files exist; commit conventions not enforced by CI.
- ADRs: [–] No ADRs folder; some docs present.

## 8) Data management

- DB per service: [~] Single DB models for all domains; SQLite default; Postgres via env possible. No migrations.
- No cross-service queries: [OK] Single service only.

## 9) Backend structure and patterns

- FastAPI app with middlewares and routers: [OK] All endpoints in `main.py`; auth router separated. Health/metrics/alerts/dashboard endpoints implemented.
- Services and processors: [OK] `services.py`, `excel_processor.py`, `brou_processor.py` structured and tested.
- Caching: [OK] In-memory caches with locks (`_cache_lock`) for BCU/BROU; warmers and data guard jobs.
- Input validation: [OK] `InputValidator` and `SecurityValidator` used.
- Job manager: [OK] In-memory async job pattern with 202 + polling for exchange refresh.
- Error messages: [OK] Centralized in `constants.py`.

## 10) Frontend conventions (Vite + React)

- API base from env with normalization: [OK] `getApiBaseUrl` uses `VITE_PUBLIC_API_URL` and ensures `/api`.
- Services in `frontend/src/services/`: [OK] Follows repo instruction; multiple services present.
- i18n: [OK] locales present and tested; no heavy dependencies.
- Theming system: [OK] themes, utils, helpers with tests and docs.
- UI compatibility: [OK] `/api/brou/current` backward-compat supported.

## 11) Testing

- Backend: [OK] Many pytest files; flag `SIFU_SKIP_BOOTSTRAP=1` used; health/circuit/perf tests provided.
- Frontend: [OK] Vitest + RTL suite extensive; helpers in `src/test/setup.jsx`.
- Contract tests: [–] No Schemathesis/Pact tests.
- Migrations: [–] No Alembic tests.

## 12) CI/CD

- Single workflow `ci-cd.yml`: [OK] security audits, backend/frontend tests, tunnel-guard, image build, frontend build and deploy, summary.
- Tunnel guard with fallback: [OK].
- Build metadata to footer: [~] Vite env expose used; footer component exists.

## 13) Notable risks and tech debt

- Lack of OpenTelemetry tracing and exporters; only correlation IDs.
- No RFC7807 standard errors; mixed JSON responses across endpoints.
- No Alembic migrations; SQLite default for dev; Postgres not enforced.
- Scraping and requests with `verify=False` (INE/BHU) – documented but should be minimized or pinned certs added.
- In-memory job manager and caches (single-instance OK; scale-out would need external store).
- Single-module layout; large `main.py` file with many endpoints.

---

## Prioritized action plan

Short-term (1–2 sprints)

1) Standardize error format (RFC 7807) [backend]
   - Add a small error mapper utility returning `application/problem+json` with fields: type, title, status, detail, instance, trace_id.
   - Update exception handlers globally; keep existing shapes as legacy when `?legacy=true` if needed.

2) Observability upgrade – OpenTelemetry (100% OSS) [backend]
   - Add `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp` (all Open Source).
   - Instrument FastAPI app, HTTP client (requests), SQLAlchemy; propagate correlation IDs.
   - Expose `/api/metrics/prometheus` with `prometheus-client` for Prometheus (OSS) scrape if needed. No paid services required.

3) CI enhancements and quality gates
   - Add mypy (strict) job with type hints for services and processors.
   - Enforce Conventional Commits via a lightweight check.
   - Add Schemathesis contract smoke against generated OpenAPI.

4) Security posture
   - Add CSP header in prod (with report-only first) via middleware; restrict `frame-ancestors`.
   - Ensure `JWT_SECRET_KEY` required in prod (fail-fast if missing).

5) Database migrations
   - Introduce Alembic; generate baseline for current tables (UI/UR/Exchange/BROU).
   - Add CI step to run migrations during tests using SQLite.

6) Split oversized `main.py`
  
   - Create sub-routers: `api/ui.py`, `api/ur.py`, `api/exchange.py`, `api/system.py`, `api/brou.py`, and include in `main.py`.
   - Keep public API unchanged.
  
Medium-term (3–6 sprints)

- **Design-first OpenAPI and SDKs**
  - Export OpenAPI yaml at build; progressively move to design-first for new resources.
  - Generate typed frontend client (openapi-typescript + openapi-fetch) and/or Python SDK.

- **Retry/backoff utilities**
  - Wrap external requests with standardized retry (exponential backoff + jitter), honoring circuit breaker state.

- **Docker hardening**
  - Multi-stage slim image, non-root user, read-only FS, healthcheck; verify existing Dockerfile or add a hardened variant.

- **Tracing + dashboards (OSS)**
  - Configure OpenTelemetry Collector (OSS) + Prometheus (OSS) for metrics, and Jaeger or Tempo (OSS) for tracing. Grafana OSS (self-hosted) is optional for dashboards; Grafana Cloud is not required.
  - Wire correlation ID to trace/span IDs.

Long-term

- **Service extraction (if needed)**
  - Consider extracting BROU/BCU as a “rates-gateway” service and UI/UR as “index-service”. Each with its own DB.

- **Eventing/outbox (optional)**
  - If other consumers exist, publish events on refresh (UI/UR/rates) using outbox + CDC.

## Concrete tasks checklist (initial)

- [ ] Backend: Add RFC7807 error handler (global exception handlers) and constants for common problem types.
- [ ] Backend: Introduce routers split without breaking routes; update imports/tests.
- [ ] Backend: Add OpenTelemetry instrumentation (FastAPI, requests, SQLAlchemy) gated by env flags.
- [ ] Backend: Add Alembic with baseline migration; dev docs to run `alembic upgrade head`.
- [ ] CI: Add mypy strict job and Schemathesis smoke; keep runtime fast.
- [ ] Security: CSP header (report-only first), prod check for JWT secret.
- [ ] Docs: Add ADRs folder and initial ADR for observability and error model.

## Notes on alignment with Copilot Workspace Instructions (SIFU)

- Health/metrics: In place; `HealthChecker.add_check` caching respected.
- Cache usage: Access via `_cache_lock` done correctly.
- Frontend API base `/api` normalization honored in CI Pages build.
- Theming v2 guidance and tests are present; changes must keep tests green (current suite is large).
- No heavy deps added yet; proposed ones (OTEL, Alembic) are standard and can be made optional via extras.

## Suggested owners and effort

- Backend platform (observability, error model, routers): 2–3 dev-days.
- CI and migrations: 1–2 dev-days.
- Security headers and prod checks: 0.5–1 dev-day.
- Docs/ADR and OpenAPI improvements: 1–2 dev-days.

---

## Appendix A: Costs and licensing (OSS stack)

- OpenTelemetry SDK and Collector: Open Source (Apache 2.0). No license cost.
- Prometheus (metrics): Open Source (Apache 2.0). No license cost.
- Jaeger (tracing): Open Source (Apache 2.0). No license cost.
- Grafana OSS (dashboards): Open Source (AGPLv3). Free when self-hosted. Grafana Cloud has paid tiers but is NOT required.
- Tempo/Loki (Grafana Labs projects): Open Source. Optional.
- No-infra profile: You can keep only in-app metrics (`/api/metrics`), structured logs, and health checks without deploying Collector/Prometheus/Grafana. This yields basic observability at zero cost.

Prepared by: Architecture Review
