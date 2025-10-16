"""
Compatibility shim: Re-exports from src.application.secret_manager
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.application.secret_manager import *
"""

from src.application.secret_manager import *

__all__ = [name for name in dir() if not name.startswith("_")]
