"""
Compatibility shim: Re-exports from src.utils.error_model
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.utils.error_model import *
"""

from src.utils.error_model import *

__all__ = [name for name in dir() if not name.startswith("_")]
