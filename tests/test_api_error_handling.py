import logging

import pytest
from fastapi import HTTPException

from src.api.error_handling import log_and_raise_http_exception


class _ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def test_log_and_raise_http_exception_uses_error_detail_by_default():
    logger = logging.getLogger("test.api_error_handling.default")
    handler = _ListHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)

    with pytest.raises(HTTPException) as exc_info:
        log_and_raise_http_exception(
            logger=logger,
            status_code=500,
            log_message="failed operation",
            error=RuntimeError("boom"),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "boom"
    assert any("failed operation: boom" in msg for msg in handler.messages)


def test_log_and_raise_http_exception_accepts_custom_detail():
    logger = logging.getLogger("test.api_error_handling.custom")
    handler = _ListHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)

    with pytest.raises(HTTPException) as exc_info:
        log_and_raise_http_exception(
            logger=logger,
            status_code=503,
            log_message="health failed",
            error=ValueError("db unavailable"),
            detail="Service unavailable",
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Service unavailable"
    assert any("health failed: db unavailable" in msg for msg in handler.messages)
