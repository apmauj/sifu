"""
Metrics middleware for FastAPI application
Automatically captures request metrics: latency, status codes, errors
"""

import time
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from metrics import metrics_collector


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record start time
        start_time = time.time()

        # Initialize error tracking
        error_occurred = False
        error_message = ""

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            metrics_collector.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
                error=error_occurred,
                error_message=error_message,
            )

            # Increment lightweight throughput counter for performance dashboard (best-effort)
            try:
                from performance_budget import (
                    get_performance_budget_manager,
                )  # lazy import to avoid cycles

                bm = get_performance_budget_manager(
                    enable_monitoring=False, enable_alerts=False
                )
                bm.update_throughput("global")
            except Exception:
                # Non-fatal; avoid impacting request path
                pass

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            error_occurred = True
            error_message = str(e)

            # Record failed request metrics
            metrics_collector.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,  # Internal server error
                duration=duration,
                error=True,
                error_message=error_message,
            )

            # Still count towards throughput to reflect incoming load
            try:
                from performance_budget import (
                    get_performance_budget_manager,
                )  # lazy import to avoid cycles

                bm = get_performance_budget_manager(
                    enable_monitoring=False, enable_alerts=False
                )
                bm.update_throughput("global")
            except Exception:
                pass

            # Re-raise the exception to maintain normal error handling
            raise


# Metrics endpoints
def _get_cache_age_metrics():
    """Get cache age metrics for BROU and BCU caches"""
    cache_metrics = {}
    
    try:
        from main import brou_cache, bcu_cache, _cache_lock
        
        # BROU Cache Age
        with _cache_lock:
            brou_cached = brou_cache
        
        if brou_cached and brou_cached.get("updated_at"):
            brou_age = (datetime.utcnow() - brou_cached["updated_at"]).total_seconds()
            cache_metrics["brou_cache_age_seconds"] = round(brou_age, 1)
            cache_metrics["brou_cache_age_minutes"] = round(brou_age / 60, 1)
            cache_metrics["brou_cache_status"] = "available"
        else:
            cache_metrics["brou_cache_age_seconds"] = None
            cache_metrics["brou_cache_age_minutes"] = None
            cache_metrics["brou_cache_status"] = "empty" if brou_cached is None else "no_timestamp"
        
        # BCU Cache Age
        with _cache_lock:
            bcu_cached = bcu_cache
        
        if bcu_cached and bcu_cached.get("updated_at"):
            bcu_age = (datetime.utcnow() - bcu_cached["updated_at"]).total_seconds()
            cache_metrics["bcu_cache_age_seconds"] = round(bcu_age, 1)
            cache_metrics["bcu_cache_age_minutes"] = round(bcu_age / 60, 1)
            cache_metrics["bcu_cache_status"] = "available"
        else:
            cache_metrics["bcu_cache_age_seconds"] = None
            cache_metrics["bcu_cache_age_minutes"] = None
            cache_metrics["bcu_cache_status"] = "empty" if bcu_cached is None else "no_timestamp"
            
    except Exception as e:
        cache_metrics["cache_metrics_error"] = str(e)
        cache_metrics["brou_cache_age_seconds"] = None
        cache_metrics["bcu_cache_age_seconds"] = None
        cache_metrics["brou_cache_status"] = "error"
        cache_metrics["bcu_cache_status"] = "error"
    
    return cache_metrics


