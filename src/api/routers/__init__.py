"""SIFU API routers package.

Modular routers for different domain areas:
- ui.py: Unidad Indexada (UI) endpoints
- ur.py: Unidad Reajustable (UR) endpoints
- exchange.py: Exchange rate endpoints
- brou.py: BROU exchange rate endpoints
- system.py: System, health, and metrics endpoints
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
