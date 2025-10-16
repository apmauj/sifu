"""
Compatibility shim: Re-exports from src.application.alerts
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.application.alerts import *
"""

from src.application.alerts import *

__all__ = [name for name in dir() if not name.startswith("_")]
