"""Core types and orchestrator for health checks."""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None  # type: ignore[assignment]
    PSUTIL_AVAILABLE = False


class HealthStatus:
    """Health status enumeration."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check."""

    def __init__(
        self,
        name: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None,
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.response_time = response_time
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "response_time_ms": round(self.response_time * 1000, 2)
            if self.response_time
            else None,
            "timestamp": self.timestamp.isoformat(),
        }


class HealthChecker:
    """Advanced health checker for all system components."""

    def __init__(self):
        self._checks: List[callable] = []
        self._last_check_time: Optional[datetime] = None
        self._check_cache: Optional[Dict[str, Any]] = None
        self._cache_duration = timedelta(seconds=30)

    def add_check(self, check_func: callable):
        """Add a health check function."""
        self._checks.append(check_func)

    def _should_use_cache(self) -> bool:
        """Check if cached results should be used."""
        if self._last_check_time is None or self._check_cache is None:
            return False
        return datetime.utcnow() - self._last_check_time < self._cache_duration

    def run_all_checks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Run all health checks and return comprehensive results."""

        if not force_refresh and self._should_use_cache():
            return self._check_cache

        start_time = time.time()
        results = []
        overall_status = HealthStatus.HEALTHY

        for check_func in self._checks:
            try:
                check_start = time.time()
                result = check_func()
                check_time = time.time() - check_start

                if isinstance(result, dict):
                    result = HealthCheckResult(
                        name=result.get("name", "unknown"),
                        status=result.get("status", HealthStatus.UNKNOWN),
                        message=result.get("message", ""),
                        details=result.get("details", {}),
                        response_time=check_time,
                    )

                if isinstance(result, HealthCheckResult):
                    results.append(result.to_dict())

                    if result.status == HealthStatus.CRITICAL:
                        overall_status = HealthStatus.CRITICAL
                    elif (
                        result.status == HealthStatus.WARNING
                        and overall_status == HealthStatus.HEALTHY
                    ):
                        overall_status = HealthStatus.WARNING

            except Exception as e:
                error_result = HealthCheckResult(
                    name=getattr(check_func, "__name__", "unknown_check"),
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=time.time() - check_start,
                )
                results.append(error_result.to_dict())
                overall_status = HealthStatus.CRITICAL

        total_time = time.time() - start_time

        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "total_checks": len(results),
            "healthy_checks": len(
                [r for r in results if r["status"] == HealthStatus.HEALTHY]
            ),
            "warning_checks": len(
                [r for r in results if r["status"] == HealthStatus.WARNING]
            ),
            "critical_checks": len(
                [r for r in results if r["status"] == HealthStatus.CRITICAL]
            ),
            "total_response_time_ms": round(total_time * 1000, 2),
            "checks": results,
            "system_info": self._get_system_info(),
        }

        self._last_check_time = datetime.utcnow()
        self._check_cache = response

        return response

    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}

        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2),
                "memory_total_mb": round(
                    psutil.virtual_memory().total / 1024 / 1024, 2
                ),
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "uptime_seconds": int(time.time() - psutil.boot_time()),
            }
        except Exception:
            return {"error": "Could not retrieve system information"}
