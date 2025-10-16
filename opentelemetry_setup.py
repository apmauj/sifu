"""
Compatibility shim: Re-exports from src.application.opentelemetry_setup
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.application.opentelemetry_setup import *
"""

from src.application.opentelemetry_setup import *

__all__ = [name for name in dir() if not name.startswith("_")]
