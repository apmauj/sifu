"""
Simple TOTP Service for Monitoring Dashboard Access
Provides lightweight authentication for internal monitoring without user management.
"""

import os
import pyotp
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from threading import Lock
from pathlib import Path

# Configure audit logging
logger = logging.getLogger(__name__)

# Create audit logger for TOTP events
audit_logger = logging.getLogger("totp_audit")
audit_logger.setLevel(logging.INFO)

# Ensure logs directory exists (skip if in test mode)
try:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler for audit logs if not already present
    if not audit_logger.handlers:
        audit_file_handler = logging.FileHandler("logs/totp_audit.log")
        audit_file_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        audit_file_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_file_handler)
except (OSError, PermissionError) as e:
    # If we can't create log file (e.g., in CI without permissions),
    # just log to console instead
    logger.warning(f"Could not create audit log file: {e}. Using console logging.")
    if not audit_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        audit_logger.addHandler(console_handler)


class SimpleTOTP:
    """
    Lightweight TOTP-based authentication for monitoring dashboard.
    Uses a single shared secret (no user database required).
    """

    def __init__(self):
        """Initialize TOTP service with shared secret from environment"""
        # Get shared secret from environment or generate a new one
        self.secret = os.getenv("MONITORING_TOTP_SECRET")
        
        if not self.secret:
            # Generate a new secret for first-time setup
            self.secret = pyotp.random_base32()
            logger.warning(
                f"No MONITORING_TOTP_SECRET found. Generated new secret: {self.secret}"
            )
            logger.warning(
                "Add this to your .env file: MONITORING_TOTP_SECRET=%s", self.secret
            )
        
        # Initialize TOTP with 30-second interval (standard)
        self.totp = pyotp.TOTP(self.secret)
        
        # In-memory session storage: {session_id: expiry_datetime}
        self.valid_sessions: Dict[str, datetime] = {}
        self._lock = Lock()
        
        # Metrics: Track failed attempts per IP
        self.failed_attempts: Dict[str, int] = {}  # ip -> count
        self.total_auth_attempts = 0
        self.total_auth_success = 0
        self.total_auth_failures = 0
        
        # Session duration (1 hour)
        self.session_duration_hours = int(
            os.getenv("MONITORING_SESSION_HOURS", "1")
        )
        
        logger.info("SimpleTOTP initialized successfully")

    def verify_code(
        self, code: str, session_id: str, client_ip: Optional[str] = None
    ) -> bool:
        """
        Verify TOTP code and create temporary session if valid.
        
        Args:
            code: 6-digit TOTP code from authenticator app
            session_id: Unique session identifier (UUID)
            client_ip: Optional client IP address for audit logging
            
        Returns:
            True if code is valid and session created, False otherwise
        """
        try:
            # Track total attempts
            self.total_auth_attempts += 1
            
            # Verify code with ±1 time window (±30 seconds tolerance)
            is_valid = self.totp.verify(code, valid_window=1)
            
            if is_valid:
                # Create session with expiry time
                expiry = datetime.utcnow() + timedelta(hours=self.session_duration_hours)
                
                with self._lock:
                    self.valid_sessions[session_id] = expiry
                    # Clean up expired sessions periodically
                    self._cleanup_expired_sessions()
                    
                    # Reset failed attempts for this IP on success
                    if client_ip and client_ip in self.failed_attempts:
                        del self.failed_attempts[client_ip]
                    
                    # Track success
                    self.total_auth_success += 1
                
                # Audit log: successful verification
                audit_logger.info(
                    f"TOTP_AUTH_SUCCESS | session={session_id[:8]} | "
                    f"ip={client_ip or 'unknown'} | "
                    f"expires={expiry.isoformat()}"
                )
                logger.info(f"Valid TOTP code verified, session created: {session_id}")
                return True
            else:
                # Track failed attempt
                with self._lock:
                    if client_ip:
                        self.failed_attempts[client_ip] = self.failed_attempts.get(client_ip, 0) + 1
                    self.total_auth_failures += 1
                
                # Audit log: failed verification
                audit_logger.warning(
                    f"TOTP_AUTH_FAILED | session={session_id[:8]} | "
                    f"ip={client_ip or 'unknown'} | "
                    f"reason=invalid_code | "
                    f"failed_attempts={self.failed_attempts.get(client_ip or 'unknown', 0)}"
                )
                logger.warning(f"Invalid TOTP code attempt for session: {session_id}")
                return False
                
        except Exception as e:
            # Track error as failure
            self.total_auth_failures += 1
            
            # Audit log: verification error
            audit_logger.error(
                f"TOTP_AUTH_ERROR | session={session_id[:8]} | "
                f"ip={client_ip or 'unknown'} | "
                f"error={str(e)}"
            )
            logger.error(f"Error verifying TOTP code: {e}")
            return False

    def is_session_valid(self, session_id: str) -> bool:
        """
        Check if a session is still valid (not expired).
        
        Args:
            session_id: Session identifier to check
            
        Returns:
            True if session exists and not expired, False otherwise
        """
        with self._lock:
            if session_id in self.valid_sessions:
                expiry = self.valid_sessions[session_id]
                
                # Check if session is still valid
                if datetime.utcnow() < expiry:
                    return True
                else:
                    # Session expired, remove it
                    del self.valid_sessions[session_id]
                    audit_logger.info(
                        f"TOTP_SESSION_EXPIRED | session={session_id[:8]}"
                    )
                    logger.info(f"Session expired and removed: {session_id}")
                    return False
            
            return False

    def invalidate_session(self, session_id: str, client_ip: Optional[str] = None) -> None:
        """
        Manually invalidate a session (logout).
        
        Args:
            session_id: Session identifier to invalidate
            client_ip: Optional client IP address for audit logging
        """
        with self._lock:
            if session_id in self.valid_sessions:
                del self.valid_sessions[session_id]
                audit_logger.info(
                    f"TOTP_SESSION_LOGOUT | session={session_id[:8]} | "
                    f"ip={client_ip or 'unknown'}"
                )
                logger.info(f"Session manually invalidated: {session_id}")
            else:
                audit_logger.warning(
                    f"TOTP_SESSION_LOGOUT_FAILED | session={session_id[:8]} | "
                    f"ip={client_ip or 'unknown'} | "
                    f"reason=session_not_found"
                )

    def get_provisioning_uri(self, name: str = "SIFU Monitoring") -> str:
        """
        Get provisioning URI for QR code generation.
        Used for initial setup with authenticator apps.
        
        Args:
            name: Account name to display in authenticator app
            
        Returns:
            otpauth:// URI for QR code generation
        """
        return self.totp.provisioning_uri(
            name=name,
            issuer_name="SIFU"
        )

    def get_current_code(self) -> str:
        """
        Get current valid TOTP code.
        WARNING: Only for debugging/testing! Never expose in production API.
        
        Returns:
            Current 6-digit TOTP code
        """
        return self.totp.now()

    def _cleanup_expired_sessions(self) -> None:
        """
        Remove expired sessions from memory.
        Called periodically during verify_code operations.
        """
        now = datetime.utcnow()
        expired = [
            session_id
            for session_id, expiry in self.valid_sessions.items()
            if now >= expiry
        ]
        
        for session_id in expired:
            del self.valid_sessions[session_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    def get_session_info(self) -> Dict:
        """
        Get information about current sessions.
        For monitoring/debugging purposes.
        
        Returns:
            Dictionary with session count and details
        """
        with self._lock:
            active_count = len(self.valid_sessions)
            
            return {
                "active_sessions": active_count,
                "session_duration_hours": self.session_duration_hours,
                "totp_interval_seconds": 30,
            }

    def get_metrics(self) -> Dict:
        """
        Get authentication metrics for monitoring.
        
        Returns:
            Dictionary with authentication statistics
        """
        with self._lock:
            success_rate = (
                (self.total_auth_success / self.total_auth_attempts * 100)
                if self.total_auth_attempts > 0
                else 0.0
            )
            
            return {
                "total_attempts": self.total_auth_attempts,
                "successful_authentications": self.total_auth_success,
                "failed_authentications": self.total_auth_failures,
                "success_rate_percent": round(success_rate, 2),
                "failed_attempts_by_ip": dict(self.failed_attempts),
                "ips_with_failures": len(self.failed_attempts),
                "active_sessions": len(self.valid_sessions),
            }


# Global instance
totp_service = SimpleTOTP()
