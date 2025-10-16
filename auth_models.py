"""
Compatibility shim: Re-exports from src.infrastructure.auth_models
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.auth_models import *
"""

from src.infrastructure.auth_models import *

__all__ = [name for name in dir() if not name.startswith("_")]
