"""
Compatibility shim: Re-exports from src.infrastructure.metrics_middleware
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.metrics_middleware import *
"""

from src.infrastructure.metrics_middleware import *

__all__ = [name for name in dir() if not name.startswith("_")]
