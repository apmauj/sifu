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
