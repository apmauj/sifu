#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Circuit Breaker Pattern Implementation for External API Calls

This module provides circuit breaker functionality to protect against cascading failures
when calling external APIs. It implements the circuit breaker pattern with configurable
thresholds and recovery mechanisms.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Circuit is open, requests fail fast
- HALF_OPEN: Testing if service has recovered

Usage:
    from src.infrastructure.circuit_breaker import CircuitBreaker, get_circuit_breaker

    # Get a circuit breaker for a specific service
    cb = get_circuit_breaker("INE_API")

    # Use it to protect API calls
    try:
        with cb:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
    except CircuitBreakerOpenException:
        # Circuit is open, handle gracefully
        return fallback_data
    except Exception as e:
        # Request failed, circuit breaker will count this as a failure
        raise
"""

import time
import logging
from contextlib import contextmanager
from threading import Lock
from typing import Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""

    pass


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker"""

    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: float = 60.0  # Seconds to wait before trying recovery
    success_threshold: int = 3  # Number of successes needed in half-open state
    timeout: float = 30.0  # Request timeout in seconds
    name: str = "default"  # Circuit breaker name for logging


class CircuitBreaker:
    """
    Circuit Breaker implementation for protecting external API calls

    This class implements the circuit breaker pattern to prevent cascading failures
    when calling external services. It monitors failures and temporarily stops
    making requests when a service appears to be down.
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._lock = Lock()

        logger.info(
            f"Circuit breaker '{config.name}' initialized: "
            f"failure_threshold={config.failure_threshold}, "
            f"recovery_timeout={config.recovery_timeout}s"
        )

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count"""
        with self._lock:
            return self._failure_count

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        return time.time() - self._last_failure_time >= self.config.recovery_timeout

    def _record_success(self):
        """Record a successful request"""
        with self._lock:
            self._success_count += 1
            self._failure_count = 0

            if self._state == CircuitBreakerState.HALF_OPEN:
                if self._success_count >= self.config.success_threshold:
                    # Service has recovered, close the circuit
                    self._state = CircuitBreakerState.CLOSED
                    self._success_count = 0
                    logger.info(
                        f"Circuit breaker '{self.config.name}' closed (service recovered)"
                    )

    def _record_failure(self):
        """Record a failed request"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._success_count = 0

            if self._state == CircuitBreakerState.CLOSED:
                if self._failure_count >= self.config.failure_threshold:
                    # Too many failures, open the circuit
                    self._state = CircuitBreakerState.OPEN
                    logger.warning(
                        f"Circuit breaker '{self.config.name}' opened "
                        f"(failure_count={self._failure_count})"
                    )

            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Failed during recovery test, go back to open
                self._state = CircuitBreakerState.OPEN
                logger.warning(
                    f"Circuit breaker '{self.config.name}' recovery failed, "
                    f"back to open state"
                )

    def _can_proceed(self) -> bool:
        """Check if request can proceed based on current state"""
        with self._lock:
            if self._state == CircuitBreakerState.CLOSED:
                return True
            elif self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_recovery():
                    # Time to try recovery
                    self._state = CircuitBreakerState.HALF_OPEN
                    self._success_count = 0
                    logger.info(
                        f"Circuit breaker '{self.config.name}' attempting recovery"
                    )
                    return True
                else:
                    return False
            elif self._state == CircuitBreakerState.HALF_OPEN:
                return True

            return False

    @contextmanager
    def __enter__(self):
        """Context manager entry - check if request can proceed"""
        if not self._can_proceed():
            logger.warning(
                f"Circuit breaker '{self.config.name}' is OPEN, failing fast"
            )
            raise CircuitBreakerOpenException(
                f"Circuit breaker '{self.config.name}' is open. "
                f"Last failure: {time.time() - self._last_failure_time:.1f}s ago"
            )
        yield

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record success or failure"""
        if exc_type is None:
            # No exception, request succeeded
            self._record_success()
        else:
            # Exception occurred, record failure
            self._record_failure()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function call protected by the circuit breaker

        Args:
            func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function call

        Raises:
            CircuitBreakerOpenException: If circuit is open
            Exception: Any exception raised by the function
        """
        with self:
            return func(*args, **kwargs)


# Global registry of circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_registry_lock = Lock()


def get_circuit_breaker(
    name: str, config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a specific service

    Args:
        name: Name of the service/API
        config: Optional configuration, uses defaults if not provided

    Returns:
        CircuitBreaker instance
    """
    global _circuit_breakers

    with _registry_lock:
        if name not in _circuit_breakers:
            if config is None:
                config = CircuitBreakerConfig(name=name)
            _circuit_breakers[name] = CircuitBreaker(config)

        return _circuit_breakers[name]


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Get all registered circuit breakers"""
    with _registry_lock:
        return _circuit_breakers.copy()


def reset_circuit_breaker(name: str) -> bool:
    """
    Reset a circuit breaker to closed state

    Args:
        name: Name of the circuit breaker

    Returns:
        True if reset was successful, False if circuit breaker doesn't exist
    """
    with _registry_lock:
        if name in _circuit_breakers:
            cb = _circuit_breakers[name]
            with cb._lock:
                cb._state = CircuitBreakerState.CLOSED
                cb._failure_count = 0
                cb._success_count = 0
                cb._last_failure_time = 0.0
            logger.info(f"Circuit breaker '{name}' reset to closed state")
            return True
    return False


def get_circuit_breaker_status(name: str) -> Optional[Dict]:
    """
    Get status information for a circuit breaker

    Args:
        name: Name of the circuit breaker

    Returns:
        Dictionary with status information or None if not found
    """
    with _registry_lock:
        if name in _circuit_breakers:
            cb = _circuit_breakers[name]
            with cb._lock:
                return {
                    "name": cb.config.name,
                    "state": cb._state.value,
                    "failure_count": cb._failure_count,
                    "success_count": cb._success_count,
                    "last_failure_time": cb._last_failure_time,
                    "time_since_last_failure": time.time() - cb._last_failure_time,
                    "failure_threshold": cb.config.failure_threshold,
                    "recovery_timeout": cb.config.recovery_timeout,
                    "success_threshold": cb.config.success_threshold,
                }
    return None


# Pre-configured circuit breakers for known external services
def initialize_default_circuit_breakers():
    """Initialize circuit breakers for known external services"""

    # INE API (Instituto Nacional de Estadística)
    ine_config = CircuitBreakerConfig(
        name="INE_API",
        failure_threshold=3,  # Open after 3 failures
        recovery_timeout=120.0,  # Wait 2 minutes before recovery
        success_threshold=2,  # Need 2 successes to close
        timeout=30.0,
    )
    get_circuit_breaker("INE_API", ine_config)

    # BHU API (Banco Hipotecario del Uruguay)
    bhu_config = CircuitBreakerConfig(
        name="BHU_API",
        failure_threshold=3,
        recovery_timeout=120.0,
        success_threshold=2,
        timeout=30.0,
    )
    get_circuit_breaker("BHU_API", bhu_config)

    # BROU API (Banco de la República Oriental del Uruguay)
    brou_config = CircuitBreakerConfig(
        name="BROU_API",
        failure_threshold=5,  # BROU might be more stable, higher threshold
        recovery_timeout=180.0,  # Wait 3 minutes before recovery
        success_threshold=3,  # Need 3 successes to close
        timeout=15.0,  # BROU has shorter timeout
    )
    get_circuit_breaker("BROU_API", brou_config)

    # BCU API (Banco Central del Uruguay)
    bcu_config = CircuitBreakerConfig(
        name="BCU_API",
        failure_threshold=3,
        recovery_timeout=120.0,
        success_threshold=2,
        timeout=20.0,
    )
    get_circuit_breaker("BCU_API", bcu_config)

    logger.info("Default circuit breakers initialized for external APIs")


# Initialize default circuit breakers on module import
initialize_default_circuit_breakers()


