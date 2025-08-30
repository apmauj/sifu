"""
Metrics collection module for SIFU application
Provides basic observability metrics: latency, error rates, request counts
"""
import time
from collections import defaultdict, deque
from typing import Dict, List, Any
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    method: str
    endpoint: str
    status_code: int
    duration: float
    timestamp: datetime
    error: bool = False
    error_message: str = ""


@dataclass
class EndpointStats:
    """Statistics for an endpoint"""
    total_requests: int = 0
    total_errors: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    last_request: datetime = None

    @property
    def avg_duration(self) -> float:
        """Average request duration"""
        if self.total_requests == 0:
            return 0.0
        return self.total_duration / self.total_requests

    @property
    def error_rate(self) -> float:
        """Error rate as percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100


class MetricsCollector:
    """Thread-safe metrics collector"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._lock = threading.Lock()
        self._recent_requests: deque[RequestMetrics] = deque(maxlen=max_history)
        self._endpoint_stats: Dict[str, EndpointStats] = defaultdict(EndpointStats)
        self._start_time = datetime.utcnow()

    def record_request(self, method: str, endpoint: str, status_code: int,
                      duration: float, error: bool = False, error_message: str = ""):
        """Record a request metric"""
        metric = RequestMetrics(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            timestamp=datetime.utcnow(),
            error=error,
            error_message=error_message
        )

        with self._lock:
            self._recent_requests.append(metric)

            # Update endpoint statistics
            key = f"{method} {endpoint}"
            stats = self._endpoint_stats[key]
            stats.total_requests += 1
            stats.total_duration += duration
            stats.last_request = metric.timestamp

            if error or status_code >= 400:
                stats.total_errors += 1

            if duration < stats.min_duration:
                stats.min_duration = duration
            if duration > stats.max_duration:
                stats.max_duration = duration

    def get_recent_requests(self, limit: int = 100) -> List[RequestMetrics]:
        """Get recent requests (most recent first)"""
        with self._lock:
            return list(self._recent_requests)[-limit:][::-1]

    def get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all endpoints"""
        with self._lock:
            result = {}
            for endpoint, stats in self._endpoint_stats.items():
                result[endpoint] = {
                    "total_requests": stats.total_requests,
                    "total_errors": stats.total_errors,
                    "error_rate": round(stats.error_rate, 2),
                    "avg_duration_ms": round(stats.avg_duration * 1000, 2),
                    "min_duration_ms": round(stats.min_duration * 1000, 2) if stats.min_duration != float('inf') else 0,
                    "max_duration_ms": round(stats.max_duration * 1000, 2),
                    "last_request": stats.last_request.isoformat() if stats.last_request else None
                }
            return result

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global application statistics"""
        with self._lock:
            total_requests = sum(stats.total_requests for stats in self._endpoint_stats.values())
            total_errors = sum(stats.total_errors for stats in self._endpoint_stats.values())
            total_duration = sum(stats.total_duration for stats in self._endpoint_stats.values())

            uptime = datetime.utcnow() - self._start_time

            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": round((total_errors / total_requests * 100) if total_requests > 0 else 0, 2),
                "avg_duration_ms": round((total_duration / total_requests * 1000) if total_requests > 0 else 0, 2),
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_human": str(uptime).split('.')[0],  # HH:MM:SS format
                "endpoints_tracked": len(self._endpoint_stats),
                "recent_requests_count": len(self._recent_requests)
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status based on metrics"""
        global_stats = self.get_global_stats()

        # Determine health based on error rate and recent activity
        error_rate = global_stats["error_rate"]
        recent_requests = len(self.get_recent_requests(10))  # Last 10 requests

        if error_rate > 50:
            health = "critical"
            status_message = f"High error rate: {error_rate}%"
        elif error_rate > 20:
            health = "warning"
            status_message = f"Elevated error rate: {error_rate}%"
        elif recent_requests == 0:
            health = "warning"
            status_message = "No recent requests"
        else:
            health = "healthy"
            status_message = "System operating normally"

        return {
            "status": health,
            "message": status_message,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": global_stats
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()
