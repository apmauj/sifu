"""
Performance Budgets and Monitoring for SIFU Application
Implements PERF-004: Performance budgets and alerts
"""
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Lazy imports to avoid circular dependencies
_metrics_collector = None
_alert_manager = None
_AlertSeverity = None
_AlertRule = None

def _get_metrics_collector():
    """Lazy import of metrics collector with timeout"""
    global _metrics_collector
    if _metrics_collector is None:
        try:
            # Use threading to add timeout for import
            import threading
            result = [None]
            exception = [None]
            
            def import_metrics():
                try:
                    from metrics import metrics_collector as mc
                    result[0] = mc
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=import_metrics)
            thread.daemon = True
            thread.start()
            thread.join(timeout=5.0)  # 5 second timeout
            
            if thread.is_alive():
                # Import is taking too long, consider it failed
                _metrics_collector = None
            elif exception[0]:
                # Import failed with exception
                _metrics_collector = None
            else:
                # Import successful
                _metrics_collector = result[0]
                
        except Exception:
            # Any other issue, consider metrics unavailable
            _metrics_collector = None
    return _metrics_collector

def _get_alert_manager():
    """Lazy import of alert manager"""
    global _alert_manager, _AlertSeverity, _AlertRule
    if _alert_manager is None:
        from alerts import alert_manager as am, AlertSeverity as AS, AlertRule as AR
        _alert_manager = am
        _AlertSeverity = AS
        _AlertRule = AR
    return _alert_manager


