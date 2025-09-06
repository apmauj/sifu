"""
Advanced health check system for SIFU application
Provides comprehensive health monitoring for all system components
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import text

from database import get_db
from brou_processor import BROUProcessor
from excel_processor import ExchangeRateBCUProcessor

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class HealthStatus:
    """Health status enumeration"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check"""

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
        """Convert to dictionary representation"""
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
    """Advanced health checker for all system components"""

    def __init__(self):
        self._checks: List[callable] = []
        self._last_check_time: Optional[datetime] = None
        self._check_cache: Optional[Dict[str, Any]] = None
        self._cache_duration = timedelta(seconds=30)  # Cache results for 30 seconds

    def add_check(self, check_func: callable):
        """Add a health check function"""
        self._checks.append(check_func)

    def _should_use_cache(self) -> bool:
        """Check if cached results should be used"""
        if self._last_check_time is None or self._check_cache is None:
            return False
        return datetime.utcnow() - self._last_check_time < self._cache_duration

    def run_all_checks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Run all health checks and return comprehensive results"""

        if not force_refresh and self._should_use_cache():
            return self._check_cache

        start_time = time.time()
        results = []
        overall_status = HealthStatus.HEALTHY

        # Run all health checks
        for check_func in self._checks:
            try:
                check_start = time.time()
                result = check_func()
                check_time = time.time() - check_start

                if isinstance(result, dict):
                    # Convert dict result to HealthCheckResult
                    result = HealthCheckResult(
                        name=result.get("name", "unknown"),
                        status=result.get("status", HealthStatus.UNKNOWN),
                        message=result.get("message", ""),
                        details=result.get("details", {}),
                        response_time=check_time,
                    )

                if isinstance(result, HealthCheckResult):
                    results.append(result.to_dict())

                    # Update overall status
                    if result.status == HealthStatus.CRITICAL:
                        overall_status = HealthStatus.CRITICAL
                    elif (
                        result.status == HealthStatus.WARNING
                        and overall_status == HealthStatus.HEALTHY
                    ):
                        overall_status = HealthStatus.WARNING

            except Exception as e:
                # Handle check failures
                error_result = HealthCheckResult(
                    name=getattr(check_func, "__name__", "unknown_check"),
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=time.time() - check_start,
                )
                results.append(error_result.to_dict())
                overall_status = HealthStatus.CRITICAL

        total_time = time.time() - start_time

        # Build comprehensive response
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

        # Cache results
        self._last_check_time = datetime.utcnow()
        self._check_cache = response

        return response

    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
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


# Individual health check functions


def check_database() -> HealthCheckResult:
    """Check database connectivity and basic operations"""
    start_time = time.time()

    try:
        db = next(get_db())
        # Test basic query
        result = db.execute(text("SELECT 1")).fetchone()

        if result and result[0] == 1:
            # Test more complex query - count records
            ui_count = db.execute(text("SELECT COUNT(*) FROM ui_records")).fetchone()[0]
            ur_count = db.execute(text("SELECT COUNT(*) FROM ur_records")).fetchone()[0]
            brou_count = db.execute(
                text("SELECT COUNT(*) FROM brou_records")
            ).fetchone()[0]

            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={
                    "ui_records": ui_count,
                    "ur_records": ur_count,
                    "brou_records": brou_count,
                    "total_records": ui_count + ur_count + brou_count,
                },
                response_time=time.time() - start_time,
            )
        else:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.CRITICAL,
                message="Database test query failed",
                response_time=time.time() - start_time,
            )

    except Exception as e:
        return HealthCheckResult(
            name="database",
            status=HealthStatus.CRITICAL,
            message=f"Database connection failed: {str(e)}",
            response_time=time.time() - start_time,
        )


def check_brou_api() -> HealthCheckResult:
    """Check BROU API availability"""
    start_time = time.time()

    try:
        processor = BROUProcessor()
        rates, is_from_brou, source_type = processor.get_current_rates()

        if rates:
            status = HealthStatus.HEALTHY if is_from_brou else HealthStatus.WARNING
            message = (
                "BROU API responding" if is_from_brou else "BROU API using cached data"
            )

            return HealthCheckResult(
                name="brou_api",
                status=status,
                message=message,
                details={
                    "source_type": source_type,
                    "currencies_count": len(rates),
                    "is_live": is_from_brou,
                },
                response_time=time.time() - start_time,
            )
        else:
            return HealthCheckResult(
                name="brou_api",
                status=HealthStatus.CRITICAL,
                message="BROU API not responding",
                response_time=time.time() - start_time,
            )

    except Exception as e:
        return HealthCheckResult(
            name="brou_api",
            status=HealthStatus.CRITICAL,
            message=f"BROU API check failed: {str(e)}",
            response_time=time.time() - start_time,
        )


def check_bcu_api() -> HealthCheckResult:
    """Check BCU API availability"""
    start_time = time.time()

    try:
        processor = ExchangeRateBCUProcessor()
        rates, is_from_bcu = processor.get_current_rates()

        if rates:
            status = HealthStatus.HEALTHY if is_from_bcu else HealthStatus.WARNING
            message = (
                "BCU API responding" if is_from_bcu else "BCU API using cached data"
            )

            return HealthCheckResult(
                name="bcu_api",
                status=status,
                message=message,
                details={"currencies_count": len(rates), "is_live": is_from_bcu},
                response_time=time.time() - start_time,
            )
        else:
            return HealthCheckResult(
                name="bcu_api",
                status=HealthStatus.CRITICAL,
                message="BCU API not responding",
                response_time=time.time() - start_time,
            )

    except Exception as e:
        return HealthCheckResult(
            name="bcu_api",
            status=HealthStatus.CRITICAL,
            message=f"BCU API check failed: {str(e)}",
            response_time=time.time() - start_time,
        )


def check_system_resources() -> HealthCheckResult:
    """Check system resource usage"""
    start_time = time.time()

    if not PSUTIL_AVAILABLE:
        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.WARNING,
            message="System resource monitoring not available (psutil not installed)",
            response_time=time.time() - start_time,
        )

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Define thresholds
        status = HealthStatus.HEALTHY
        issues = []

        if cpu_percent > 90:
            status = HealthStatus.CRITICAL
            issues.append(f"High CPU usage: {cpu_percent}%")
        elif cpu_percent > 75:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"Elevated CPU usage: {cpu_percent}%")

        if memory.percent > 90:
            status = HealthStatus.CRITICAL
            issues.append(f"High memory usage: {memory.percent}%")
        elif memory.percent > 80:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"Elevated memory usage: {memory.percent}%")

        if disk.percent > 95:
            status = HealthStatus.CRITICAL
            issues.append(f"High disk usage: {disk.percent}%")
        elif disk.percent > 85:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"Elevated disk usage: {disk.percent}%")

        message = "System resources OK" if not issues else "; ".join(issues)

        return HealthCheckResult(
            name="system_resources",
            status=status,
            message=message,
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / 1024 / 1024, 2),
                "memory_total_mb": round(memory.total / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            },
            response_time=time.time() - start_time,
        )

    except Exception as e:
        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.WARNING,
            message=f"Could not check system resources: {str(e)}",
            response_time=time.time() - start_time,
        )


def check_brou_cache_freshness() -> HealthCheckResult:
    """Check BROU cache freshness and data availability"""
    start_time = time.time()

    try:
        # Import here to avoid circular imports
        from main import brou_cache, _cache_lock

        with _cache_lock:
            cached = brou_cache

        if not cached:
            return HealthCheckResult(
                name="brou_cache",
                status=HealthStatus.CRITICAL,
                message="BROU cache is empty",
                details={"cache_status": "empty"},
                response_time=time.time() - start_time,
            )

        # Check data availability
        data_list = cached.get("data", [])
        if not data_list:
            return HealthCheckResult(
                name="brou_cache",
                status=HealthStatus.CRITICAL,
                message="BROU cache contains no data",
                details={"cache_status": "no_data", "data_count": 0},
                response_time=time.time() - start_time,
            )

        # Check data freshness
        updated_at = cached.get("updated_at")
        if not updated_at:
            return HealthCheckResult(
                name="brou_cache",
                status=HealthStatus.WARNING,
                message="BROU cache has no timestamp",
                details={"data_count": len(data_list), "timestamp": None},
                response_time=time.time() - start_time,
            )

        # Calculate age in minutes
        age_seconds = (datetime.utcnow() - updated_at).total_seconds()
        age_minutes = age_seconds / 60

        # Determine status based on age
        if age_minutes > 120:  # 2 hours
            status = HealthStatus.CRITICAL
            message = f"BROU cache is very stale ({age_minutes:.1f} minutes old)"
        elif age_minutes > 60:  # 1 hour
            status = HealthStatus.WARNING
            message = f"BROU cache is stale ({age_minutes:.1f} minutes old)"
        else:
            status = HealthStatus.HEALTHY
            message = f"BROU cache is fresh ({age_minutes:.1f} minutes old)"

        # Get source information
        source = cached.get("source", "UNKNOWN")
        source_type = cached.get("source_type", "unknown")

        # Count currencies
        currencies_count = len(data_list)
        usd_ebrou_present = any(
            rate.get("currency") == "USD_EBROU" for rate in data_list
        )

        return HealthCheckResult(
            name="brou_cache",
            status=status,
            message=message,
            details={
                "data_count": currencies_count,
                "age_minutes": round(age_minutes, 1),
                "age_seconds": int(age_seconds),
                "source": source,
                "source_type": source_type,
                "usd_ebrou_present": usd_ebrou_present,
                "last_updated": updated_at.isoformat() if updated_at else None,
                "is_fresh": age_minutes < 60,
            },
            response_time=time.time() - start_time,
        )

    except Exception as e:
        return HealthCheckResult(
            name="brou_cache",
            status=HealthStatus.CRITICAL,
            message=f"BROU cache check failed: {str(e)}",
            response_time=time.time() - start_time,
        )


def check_bcu_cache_freshness() -> HealthCheckResult:
    """Check BCU cache freshness and data availability (mirrors BROU pattern)."""
    start_time = time.time()

    try:
        from main import bcu_cache, _cache_lock  # local import to avoid circular

        with _cache_lock:
            cached = bcu_cache

        if not cached:
            return HealthCheckResult(
                name="bcu_cache",
                status=HealthStatus.CRITICAL,
                message="BCU cache is empty",
                details={"cache_status": "empty"},
                response_time=time.time() - start_time,
            )

        data_list = cached.get("data", [])
        if not data_list:
            return HealthCheckResult(
                name="bcu_cache",
                status=HealthStatus.CRITICAL,
                message="BCU cache contains no data",
                details={"cache_status": "no_data", "data_count": 0},
                response_time=time.time() - start_time,
            )

        updated_at = cached.get("updated_at")
        if not updated_at:
            return HealthCheckResult(
                name="bcu_cache",
                status=HealthStatus.WARNING,
                message="BCU cache has no timestamp",
                details={"data_count": len(data_list), "timestamp": None},
                response_time=time.time() - start_time,
            )

        age_seconds = (datetime.utcnow() - updated_at).total_seconds()
        age_minutes = age_seconds / 60

        if age_minutes > 120:
            status = HealthStatus.CRITICAL
            message = f"BCU cache is very stale ({age_minutes:.1f} minutes old)"
        elif age_minutes > 60:
            status = HealthStatus.WARNING
            message = f"BCU cache is stale ({age_minutes:.1f} minutes old)"
        else:
            status = HealthStatus.HEALTHY
            message = f"BCU cache is fresh ({age_minutes:.1f} minutes old)"

        return HealthCheckResult(
            name="bcu_cache",
            status=status,
            message=message,
            details={
                "data_count": len(data_list),
                "age_minutes": round(age_minutes, 1),
                "age_seconds": int(age_seconds),
                "last_updated": updated_at.isoformat() if updated_at else None,
                "is_fresh": age_minutes < 60,
            },
            response_time=time.time() - start_time,
        )
    except Exception as e:
        return HealthCheckResult(
            name="bcu_cache",
            status=HealthStatus.CRITICAL,
            message=f"BCU cache check failed: {str(e)}",
            response_time=time.time() - start_time,
        )


# Global health checker instance
health_checker = HealthChecker()

# Register all health checks
health_checker.add_check(check_database)
health_checker.add_check(check_brou_api)
health_checker.add_check(check_bcu_api)
health_checker.add_check(check_brou_cache_freshness)
health_checker.add_check(check_bcu_cache_freshness)
health_checker.add_check(check_system_resources)


# Health check endpoints
async def get_advanced_health(force_refresh: bool = False):
    """Get comprehensive health check results"""
    # Use synchronous call - health checks are designed to be fast
    result = health_checker.run_all_checks(force_refresh)
    return result


async def get_simple_health():
    """Get simple health status for load balancers"""
    # Use synchronous call - health checks are designed to be fast
    results = health_checker.run_all_checks()

    # Simple health: OK if no critical issues
    is_healthy = results["status"] != HealthStatus.CRITICAL

    return {
        "status": "ok" if is_healthy else "FAIL",
        "timestamp": results["timestamp"],
        "checks": results["total_checks"],
        "issues": results["critical_checks"] + results["warning_checks"],
    }
