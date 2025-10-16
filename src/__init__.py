"""
SIFU Backend - Hexagonal Architecture

Layers:
  - api:            HTTP routers (REST endpoints)
  - domain:         Business logic (services, models, processors)
  - infrastructure: External integrations (database, cache, auth)
  - application:    App-level concerns (bootstrap, config, security)
  - utils:          Shared utilities (constants, errors, tracing)
"""

__version__ = "1.0.0"
