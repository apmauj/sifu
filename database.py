"""
Compatibility shim: Re-exports from src.infrastructure.database
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.database import *
"""

from src.infrastructure.database import *

__all__ = [name for name in dir() if not name.startswith("_")]
