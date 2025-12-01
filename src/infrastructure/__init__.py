"""
Infrastructure Layer - External Integrations

Exports:
  - database: SQLAlchemy session and engine setup
  - auth_*: Authentication and RBAC
  - *_middleware: HTTP middleware (HTTPS, CSP, correlation, metrics)
  - health_checks: Health check implementations
  - circuit_breaker: Circuit breaker for external calls
"""

# Infrastructure components are imported on-demand to manage dependencies
