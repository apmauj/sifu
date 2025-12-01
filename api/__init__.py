"""
Compatibility shim: Re-exports from src.api.routers
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.api.routers import *
"""

from src.api.routers.ui import router as ui_router
from src.api.routers.ur import router as ur_router
from src.api.routers.exchange import router as exchange_router
from src.api.routers.brou import router as brou_router
from src.api.routers.system import router as system_router

__all__ = [
    "ui_router",
    "ur_router",
    "exchange_router",
    "brou_router",
    "system_router",
]
