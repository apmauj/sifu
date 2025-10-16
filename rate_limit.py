"""
Compatibility shim: Re-exports from src.infrastructure.rate_limit
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.rate_limit import *
"""

from src.infrastructure.rate_limit import *

__all__ = [name for name in dir() if not name.startswith("_")]
