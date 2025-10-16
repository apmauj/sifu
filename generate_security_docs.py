"""
Compatibility shim: Re-exports from src.application.generate_security_docs
This file ensures backward compatibility after moving to hexagonal architecture.
All new code should import from: from src.application.generate_security_docs import *
"""

from src.application.generate_security_docs import *

__all__ = [name for name in dir() if not name.startswith("_")]
