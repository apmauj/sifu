"""
Compatibility shim: Re-exports from src.infrastructure.database_optimizer
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.database_optimizer import *
"""

from src.infrastructure.database_optimizer import *

__all__ = [name for name in dir() if not name.startswith("_")]
