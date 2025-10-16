"""
Compatibility shim: Re-exports from src.infrastructure.https_middleware
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.https_middleware import *
"""

from src.infrastructure.https_middleware import *

__all__ = [name for name in dir() if not name.startswith("_")]
