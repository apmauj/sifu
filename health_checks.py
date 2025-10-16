"""
Compatibility shim: Re-exports from src.infrastructure.health_checks
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.health_checks import *
"""

from src.infrastructure.health_checks import *

__all__ = [name for name in dir() if not name.startswith("_")]
