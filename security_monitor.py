#!/usr/bin/env python3
"""
Security Log Monitor for SIFU
Monitors security logs in real-time and alerts on suspicious activity
"""
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

class SecurityLogMonitor:
    """Monitors security logs for suspicious activity"""

    def __init__(self, log_file: str = 'sifu.log', security_log_file: str = 'security_audit.log'):
        self.log_file = Path(log_file)
        self.security_log_file = Path(security_log_file)
        self.logger = logging.getLogger(__name__)

        # Security patterns to monitor
        self.security_patterns = {
            'failed_login': re.compile(r'Authentication FAILURE'),
            'suspicious_ip': re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'),
            'sql_injection': re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s+.*(--|#|/\*|\*/)', re.IGNORECASE),
            'xss_attempt': re.compile(r'<script|<iframe|<object|<embed', re.IGNORECASE),
            'path_traversal': re.compile(r'\.\./|\.\.\\'),
            'rate_limit_hit': re.compile(r'Rate limit exceeded'),
            'config_error': re.compile(r'Configuration.*error|Secret.*missing', re.IGNORECASE),
        }

        # Alert thresholds
        self.alert_thresholds = {
            'failed_login': 5,  # 5 failed logins per minute
            'suspicious_activity': 10,  # 10 suspicious activities per minute
        }

        # Tracking
        self.last_positions = {self.log_file: 0, self.security_log_file: 0}
        self.alert_counts = {}
        self.last_alert_time = datetime.now()

    def monitor_logs(self):
        """Monitor log files for security events"""
        print("🔍 Starting security log monitoring...")
        print("📊 Monitoring files:", self.log_file, self.security_log_file)
        print("⚠️  Press Ctrl+C to stop monitoring")
        print("-" * 60)

        try:
            while True:
                self._check_log_file(self.log_file)
                self._check_log_file(self.security_log_file)
                self._check_alert_thresholds()
                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print("\n🛑 Security monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")

    def _check_log_file(self, log_file: Path):
        """Check a specific log file for security events"""
        if not log_file.exists():
            return

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to last position
                if log_file in self.last_positions:
                    f.seek(self.last_positions[log_file])

                # Read new lines
                lines = f.readlines()
                if lines:
                    self.last_positions[log_file] = f.tell()

                    for line in lines:
                        self._analyze_log_line(line.strip(), log_file.name)

        except Exception as e:
            print(f"⚠️  Error reading {log_file}: {e}")

    def _analyze_log_line(self, line: str, source: str):
        """Analyze a log line for security events"""
        if not line:
            return

        # Check for security patterns
        for pattern_name, pattern in self.security_patterns.items():
            if pattern.search(line):
                self._handle_security_event(pattern_name, line, source)
                break

    def _handle_security_event(self, event_type: str, line: str, source: str):
        """Handle a detected security event"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Initialize alert count if needed
        if event_type not in self.alert_counts:
            self.alert_counts[event_type] = []

        # Add current timestamp
        self.alert_counts[event_type].append(datetime.now())

        # Clean old entries (older than 1 minute)
        cutoff = datetime.now() - timedelta(minutes=1)
        self.alert_counts[event_type] = [
            ts for ts in self.alert_counts[event_type] if ts > cutoff
        ]

        # Log the security event
        print(f"🚨 [{timestamp}] SECURITY EVENT: {event_type.upper()}")
        print(f"   📄 Source: {source}")
        print(f"   📝 Details: {line[:100]}{'...' if len(line) > 100 else ''}")

        # Check if we should alert
        if len(self.alert_counts[event_type]) >= self.alert_thresholds.get(event_type, 1):
            self._send_alert(event_type, len(self.alert_counts[event_type]))

        print()

    def _check_alert_thresholds(self):
        """Check if any alert thresholds have been exceeded"""
        now = datetime.now()

        # Clean old alert counts (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        for event_type in self.alert_counts:
            self.alert_counts[event_type] = [
                ts for ts in self.alert_counts[event_type] if ts > cutoff
            ]

        # Check for sustained high activity
        total_recent_activity = sum(len(counts) for counts in self.alert_counts.values())

        if total_recent_activity >= self.alert_thresholds['suspicious_activity']:
            if (now - self.last_alert_time).seconds > 300:  # Only alert every 5 minutes
                self._send_alert('high_activity', total_recent_activity)
                self.last_alert_time = now

    def _send_alert(self, alert_type: str, count: int):
        """Send an alert for suspicious activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"🚨🚨🚨 [{timestamp}] ALERT: {alert_type.upper()} THRESHOLD EXCEEDED")
        print(f"   📊 Count: {count} events in the last minute")
        print(f"   🔔 Action Required: Review security logs immediately")
        print(f"   📞 Recommended: Check system access logs and block suspicious IPs")
        print("-" * 60)

        # In a real system, this would:
        # - Send email alerts
        # - Send Slack/Discord notifications
        # - Trigger incident response
        # - Log to SIEM system

    def generate_security_report(self) -> str:
        """Generate a security monitoring report"""
        report_lines = [
            "=" * 60,
            "SIFU SECURITY MONITORING REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📊 MONITORED PATTERNS:",
        ]

        for pattern_name in self.security_patterns.keys():
            count = len(self.alert_counts.get(pattern_name, []))
            report_lines.append(f"   • {pattern_name}: {count} recent events")

        report_lines.extend([
            "",
            "⚠️  ALERT THRESHOLDS:",
            f"   • Failed logins: {self.alert_thresholds['failed_login']}/min",
            f"   • Suspicious activity: {self.alert_thresholds['suspicious_activity']}/min",
            "",
            "📁 MONITORED FILES:",
            f"   • {self.log_file}",
            f"   • {self.security_log_file}",
            "",
            "=" * 60,
        ])

        return "\n".join(report_lines)

def main():
    """Main monitoring function"""
    import argparse

    parser = argparse.ArgumentParser(description='SIFU Security Log Monitor')
    parser.add_argument('--log-file', default='sifu.log', help='Main log file to monitor')
    parser.add_argument('--security-log', default='security_audit.log', help='Security audit log file')
    parser.add_argument('--report', action='store_true', help='Generate and print security report')

    args = parser.parse_args()

    monitor = SecurityLogMonitor(args.log_file, args.security_log)

    if args.report:
        print(monitor.generate_security_report())
    else:
        monitor.monitor_logs()

if __name__ == "__main__":
    main()
