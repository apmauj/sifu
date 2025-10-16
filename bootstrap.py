"""
Compatibility shim: Re-exports from src.application.bootstrap
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.application.bootstrap import *
"""

from src.application.bootstrap import *

__all__ = [name for name in dir() if not name.startswith("_")]
