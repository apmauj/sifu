"""
Advanced health check system for SIFU application
Provides comprehensive health monitoring for all system components
"""
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from brou_processor import BROUProcessor
from excel_processor import ExchangeRateBCUProcessor
from metrics import metrics_collector

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

    def __init__(self, name: str, status: str, message: str = "",
                 details: Optional[Dict[str, Any]] = None,
                 response_time: Optional[float] = None):
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
            "response_time_ms": round(self.response_time * 1000, 2) if self.response_time else None,
            "timestamp": self.timestamp.isoformat()
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
                        response_time=check_time
                    )

                if isinstance(result, HealthCheckResult):
                    results.append(result.to_dict())

                    # Update overall status
                    if result.status == HealthStatus.CRITICAL:
                        overall_status = HealthStatus.CRITICAL
                    elif result.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.WARNING

            except Exception as e:
                # Handle check failures
                error_result = HealthCheckResult(
                    name=getattr(check_func, '__name__', 'unknown_check'),
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=time.time() - check_start
                )
                results.append(error_result.to_dict())
                overall_status = HealthStatus.CRITICAL

        total_time = time.time() - start_time

        # Build comprehensive response
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "total_checks": len(results),
            "healthy_checks": len([r for r in results if r["status"] == HealthStatus.HEALTHY]),
            "warning_checks": len([r for r in results if r["status"] == HealthStatus.WARNING]),
            "critical_checks": len([r for r in results if r["status"] == HealthStatus.CRITICAL]),
            "total_response_time_ms": round(total_time * 1000, 2),
            "checks": results,
            "system_info": self._get_system_info()
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
                "memory_total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "uptime_seconds": int(time.time() - psutil.boot_time())
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
            brou_count = db.execute(text("SELECT COUNT(*) FROM brou_records")).fetchone()[0]

            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                details={
                    "ui_records": ui_count,
                    "ur_records": ur_count,
                    "brou_records": brou_count,
                    "total_records": ui_count + ur_count + brou_count
                },
                response_time=time.time() - start_time
            )
        else:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.CRITICAL,
                message="Database test query failed",
                response_time=time.time() - start_time
            )

    except Exception as e:
        return HealthCheckResult(
            name="database",
            status=HealthStatus.CRITICAL,
            message=f"Database connection failed: {str(e)}",
            response_time=time.time() - start_time
        )


def check_brou_api() -> HealthCheckResult:
    """Check BROU API availability"""
    start_time = time.time()

    try:
        processor = BROUProcessor()
        rates, is_from_brou, source_type = processor.get_current_rates()

        if rates:
            status = HealthStatus.HEALTHY if is_from_brou else HealthStatus.WARNING
            message = "BROU API responding" if is_from_brou else "BROU API using cached data"

            return HealthCheckResult(
                name="brou_api",
                status=status,
                message=message,
                details={
                    "source_type": source_type,
                    "currencies_count": len(rates),
                    "is_live": is_from_brou
                },
                response_time=time.time() - start_time
            )
        else:
            return HealthCheckResult(
                name="brou_api",
                status=HealthStatus.CRITICAL,
                message="BROU API not responding",
                response_time=time.time() - start_time
            )

    except Exception as e:
        return HealthCheckResult(
            name="brou_api",
            status=HealthStatus.CRITICAL,
            message=f"BROU API check failed: {str(e)}",
            response_time=time.time() - start_time
        )


def check_bcu_api() -> HealthCheckResult:
    """Check BCU API availability"""
    start_time = time.time()

    try:
        processor = ExchangeRateBCUProcessor()
        rates, is_from_bcu = processor.get_current_rates()

        if rates:
            status = HealthStatus.HEALTHY if is_from_bcu else HealthStatus.WARNING
            message = "BCU API responding" if is_from_bcu else "BCU API using cached data"

            return HealthCheckResult(
                name="bcu_api",
                status=status,
                message=message,
                details={
                    "currencies_count": len(rates),
                    "is_live": is_from_bcu
                },
                response_time=time.time() - start_time
            )
        else:
            return HealthCheckResult(
                name="bcu_api",
                status=HealthStatus.CRITICAL,
                message="BCU API not responding",
                response_time=time.time() - start_time
            )

    except Exception as e:
        return HealthCheckResult(
            name="bcu_api",
            status=HealthStatus.CRITICAL,
            message=f"BCU API check failed: {str(e)}",
            response_time=time.time() - start_time
        )


def check_system_resources() -> HealthCheckResult:
    """Check system resource usage"""
    start_time = time.time()

    if not PSUTIL_AVAILABLE:
        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.WARNING,
            message="System resource monitoring not available (psutil not installed)",
            response_time=time.time() - start_time
        )

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

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
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
            },
            response_time=time.time() - start_time
        )

    except Exception as e:
        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.WARNING,
            message=f"Could not check system resources: {str(e)}",
            response_time=time.time() - start_time
        )


def check_application_metrics() -> HealthCheckResult:
    """Check application performance metrics"""
    start_time = time.time()

    try:
        global_stats = metrics_collector.get_global_stats()

        # Check for concerning metrics
        status = HealthStatus.HEALTHY
        issues = []

        error_rate = global_stats["error_rate"]
        avg_response_time = global_stats["avg_duration_ms"]

        if error_rate > 10:
            status = HealthStatus.CRITICAL
            issues.append(f"High error rate: {error_rate}%")
        elif error_rate > 5:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"Elevated error rate: {error_rate}%")

        if avg_response_time > 2000:  # 2 seconds
            status = HealthStatus.CRITICAL
            issues.append(f"High average response time: {avg_response_time}ms")
        elif avg_response_time > 1000:  # 1 second
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"Elevated response time: {avg_response_time}ms")

        message = "Application metrics OK" if not issues else "; ".join(issues)

        return HealthCheckResult(
            name="application_metrics",
            status=status,
            message=message,
            details={
                "total_requests": global_stats["total_requests"],
                "error_rate_percent": global_stats["error_rate"],
                "avg_response_time_ms": global_stats["avg_duration_ms"],
                "uptime_seconds": global_stats["uptime_seconds"],
                "endpoints_tracked": global_stats["endpoints_tracked"]
            },
            response_time=time.time() - start_time
        )

    except Exception as e:
        return HealthCheckResult(
            name="application_metrics",
            status=HealthStatus.WARNING,
            message=f"Could not check application metrics: {str(e)}",
            response_time=time.time() - start_time
        )


# Global health checker instance
health_checker = HealthChecker()

# Register all health checks
health_checker.add_check(check_database)
health_checker.add_check(check_brou_api)
health_checker.add_check(check_bcu_api)
health_checker.add_check(check_system_resources)
health_checker.add_check(check_application_metrics)


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
        "status": "OK" if is_healthy else "FAIL",
        "timestamp": results["timestamp"],
        "checks": results["total_checks"],
        "issues": results["critical_checks"] + results["warning_checks"]
    }
