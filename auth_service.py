"""
Compatibility shim: Re-exports from src.infrastructure.auth_service
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.auth_service import *
"""

from src.infrastructure.auth_service import *

__all__ = [name for name in dir() if not name.startswith("_")]
