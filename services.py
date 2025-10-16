"""
Compatibility shim: Re-exports from src.domain.services
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.domain.services import *
"""

from src.domain.services import *

__all__ = [name for name in dir() if not name.startswith("_")]
