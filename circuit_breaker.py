"""
Compatibility shim: Re-exports from src.infrastructure.circuit_breaker
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.infrastructure.circuit_breaker import *
"""

from src.infrastructure.circuit_breaker import *

__all__ = [name for name in dir() if not name.startswith("_")]
