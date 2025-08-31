"""
Dashboard module for SIFU application
Provides comprehensive dashboard data combining metrics and alerts
"""
from datetime import datetime
from typing import Dict, List, Any
import logging

from metrics import metrics_collector
from alerts import alert_manager


class DashboardService:
    """Service for dashboard data aggregation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get current metrics
            global_stats = metrics_collector.get_global_stats()
            endpoint_stats = metrics_collector.get_endpoint_stats()
            recent_requests = metrics_collector.get_recent_requests(20)
            health_status = metrics_collector.get_health_status()

            # Get alerts
            active_alerts = alert_manager.get_active_alerts()
            alert_summary = alert_manager.get_alert_summary()

            # Calculate additional dashboard metrics
            dashboard_metrics = self._calculate_dashboard_metrics(
                global_stats, endpoint_stats, recent_requests
            )

            # Get system status
            system_status = self._get_system_status(health_status, active_alerts)

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_status": system_status,
                "metrics": dashboard_metrics,
                "alerts": {
                    "active": active_alerts,
                    "summary": alert_summary
                },
                "performance": {
                    "global": global_stats,
                    "endpoints": endpoint_stats,
                    "recent_requests": [
                        {
                            "method": req.method,
                            "endpoint": req.endpoint,
                            "status_code": req.status_code,
                            "duration_ms": round(req.duration * 1000, 2),
                            "timestamp": req.timestamp.isoformat(),
                            "error": req.error
                        }
                        for req in recent_requests
                    ]
                },
                "health": health_status
            }

        except Exception as e:
            self.logger.error(f"Error generating dashboard data: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": f"Failed to generate dashboard: {str(e)}",
                "system_status": "error"
            }

    def _calculate_dashboard_metrics(self, global_stats: Dict, endpoint_stats: Dict,
                                   recent_requests: List) -> Dict[str, Any]:
        """Calculate additional dashboard-specific metrics"""

        # Request rate (requests per minute)
        uptime_minutes = global_stats["uptime_seconds"] / 60
        request_rate = global_stats["total_requests"] / uptime_minutes if uptime_minutes > 0 else 0

        # Error trend (last 10 requests)
        recent_errors = len([r for r in recent_requests if r.error or r.status_code >= 400])
        recent_error_rate = (recent_errors / len(recent_requests) * 100) if recent_requests else 0

        # Endpoint performance summary
        endpoint_summary = []
        for endpoint, stats in endpoint_stats.items():
            endpoint_summary.append({
                "endpoint": endpoint,
                "requests": stats["total_requests"],
                "error_rate": stats["error_rate"],
                "avg_duration": stats["avg_duration_ms"],
                "status": "healthy" if stats["error_rate"] < 10 else "warning" if stats["error_rate"] < 30 else "critical"
            })

        # Sort by request count
        endpoint_summary.sort(key=lambda x: x["requests"], reverse=True)

        # Performance score (0-100)
        performance_score = self._calculate_performance_score(global_stats, recent_error_rate)

        return {
            "request_rate_per_minute": round(request_rate, 2),
            "recent_error_rate": round(recent_error_rate, 2),
            "performance_score": performance_score,
            "endpoint_summary": endpoint_summary[:10],  # Top 10 endpoints
            "total_endpoints": len(endpoint_stats)
        }

    def _calculate_performance_score(self, global_stats: Dict, recent_error_rate: float) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100

        # Error rate penalties
        if recent_error_rate > 50:
            score -= 50
        elif recent_error_rate > 20:
            score -= 25
        elif recent_error_rate > 10:
            score -= 10

        # Latency penalties
        avg_latency = global_stats["avg_duration_ms"]
        if avg_latency > 2000:
            score -= 30
        elif avg_latency > 1000:
            score -= 20
        elif avg_latency > 500:
            score -= 10

        # Request rate bonus
        request_rate = global_stats["total_requests"] / max(global_stats["uptime_seconds"] / 60, 1)
        if request_rate > 10:
            score += 5
        elif request_rate > 1:
            score += 2

        return max(0, min(100, score))

    def _get_system_status(self, health_status: Dict, active_alerts: List) -> str:
        """Determine overall system status"""

        # Check for critical alerts
        critical_alerts = [a for a in active_alerts if a["severity"] == "critical"]
        if critical_alerts:
            return "critical"

        # Check health status
        if health_status["status"] == "critical":
            return "critical"
        elif health_status["status"] == "warning":
            return "warning"

        # Check for high severity alerts
        high_alerts = [a for a in active_alerts if a["severity"] == "high"]
        if high_alerts:
            return "warning"

        # Default to healthy
        return "healthy"

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get simplified dashboard summary for quick status"""
        try:
            global_stats = metrics_collector.get_global_stats()
            active_alerts = alert_manager.get_active_alerts()
            health_status = metrics_collector.get_health_status()

            system_status = self._get_system_status(health_status, active_alerts)

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": system_status,
                "uptime": global_stats["uptime_human"],
                "total_requests": global_stats["total_requests"],
                "error_rate": f"{global_stats['error_rate']}%",
                "avg_response_time": f"{global_stats['avg_duration_ms']}ms",
                "active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a["severity"] == "critical"]),
                "endpoints_tracked": global_stats["endpoints_tracked"]
            }

        except Exception as e:
            self.logger.error(f"Error generating dashboard summary: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }


# Global dashboard service instance
dashboard_service = DashboardService()
