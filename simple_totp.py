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

logger = logging.getLogger(__name__)


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
        
        # Session duration (1 hour)
        self.session_duration_hours = int(
            os.getenv("MONITORING_SESSION_HOURS", "1")
        )
        
        logger.info("SimpleTOTP initialized successfully")

    def verify_code(self, code: str, session_id: str) -> bool:
        """
        Verify TOTP code and create temporary session if valid.
        
        Args:
            code: 6-digit TOTP code from authenticator app
            session_id: Unique session identifier (UUID)
            
        Returns:
            True if code is valid and session created, False otherwise
        """
        try:
            # Verify code with ±1 time window (±30 seconds tolerance)
            is_valid = self.totp.verify(code, valid_window=1)
            
            if is_valid:
                # Create session with expiry time
                expiry = datetime.utcnow() + timedelta(hours=self.session_duration_hours)
                
                with self._lock:
                    self.valid_sessions[session_id] = expiry
                    # Clean up expired sessions periodically
                    self._cleanup_expired_sessions()
                
                logger.info(f"Valid TOTP code verified, session created: {session_id}")
                return True
            else:
                logger.warning(f"Invalid TOTP code attempt for session: {session_id}")
                return False
                
        except Exception as e:
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
                    logger.info(f"Session expired and removed: {session_id}")
                    return False
            
            return False

    def invalidate_session(self, session_id: str) -> None:
        """
        Manually invalidate a session (logout).
        
        Args:
            session_id: Session identifier to invalidate
        """
        with self._lock:
            if session_id in self.valid_sessions:
                del self.valid_sessions[session_id]
                logger.info(f"Session manually invalidated: {session_id}")

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


# Global instance
totp_service = SimpleTOTP()
