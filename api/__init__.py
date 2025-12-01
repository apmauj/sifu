"""
Compatibility shim: Re-exports from src.api.routers
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.api.routers import *
"""

from src.api.routers import *

__all__ = [
    "ui_router",
    "ur_router",
    "exchange_router",
    "brou_router",
    "system_router",
]
