#!/usr/bin/env python3
"""
Script to create compatibility shims for all moved files.
This ensures backward compatibility after hexagonal architecture migration.
"""

import os

shims = {
    # Root level shims for backward compatibility
    "constants.py": "src.utils.constants",
    "error_model.py": "src.utils.error_model",
    "models.py": "src.domain.models",
    "pydantic_models.py": "src.domain.pydantic_models",
    "services.py": "src.domain.services",
    "brou_processor.py": "src.domain.brou_processor",
    "excel_processor.py": "src.domain.excel_processor",
    "exchange_utils.py": "src.domain.exchange_utils",
    "database.py": "src.infrastructure.database",
    "database_optimizer.py": "src.infrastructure.database_optimizer",
    "auth_middleware.py": "src.infrastructure.auth_middleware",
    "auth_models.py": "src.infrastructure.auth_models",
    "auth_routes.py": "src.infrastructure.auth_routes",
    "auth_service.py": "src.infrastructure.auth_service",
    "https_middleware.py": "src.infrastructure.https_middleware",
    "metrics_middleware.py": "src.infrastructure.metrics_middleware",
    "correlation_middleware.py": "src.infrastructure.correlation_middleware",
    "rate_limit.py": "src.infrastructure.rate_limit",
    "circuit_breaker.py": "src.infrastructure.circuit_breaker",
    "health_checks.py": "src.infrastructure.health_checks",
    "metrics.py": "src.infrastructure.metrics",
    "alerts.py": "src.application.alerts",
    "bootstrap.py": "src.application.bootstrap",
    "config_validator.py": "src.application.config_validator",
    "secret_manager.py": "src.application.secret_manager",
    "secure_logging.py": "src.application.secure_logging",
    "security_monitor.py": "src.application.security_monitor",
    "security_utils.py": "src.application.security_utils",
    "opentelemetry_setup.py": "src.application.opentelemetry_setup",
    "generate_security_docs.py": "src.application.generate_security_docs",
    "validate_deploy.py": "src.application.validate_deploy",
    "verify_security.py": "src.application.verify_security",
}

count = 0
for filename, module in shims.items():
    content = f'''"""
Compatibility shim: Re-exports from {module}
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from {module} import *
"""

from {module} import *

__all__ = [name for name in dir() if not name.startswith("_")]
'''
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    count += 1
    print(f"✓ Created shim: {filename}")

print(f"\n✅ Total shims created: {count}")
