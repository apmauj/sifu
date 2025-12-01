"""
Domain Layer - Business Logic

Exports:
  - models: SQLAlchemy ORM models (UIRecord, URRecord, etc)
  - services: Domain services (UIService, URService, ExchangeRateService)
  - processors: Data processors (ExcelProcessor, BROUProcessor)
"""

# Models are loaded lazily to avoid circular imports
# Services depend on models, so import after
