"""Shared API error-handling helpers for router-level exception normalization."""

from fastapi import HTTPException


def log_and_raise_http_exception(
    *,
    logger,
    status_code: int,
    log_message: str,
    error: Exception,
    detail: str | None = None,
) -> None:
    """Log an exception with context and raise an HTTPException."""
    logger.error("%s: %s", log_message, error)
    raise HTTPException(status_code=status_code, detail=detail or str(error))