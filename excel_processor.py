"""
Compatibility shim: Re-exports from src.domain.excel_processor
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.domain.excel_processor import *
"""

from src.domain.excel_processor import *

__all__ = [name for name in dir() if not name.startswith("_")]