class BudgetType(Enum):
    """Types of performance budgets"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"


@dataclass
class PerformanceBudget:
    """Performance budget configuration"""
    name: str
    budget_type: BudgetType
    target_value: float
    warning_threshold: float
    critical_threshold: float
    window_minutes: int = 5
    description: str = ""
    enabled: bool = True

    @property
    def warning_value(self) -> float:
        """Calculate warning threshold value"""
        if self.budget_type == BudgetType.LATENCY:
            return self.target_value * (1 + self.warning_threshold / 100)
        elif self.budget_type == BudgetType.ERROR_RATE:
            return self.warning_threshold
        elif self.budget_type == BudgetType.AVAILABILITY:
            return 100 - self.warning_threshold
        return self.target_value * (1 - self.warning_threshold / 100)

    @property
    def critical_value(self) -> float:
        """Calculate critical threshold value"""
        if self.budget_type == BudgetType.LATENCY:
            return self.target_value * (1 + self.critical_threshold / 100)
        elif self.budget_type == BudgetType.ERROR_RATE:
            return self.critical_threshold
        elif self.budget_type == BudgetType.AVAILABILITY:
            return 100 - self.critical_threshold
        return self.target_value * (1 - self.critical_threshold / 100)


@dataclass
class ThroughputMetrics:
    """Throughput tracking data"""
    requests_per_minute: float = 0.0
    requests_per_hour: float = 0.0
    peak_rpm: float = 0.0
    window_start: datetime = field(default_factory=datetime.utcnow)
    request_count: int = 0


class PerformanceBudgetManager:
    """Manages performance budgets and monitoring"""

    def __init__(self, enable_monitoring=True, enable_alerts=True):
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._budgets: Dict[str, PerformanceBudget] = {}
        self._throughput_data: Dict[str, ThroughputMetrics] = {}
        self._last_check: Dict[str, datetime] = {}

        # Initialize default performance budgets
        self._setup_default_budgets()

        # Start background monitoring (optional for testing)
        if enable_monitoring:
            self._monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitoring_thread.start()

        # Setup alert rules for budgets (optional for testing)
        if enable_alerts:
            self._setup_budget_alert_rules()

    def _setup_default_budgets(self):
        """Setup default performance budgets based on roadmap targets"""

        # Latency budget: Target < 200ms
        self.add_budget(PerformanceBudget(
            name="api_latency_budget",
            budget_type=BudgetType.LATENCY,
            target_value=200.0,  # 200ms target
            warning_threshold=50.0,  # 50% over target = 300ms warning
            critical_threshold=100.0,  # 100% over target = 400ms critical
            window_minutes=5,
            description="API response time budget - Target: <200ms"
        ))

        # Throughput budget: Target > 1000 req/min
        self.add_budget(PerformanceBudget(
            name="throughput_budget",
            budget_type=BudgetType.THROUGHPUT,
            target_value=1000.0,  # 1000 req/min target
            warning_threshold=20.0,  # 20% below target = 800 req/min warning
            critical_threshold=50.0,  # 50% below target = 500 req/min critical
            window_minutes=5,
            description="Request throughput budget - Target: >1000 req/min"
        ))

        # Error rate budget: Target < 5%
        self.add_budget(PerformanceBudget(
            name="error_rate_budget",
            budget_type=BudgetType.ERROR_RATE,
            target_value=5.0,  # 5% target
            warning_threshold=10.0,  # 10% warning
            critical_threshold=20.0,  # 20% critical
            window_minutes=5,
            description="Error rate budget - Target: <5%"
        ))

        # Availability budget: Target > 99.5%
        self.add_budget(PerformanceBudget(
            name="availability_budget",
            budget_type=BudgetType.AVAILABILITY,
            target_value=99.5,  # 99.5% uptime target
            warning_threshold=0.5,  # 99% availability warning
            critical_threshold=1.0,  # 98.5% availability critical
            window_minutes=60,  # Check over 1 hour window
            description="Service availability budget - Target: >99.5%"
        ))

    def _setup_budget_alert_rules(self):
        """Setup alert rules for performance budgets"""
        alert_manager = _get_alert_manager()
        AlertRule = _AlertRule
        AlertSeverity = _AlertSeverity

        # Latency budget alerts
        alert_manager.add_rule(AlertRule(
            name="latency_budget_warning",
            description="API latency exceeding warning threshold",
            condition=self._check_latency_budget_warning,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=10,
            tags={"category": "performance", "budget": "latency", "level": "warning"}
        ))

        alert_manager.add_rule(AlertRule(
            name="latency_budget_critical",
            description="API latency exceeding critical threshold",
            condition=self._check_latency_budget_critical,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=5,
            tags={"category": "performance", "budget": "latency", "level": "critical"}
        ))

        # Throughput budget alerts
        alert_manager.add_rule(AlertRule(
            name="throughput_budget_warning",
            description="Request throughput below warning threshold",
            condition=self._check_throughput_budget_warning,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=10,
            tags={"category": "performance", "budget": "throughput", "level": "warning"}
        ))

        alert_manager.add_rule(AlertRule(
            name="throughput_budget_critical",
            description="Request throughput below critical threshold",
            condition=self._check_throughput_budget_critical,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=5,
            tags={"category": "performance", "budget": "throughput", "level": "critical"}
        ))

        # Error rate budget alerts
        alert_manager.add_rule(AlertRule(
            name="error_rate_budget_warning",
            description="Error rate exceeding warning threshold",
            condition=self._check_error_rate_budget_warning,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=10,
            tags={"category": "performance", "budget": "error_rate", "level": "warning"}
        ))

        alert_manager.add_rule(AlertRule(
            name="error_rate_budget_critical",
            description="Error rate exceeding critical threshold",
            condition=self._check_error_rate_budget_critical,
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=5,
            tags={"category": "performance", "budget": "error_rate", "level": "critical"}
        ))

    def add_budget(self, budget: PerformanceBudget):
        """Add a performance budget"""
        with self._lock:
            self._budgets[budget.name] = budget
            self.logger.info(f"Added performance budget: {budget.name}")

    def get_budget(self, name: str) -> Optional[PerformanceBudget]:
        """Get a performance budget by name"""
        with self._lock:
            return self._budgets.get(name)

    def get_all_budgets(self) -> Dict[str, Dict[str, Any]]:
        """Get all performance budgets"""
        with self._lock:
            result = {}
            for name, budget in self._budgets.items():
                result[name] = {
                    "name": budget.name,
                    "type": budget.budget_type.value,
                    "target_value": budget.target_value,
                    "warning_threshold": budget.warning_threshold,
                    "critical_threshold": budget.critical_threshold,
                    "warning_value": budget.warning_value,
                    "critical_value": budget.critical_value,
                    "window_minutes": budget.window_minutes,
                    "description": budget.description,
                    "enabled": budget.enabled
                }
            return result

    def update_throughput(self, endpoint: str = "global"):
        """Update throughput metrics for an endpoint"""
        with self._lock:
            now = datetime.utcnow()
            metrics = self._throughput_data.get(endpoint, ThroughputMetrics())

            # Reset window if needed
            if (now - metrics.window_start).seconds >= 60:  # 1 minute window
                metrics.window_start = now
                metrics.request_count = 0

            metrics.request_count += 1

            # Calculate rates
            window_seconds = (now - metrics.window_start).seconds
            if window_seconds > 0:
                metrics.requests_per_minute = metrics.request_count / (window_seconds / 60)
                metrics.requests_per_hour = metrics.requests_per_minute * 60

                if metrics.requests_per_minute > metrics.peak_rpm:
                    metrics.peak_rpm = metrics.requests_per_minute

            self._throughput_data[endpoint] = metrics

    def get_throughput_metrics(self, endpoint: str = "global") -> Dict[str, Any]:
        """Get throughput metrics for an endpoint"""
        with self._lock:
            metrics = self._throughput_data.get(endpoint, ThroughputMetrics())
            return {
                "requests_per_minute": round(metrics.requests_per_minute, 2),
                "requests_per_hour": round(metrics.requests_per_hour, 2),
                "peak_rpm": round(metrics.peak_rpm, 2),
                "current_window_requests": metrics.request_count,
                "window_start": metrics.window_start.isoformat()
            }

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current status of all budgets"""
        with self._lock:
            status = {}
            try:
                metrics_collector = _get_metrics_collector()
                
                # Use default values if metrics collector is not available
                if metrics_collector:
                    global_stats = metrics_collector.get_global_stats()
                    global_throughput = self.get_throughput_metrics("global")
                else:
                    # Fallback values when metrics are not available
                    global_stats = {
                        "avg_duration_ms": 0,
                        "error_rate": 0,
                        "uptime_seconds": 0
                    }
                    global_throughput = {"requests_per_minute": 0}
            except Exception as e:
                # If there's any issue with metrics collection, use fallback values
                self.logger.warning(f"Error getting metrics collector: {e}")
                global_stats = {
                    "avg_duration_ms": 0,
                    "error_rate": 0,
                    "uptime_seconds": 0
                }
                global_throughput = {"requests_per_minute": 0}

            for name, budget in self._budgets.items():
                if not budget.enabled:
                    continue

                current_value = self._get_current_budget_value(budget, global_stats, global_throughput)
                status[name] = {
                    "budget": budget.name,
                    "type": budget.budget_type.value,
                    "target": budget.target_value,
                    "current": current_value,
                    "warning_threshold": budget.warning_value,
                    "critical_threshold": budget.critical_value,
                    "status": self._calculate_budget_status(budget, current_value),
                    "description": budget.description
                }

            return status

    def _get_current_budget_value(self, budget: PerformanceBudget, global_stats: Dict[str, Any],
                                throughput: Dict[str, Any]) -> float:
        """Get current value for a budget"""
        if budget.budget_type == BudgetType.LATENCY:
            return global_stats.get("avg_duration_ms", 0)
        elif budget.budget_type == BudgetType.THROUGHPUT:
            return throughput.get("requests_per_minute", 0)
        elif budget.budget_type == BudgetType.ERROR_RATE:
            return global_stats.get("error_rate", 0)
        elif budget.budget_type == BudgetType.AVAILABILITY:
            # Calculate availability based on uptime and error rate
            uptime_seconds = global_stats.get("uptime_seconds", 0)
            if uptime_seconds > 0:
                # Simplified availability calculation
                error_rate = global_stats.get("error_rate", 0)
                return 100 - error_rate
            return 100.0
        return 0.0

    def _calculate_budget_status(self, budget: PerformanceBudget, current_value: float) -> str:
        """Calculate budget status"""
        if budget.budget_type in [BudgetType.LATENCY, BudgetType.ERROR_RATE]:
            # Higher values are worse
            if current_value >= budget.critical_value:
                return "critical"
            elif current_value >= budget.warning_value:
                return "warning"
            else:
                return "healthy"
        else:
            # Lower values are worse (throughput, availability)
            if current_value <= budget.critical_value:
                return "critical"
            elif current_value <= budget.warning_value:
                return "warning"
            else:
                return "healthy"

    def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                self._check_budgets()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in performance budget monitoring: {e}")
                time.sleep(120)  # Wait longer on error

    def _check_budgets(self):
        """Check all budgets and update status"""
        # This is mainly for logging and potential future enhancements
        # Alert rules are handled separately by the alert manager
        status = self.get_budget_status()

        for budget_name, budget_status in status.items():
            if budget_status["status"] != "healthy":
                self.logger.warning(
                    f"Performance budget violation: {budget_name} - "
                    f"Current: {budget_status['current']:.2f}, "
                    f"Target: {budget_status['target']:.2f}, "
                    f"Status: {budget_status['status']}"
                )

    # Alert condition checkers
    def _check_latency_budget_warning(self) -> bool:
        """Check if latency exceeds warning threshold"""
        budget = self._budgets.get("api_latency_budget")
        if not budget or not budget.enabled:
            return False

        metrics_collector = _get_metrics_collector()
        if not metrics_collector:
            return False
            
        global_stats = metrics_collector.get_global_stats()
        current_latency = global_stats.get("avg_duration_ms", 0)
        return current_latency >= budget.warning_value

    def _check_latency_budget_critical(self) -> bool:
        """Check if latency exceeds critical threshold"""
        budget = self._budgets.get("api_latency_budget")
        if not budget or not budget.enabled:
            return False

        metrics_collector = _get_metrics_collector()
        if not metrics_collector:
            return False
            
        global_stats = metrics_collector.get_global_stats()
        current_latency = global_stats.get("avg_duration_ms", 0)
        return current_latency >= budget.critical_value

    def _check_throughput_budget_warning(self) -> bool:
        """Check if throughput is below warning threshold"""
        budget = self._budgets.get("throughput_budget")
        if not budget or not budget.enabled:
            return False

        throughput = self.get_throughput_metrics("global")
        current_throughput = throughput.get("requests_per_minute", 0)
        return current_throughput <= budget.warning_value

    def _check_throughput_budget_critical(self) -> bool:
        """Check if throughput is below critical threshold"""
        budget = self._budgets.get("throughput_budget")
        if not budget or not budget.enabled:
            return False

        throughput = self.get_throughput_metrics("global")
        current_throughput = throughput.get("requests_per_minute", 0)
        return current_throughput <= budget.critical_value

    def _check_error_rate_budget_warning(self) -> bool:
        """Check if error rate exceeds warning threshold"""
        budget = self._budgets.get("error_rate_budget")
        if not budget or not budget.enabled:
            return False

        metrics_collector = _get_metrics_collector()
        if not metrics_collector:
            return False
            
        global_stats = metrics_collector.get_global_stats()
        current_error_rate = global_stats.get("error_rate", 0)
        return current_error_rate >= budget.warning_value

    def _check_error_rate_budget_critical(self) -> bool:
        """Check if error rate exceeds critical threshold"""
        budget = self._budgets.get("error_rate_budget")
        if not budget or not budget.enabled:
            return False

        metrics_collector = _get_metrics_collector()
        if not metrics_collector:
            return False
            
        global_stats = metrics_collector.get_global_stats()
        current_error_rate = global_stats.get("error_rate", 0)
        return current_error_rate >= budget.critical_value


# Global performance budget manager instance - lazy initialization
_performance_budget_manager_instance = None

def get_performance_budget_manager(enable_monitoring=False, enable_alerts=False):
    """Get the global performance budget manager instance (lazy initialization)"""
    global _performance_budget_manager_instance
    if _performance_budget_manager_instance is None:
        _performance_budget_manager_instance = PerformanceBudgetManager(
            enable_monitoring=enable_monitoring,
            enable_alerts=enable_alerts
        )
    return _performance_budget_manager_instance

# For backward compatibility, provide the instance
performance_budget_manager = None
