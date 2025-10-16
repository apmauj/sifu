"""
Compatibility shim: Re-exports from src.infrastructure.auth_routes
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.auth_routes import *
"""

from src.infrastructure.auth_routes import *

__all__ = [name for name in dir() if not name.startswith("_")]