async def get_metrics():
    """Get comprehensive metrics data"""
    base = {
        "global_stats": metrics_collector.get_global_stats(),
        "endpoint_stats": metrics_collector.get_endpoint_stats(),
        "recent_requests": [
            {
                "method": req.method,
                "endpoint": req.endpoint,
                "status_code": req.status_code,
                "duration_ms": round(req.duration * 1000, 2),
                "timestamp": req.timestamp.isoformat(),
                "error": req.error,
                "error_message": req.error_message if req.error else None,
            }
            for req in metrics_collector.get_recent_requests(50)
        ],
    }

    # UI freshness metrics (roadmap task) - lightweight query
    try:
        from database import SessionLocal
        from services import UIService
        from datetime import datetime
        import os
        import pytz  # type: ignore

        session = SessionLocal()
        try:
            ui_service = UIService(session)
            latest = ui_service.get_latest_ui()
        finally:
            session.close()

        if latest:
            tz_name = os.getenv("SCHEDULER_TIMEZONE", "UTC")
            try:
                tz = pytz.timezone(tz_name)
            except Exception:
                tz = pytz.UTC
            now_local = datetime.now(tz)
            dias_gap_raw = (now_local.date() - latest.date).days
            if dias_gap_raw < 0:  # futuro
                dias_ahead = -dias_gap_raw
                base["ui_freshness"] = {
                    "ui_latest_date": latest.date.isoformat(),
                    "ui_dias_gap": 0,
                    "ui_latest_age_seconds": 0,
                    "ui_gap_detected": False,
                    "future": True,
                    "ui_dias_ahead": dias_ahead,
                }
            else:
                base["ui_freshness"] = {
                    "ui_latest_date": latest.date.isoformat(),
                    "ui_dias_gap": dias_gap_raw,
                    "ui_latest_age_seconds": dias_gap_raw * 86400,
                    "ui_gap_detected": dias_gap_raw >= 2,
                    "future": False,
                }
        else:
            base["ui_freshness"] = {
                "ui_latest_date": None,
                "ui_dias_gap": None,
                "ui_latest_age_seconds": None,
                "ui_gap_detected": True,
                "error": "no_ui_records",
            }
    except Exception as e:  # noqa: BLE001
        base["ui_freshness"] = {"error": f"ui_metrics_failed: {e}"}

    # Cache age metrics (Punto 4: Métricas de Edad de Caché)
    try:
        cache_metrics = _get_cache_age_metrics()
        base["cache_metrics"] = cache_metrics
        
        # Add cache age warnings based on configurable thresholds
        cache_warnings = []
        try:
            from constants import CACHE_WARNING_THRESHOLD_MINUTES, CACHE_CRITICAL_THRESHOLD_MINUTES
            
            if cache_metrics.get("brou_cache_age_seconds") is not None:
                brou_age_minutes = cache_metrics["brou_cache_age_minutes"]
                if brou_age_minutes > CACHE_CRITICAL_THRESHOLD_MINUTES:
                    cache_warnings.append(f"BROU cache critical: {brou_age_minutes:.1f} minutes (threshold: {CACHE_CRITICAL_THRESHOLD_MINUTES})")
                elif brou_age_minutes > CACHE_WARNING_THRESHOLD_MINUTES:
                    cache_warnings.append(f"BROU cache stale: {brou_age_minutes:.1f} minutes (threshold: {CACHE_WARNING_THRESHOLD_MINUTES})")
            
            if cache_metrics.get("bcu_cache_age_seconds") is not None:
                bcu_age_minutes = cache_metrics["bcu_cache_age_minutes"]
                if bcu_age_minutes > CACHE_CRITICAL_THRESHOLD_MINUTES:
                    cache_warnings.append(f"BCU cache critical: {bcu_age_minutes:.1f} minutes (threshold: {CACHE_CRITICAL_THRESHOLD_MINUTES})")
                elif bcu_age_minutes > CACHE_WARNING_THRESHOLD_MINUTES:
                    cache_warnings.append(f"BCU cache stale: {bcu_age_minutes:.1f} minutes (threshold: {CACHE_WARNING_THRESHOLD_MINUTES})")
        except ImportError:
            # Fallback to hardcoded values if constants import fails
            if cache_metrics.get("brou_cache_age_seconds") is not None:
                brou_age_minutes = cache_metrics["brou_cache_age_minutes"]
                if brou_age_minutes > 120:  # 2 hours
                    cache_warnings.append(f"BROU cache critical: {brou_age_minutes:.1f} minutes")
                elif brou_age_minutes > 60:  # 1 hour
                    cache_warnings.append(f"BROU cache stale: {brou_age_minutes:.1f} minutes")
            
            if cache_metrics.get("bcu_cache_age_seconds") is not None:
                bcu_age_minutes = cache_metrics["bcu_cache_age_minutes"]
                if bcu_age_minutes > 120:  # 2 hours
                    cache_warnings.append(f"BCU cache critical: {bcu_age_minutes:.1f} minutes")
                elif bcu_age_minutes > 60:  # 1 hour
                    cache_warnings.append(f"BCU cache stale: {bcu_age_minutes:.1f} minutes")
        
        if cache_warnings:
            base["cache_warnings"] = cache_warnings
            
    except Exception as e:
        logger.warning(f"Cache metrics failed: {e}")
        base["cache_metrics"] = {"error": str(e)}

    return base


async def get_health():
    """Get health status with metrics"""
    return metrics_collector.get_health_status()


async def get_simple_metrics():
    """Get simplified metrics for monitoring systems"""
    global_stats = metrics_collector.get_global_stats()

    return {
        "uptime_seconds": global_stats["uptime_seconds"],
        "total_requests": global_stats["total_requests"],
        "error_rate_percent": global_stats["error_rate"],
        "avg_response_time_ms": global_stats["avg_duration_ms"],
        "endpoints_tracked": global_stats["endpoints_tracked"],
        "timestamp": datetime.utcnow().isoformat(),
    }
