"""
Shared utilities module.

Exports:
  - constants: Configuration constants
  - error_model: RFC7807 error responses
  - opentelemetry_setup: OTel initialization
  - https_middleware: HTTPS/CSP middleware
  - metrics_middleware: Metrics collection
  - correlation_middleware: Request correlation
"""

from .constants import *  # noqa: F403
from .error_model import ProblemResponse, ProblemDetail, PROBLEM_TYPES

__all__ = [
    "ProblemResponse",
    "ProblemDetail",
    "PROBLEM_TYPES",
]
