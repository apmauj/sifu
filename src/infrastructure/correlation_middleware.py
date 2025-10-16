"""
Correlation ID middleware for distributed tracing.

This module provides middleware to add correlation IDs to all requests,
enabling distributed tracing across the application.
"""

import uuid
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Correlation ID header name
CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds correlation IDs to all requests for distributed tracing.

    This middleware:
    - Generates a unique correlation ID for each request
    - Adds it to request headers for downstream services
    - Includes it in response headers for client tracing
    - Makes it available in request state for logging
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get correlation ID from request header or generate new one
        correlation_id = self._get_or_create_correlation_id(request)

        # Add to request state for use in handlers
        request.state.correlation_id = correlation_id

        # Add to request headers for downstream services
        request.headers.__dict__["_list"].append(
            (CORRELATION_ID_HEADER.encode(), correlation_id.encode())
        )

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response

    def _get_or_create_correlation_id(self, request: Request) -> str:
        """Get correlation ID from request header or create a new one."""
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)

        if not correlation_id:
            # Generate new correlation ID
            correlation_id = str(uuid.uuid4())

        return correlation_id


def get_correlation_id(request: Request) -> Optional[str]:
    """Get the correlation ID from the current request."""
    return getattr(request.state, "correlation_id", None)


def setup_correlation_logging():
    """Configure logging to include correlation IDs."""

    class CorrelationIdFilter(logging.Filter):
        """Logging filter to add correlation ID to log records."""

        def __init__(self, request: Optional[Request] = None):
            super().__init__()
            self.request = request

        def filter(self, record):
            # Try to get correlation ID from current request context
            correlation_id = None

            # This is a simplified approach - in production you might want
            # to use context variables or thread-local storage
            try:
                import asyncio

                # Get current task
                current_task = asyncio.current_task()
                if current_task and hasattr(current_task, "request"):
                    correlation_id = getattr(
                        current_task.request.state, "correlation_id", None
                    )
            except Exception:
                pass

            # Add correlation ID to log record
            record.correlation_id = correlation_id or "NO_CORRELATION_ID"
            return True

    # Add filter to root logger
    correlation_filter = CorrelationIdFilter()
    logging.getLogger().addFilter(correlation_filter)

    # Update existing loggers
    for name in ["uvicorn", "uvicorn.access", "fastapi", "__main__"]:
        logger = logging.getLogger(name)
        logger.addFilter(correlation_filter)


def get_correlation_logger(name: str) -> logging.Logger:
    """Get a logger configured with correlation ID support."""
    logger = logging.getLogger(name)

    # Ensure correlation filter is added
    has_correlation_filter = any(
        isinstance(f, type("CorrelationIdFilter", (), {})) for f in logger.filters
    )

    if not has_correlation_filter:

        class CorrelationIdFilter(logging.Filter):
            def filter(self, record):
                record.correlation_id = getattr(
                    record, "correlation_id", "NO_CORRELATION_ID"
                )
                return True

        logger.addFilter(CorrelationIdFilter())

    return logger


# Utility functions for correlation ID management
def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def validate_correlation_id(correlation_id: str) -> bool:
    """Validate that a correlation ID is properly formatted."""
    try:
        uuid.UUID(correlation_id)
        return True
    except (ValueError, TypeError):
        return False
