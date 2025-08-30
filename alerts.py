"""
Alert system for SIFU application
Provides comprehensive alerting for metrics, security, and system health
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from metrics import metrics_collector


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    condition: Callable[[], bool]
    severity: AlertSeverity
    cooldown_minutes: int = 5
    enabled: bool = True
    tags: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """Central alert management system"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._alerts: Dict[str, Alert] = {}
        self._rules: List[AlertRule] = []
        self._last_check: Dict[str, datetime] = {}
        self._alert_counter = 0

        # Initialize default alert rules
        self._setup_default_rules()

        # Start background monitoring
        self._monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitoring_thread.start()

    def _setup_default_rules(self):
        """Setup default alert rules"""

        # Performance alerts
        self.add_rule(AlertRule(
            name="high_error_rate",
            description="Error rate above 20%",
            condition=self._check_high_error_rate,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=10,
            tags={"category": "performance", "metric": "error_rate"}
        ))

        self.add_rule(AlertRule(
            name="critical_error_rate",
            description="Error rate above 50%",
            condition=self._check_critical_error_rate,
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=5,
            tags={"category": "performance", "metric": "error_rate"}
        ))

        self.add_rule(AlertRule(
            name="high_latency",
            description="Average response time above 500ms",
            condition=self._check_high_latency,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=15,
            tags={"category": "performance", "metric": "latency"}
        ))

        self.add_rule(AlertRule(
            name="no_recent_requests",
            description="No requests in the last 5 minutes",
            condition=self._check_no_recent_requests,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=5,
            tags={"category": "availability", "metric": "requests"}
        ))

        # System alerts
        self.add_rule(AlertRule(
            name="endpoint_high_error_rate",
            description="Specific endpoint has error rate above 30%",
            condition=self._check_endpoint_high_error_rate,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=10,
            tags={"category": "performance", "metric": "endpoint_error_rate"}
        ))

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        with self._lock:
            self._rules.append(rule)
            self.logger.info(f"Added alert rule: {rule.name}")

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self._alert_counter += 1
        return f"alert_{self._alert_counter}_{int(time.time())}"

    def _create_alert(self, rule: AlertRule, additional_info: str = "") -> Alert:
        """Create a new alert from a rule"""
        alert_id = self._generate_alert_id()
        now = datetime.utcnow()

        description = rule.description
        if additional_info:
            description += f" - {additional_info}"

        alert = Alert(
            id=alert_id,
            title=f"🚨 {rule.name.replace('_', ' ').title()}",
            description=description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            source=rule.name,
            created_at=now,
            updated_at=now,
            tags=rule.tags.copy()
        )

        with self._lock:
            self._alerts[alert_id] = alert
            self._last_check[rule.name] = now

        self.logger.warning(f"Alert created: {alert.title} (Severity: {alert.severity.value})")
        return alert

    def _resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        with self._lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                alert.updated_at = alert.resolved_at
                self.logger.info(f"Alert resolved: {alert.title}")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                self._check_all_rules()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in alert monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _check_all_rules(self):
        """Check all alert rules"""
        for rule in self._rules:
            if not rule.enabled:
                continue

            # Check cooldown
            last_check = self._last_check.get(rule.name)
            if last_check and (datetime.utcnow() - last_check).seconds < (rule.cooldown_minutes * 60):
                continue

            try:
                if rule.condition():
                    # Check if alert already exists
                    existing_alert = self._find_active_alert(rule.name)
                    if not existing_alert:
                        self._create_alert(rule)
            except Exception as e:
                self.logger.error(f"Error checking rule {rule.name}: {e}")

    def _find_active_alert(self, source: str) -> Optional[Alert]:
        """Find active alert by source"""
        with self._lock:
            for alert in self._alerts.values():
                if alert.source == source and alert.status == AlertStatus.ACTIVE:
                    return alert
        return None

    # Alert condition checkers
    def _check_high_error_rate(self) -> bool:
        """Check if global error rate is above 20%"""
        stats = metrics_collector.get_global_stats()
        return stats["error_rate"] > 20

    def _check_critical_error_rate(self) -> bool:
        """Check if global error rate is above 50%"""
        stats = metrics_collector.get_global_stats()
        return stats["error_rate"] > 50

    def _check_high_latency(self) -> bool:
        """Check if average response time is above 500ms"""
        stats = metrics_collector.get_global_stats()
        return stats["avg_duration_ms"] > 500

    def _check_no_recent_requests(self) -> bool:
        """Check if there have been no requests in the last 5 minutes"""
        recent_requests = metrics_collector.get_recent_requests(10)
        if not recent_requests:
            return True

        latest_request = max(req.timestamp for req in recent_requests)
        return (datetime.utcnow() - latest_request).seconds > 300  # 5 minutes

    def _check_endpoint_high_error_rate(self) -> bool:
        """Check if any endpoint has error rate above 30%"""
        endpoint_stats = metrics_collector.get_endpoint_stats()
        for endpoint, stats in endpoint_stats.items():
            if stats["error_rate"] > 30:
                return True
        return False

    # Public API
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        with self._lock:
            return [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "source": alert.source,
                    "created_at": alert.created_at.isoformat(),
                    "updated_at": alert.updated_at.isoformat(),
                    "tags": alert.tags,
                    "metadata": alert.metadata
                }
                for alert in self._alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]

    def get_all_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all alerts (active and resolved)"""
        with self._lock:
            alerts = list(self._alerts.values())
            alerts.sort(key=lambda x: x.created_at, reverse=True)

            return [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "source": alert.source,
                    "created_at": alert.created_at.isoformat(),
                    "updated_at": alert.updated_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "tags": alert.tags,
                    "metadata": alert.metadata
                }
                for alert in alerts[:limit]
            ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        with self._lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.utcnow()
                alert.updated_at = alert.acknowledged_at
                self.logger.info(f"Alert acknowledged: {alert.title}")
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert"""
        with self._lock:
            if alert_id in self._alerts:
                self._resolve_alert(alert_id)
                return True
        return False

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        with self._lock:
            active_alerts = [a for a in self._alerts.values() if a.status == AlertStatus.ACTIVE]
            critical_count = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
            high_count = len([a for a in active_alerts if a.severity == AlertSeverity.HIGH])
            medium_count = len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM])
            low_count = len([a for a in active_alerts if a.severity == AlertSeverity.LOW])

            return {
                "total_active": len(active_alerts),
                "by_severity": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count
                },
                "total_resolved": len([a for a in self._alerts.values() if a.status == AlertStatus.RESOLVED]),
                "rules_active": len([r for r in self._rules if r.enabled])
            }


# Global alert manager instance
alert_manager = AlertManager()
