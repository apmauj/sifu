"""
Tests for SimpleTOTP authentication service
"""

import pytest
import os
import time
from datetime import datetime, timedelta
from src.application.simple_totp import SimpleTOTP
import pyotp


class TestSimpleTOTP:
    """Test suite for SimpleTOTP class"""

    @pytest.fixture
    def totp_service(self):
        """Create a fresh TOTP service instance for each test"""
        # Set a fixed secret for predictable testing
        os.environ["MONITORING_TOTP_SECRET"] = "JBSWY3DPEHPK3PXP"
        service = SimpleTOTP()
        yield service
        # Cleanup
        service.valid_sessions.clear()

    @pytest.fixture
    def known_secret(self):
        """Return a known secret for testing"""
        return "JBSWY3DPEHPK3PXP"

    def test_initialization_with_env_secret(self, known_secret):
        """Test TOTP service initializes with environment secret"""
        os.environ["MONITORING_TOTP_SECRET"] = known_secret
        service = SimpleTOTP()

        assert service.secret == known_secret
        assert service.totp is not None
        assert isinstance(service.valid_sessions, dict)
        assert len(service.valid_sessions) == 0

    def test_initialization_without_env_secret(self):
        """Test TOTP service generates secret when not in environment"""
        # Remove env variable if exists
        if "MONITORING_TOTP_SECRET" in os.environ:
            del os.environ["MONITORING_TOTP_SECRET"]

        service = SimpleTOTP()

        assert service.secret is not None
        assert len(service.secret) == 32  # Base32 encoded
        assert service.secret.isupper()  # Base32 is uppercase

    def test_verify_code_valid(self, totp_service, known_secret):
        """Test verification with valid TOTP code"""
        # Generate current valid code
        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()

        session_id = "test-session-123"
        result = totp_service.verify_code(current_code, session_id)

        assert result is True
        assert session_id in totp_service.valid_sessions
        assert isinstance(totp_service.valid_sessions[session_id], datetime)

    def test_verify_code_invalid(self, totp_service):
        """Test verification with invalid TOTP code"""
        invalid_code = "000000"
        session_id = "test-session-invalid"

        result = totp_service.verify_code(invalid_code, session_id)

        assert result is False
        assert session_id not in totp_service.valid_sessions

    def test_verify_code_expired(self, totp_service, known_secret):
        """Test verification with expired TOTP code"""
        # Generate a code from 2 minutes ago (well beyond valid window)
        totp = pyotp.TOTP(known_secret)
        old_timestamp = int(time.time()) - 120  # 2 minutes ago
        expired_code = totp.at(old_timestamp)

        session_id = "test-session-expired"
        result = totp_service.verify_code(expired_code, session_id)

        assert result is False
        assert session_id not in totp_service.valid_sessions

    def test_verify_code_within_window(self, totp_service, known_secret):
        """Test verification with code from previous time window (±30s)"""
        # valid_window=1 means ±1 slot (±30 seconds)
        totp = pyotp.TOTP(known_secret)
        
        # Get code from previous slot (30 seconds ago)
        previous_timestamp = int(time.time()) - 30
        previous_code = totp.at(previous_timestamp)

        session_id = "test-session-window"
        result = totp_service.verify_code(previous_code, session_id)

        # Should be valid within window
        assert result is True
        assert session_id in totp_service.valid_sessions

    def test_is_session_valid_active(self, totp_service, known_secret):
        """Test session validation for active session"""
        # Create valid session first
        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()
        session_id = "test-session-active"

        totp_service.verify_code(current_code, session_id)

        # Check if session is valid
        assert totp_service.is_session_valid(session_id) is True

    def test_is_session_valid_nonexistent(self, totp_service):
        """Test session validation for non-existent session"""
        session_id = "nonexistent-session"

        assert totp_service.is_session_valid(session_id) is False

    def test_is_session_valid_expired(self, totp_service):
        """Test session validation for expired session"""
        session_id = "test-session-expired"

        # Manually create expired session
        expired_time = datetime.utcnow() - timedelta(hours=2)
        totp_service.valid_sessions[session_id] = expired_time

        # Should return False and remove session
        assert totp_service.is_session_valid(session_id) is False
        assert session_id not in totp_service.valid_sessions

    def test_invalidate_session(self, totp_service, known_secret):
        """Test manual session invalidation"""
        # Create valid session
        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()
        session_id = "test-session-invalidate"

        totp_service.verify_code(current_code, session_id)
        assert session_id in totp_service.valid_sessions

        # Invalidate session
        totp_service.invalidate_session(session_id)

        assert session_id not in totp_service.valid_sessions
        assert totp_service.is_session_valid(session_id) is False

    def test_get_provisioning_uri(self, totp_service, known_secret):
        """Test provisioning URI generation"""
        uri = totp_service.get_provisioning_uri("Test Account")

        assert uri.startswith("otpauth://totp/")
        assert "Test%20Account" in uri or "Test Account" in uri
        assert known_secret in uri
        assert "issuer=SIFU" in uri

    def test_get_current_code(self, totp_service, known_secret):
        """Test getting current TOTP code"""
        code = totp_service.get_current_code()

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

        # Verify it's actually valid
        totp = pyotp.TOTP(known_secret)
        assert totp.verify(code)

    def test_cleanup_expired_sessions(self, totp_service):
        """Test automatic cleanup of expired sessions"""
        # Create mix of valid and expired sessions
        totp_service.valid_sessions["valid-1"] = datetime.utcnow() + timedelta(
            hours=1
        )
        totp_service.valid_sessions["valid-2"] = datetime.utcnow() + timedelta(
            hours=1
        )
        totp_service.valid_sessions["expired-1"] = datetime.utcnow() - timedelta(
            hours=1
        )
        totp_service.valid_sessions["expired-2"] = datetime.utcnow() - timedelta(
            hours=2
        )

        # Trigger cleanup
        totp_service._cleanup_expired_sessions()

        # Only valid sessions should remain
        assert len(totp_service.valid_sessions) == 2
        assert "valid-1" in totp_service.valid_sessions
        assert "valid-2" in totp_service.valid_sessions
        assert "expired-1" not in totp_service.valid_sessions
        assert "expired-2" not in totp_service.valid_sessions

    def test_get_session_info(self, totp_service, known_secret):
        """Test getting session information"""
        # Create some sessions
        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()

        totp_service.verify_code(current_code, "session-1")
        totp_service.verify_code(current_code, "session-2")

        info = totp_service.get_session_info()

        assert info["active_sessions"] == 2
        assert info["session_duration_hours"] == 1
        assert info["totp_interval_seconds"] == 30

    def test_multiple_sessions_same_code(self, totp_service, known_secret):
        """Test creating multiple sessions with same valid code"""
        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()

        # Create multiple sessions with same code
        session_ids = ["session-1", "session-2", "session-3"]

        for session_id in session_ids:
            result = totp_service.verify_code(current_code, session_id)
            assert result is True

        # All sessions should be valid
        assert len(totp_service.valid_sessions) == 3
        for session_id in session_ids:
            assert totp_service.is_session_valid(session_id) is True

    def test_thread_safety_verify_code(self, totp_service, known_secret):
        """Test thread safety when verifying codes"""
        import threading

        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()

        results = []
        sessions = []

        def verify_in_thread(code, session):
            result = totp_service.verify_code(code, session)
            results.append(result)

        threads = []
        for i in range(10):
            session_id = f"thread-session-{i}"
            sessions.append(session_id)
            thread = threading.Thread(
                target=verify_in_thread, args=(current_code, session_id)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All verifications should succeed
        assert all(results)
        assert len(totp_service.valid_sessions) == 10

    def test_session_duration_configuration(self):
        """Test custom session duration from environment"""
        os.environ["MONITORING_SESSION_HOURS"] = "2"
        os.environ["MONITORING_TOTP_SECRET"] = "JBSWY3DPEHPK3PXP"

        service = SimpleTOTP()

        assert service.session_duration_hours == 2

        # Cleanup
        del os.environ["MONITORING_SESSION_HOURS"]

    def test_verify_code_empty_string(self, totp_service):
        """Test verification with empty code"""
        result = totp_service.verify_code("", "test-session")

        assert result is False

    def test_verify_code_non_numeric(self, totp_service):
        """Test verification with non-numeric code"""
        result = totp_service.verify_code("abcdef", "test-session")

        assert result is False

    def test_session_expiry_timing(self, totp_service, known_secret):
        """Test that session expires at correct time"""
        os.environ["MONITORING_SESSION_HOURS"] = "1"

        totp = pyotp.TOTP(known_secret)
        current_code = totp.now()
        session_id = "test-timing"

        totp_service.verify_code(current_code, session_id)

        # Session should be valid immediately
        assert totp_service.is_session_valid(session_id) is True

        # Manually set session to expire in 1 second
        totp_service.valid_sessions[session_id] = datetime.utcnow() + timedelta(
            seconds=1
        )

        # Still valid
        assert totp_service.is_session_valid(session_id) is True

        # Wait 2 seconds
        time.sleep(2)

        # Should be expired now
        assert totp_service.is_session_valid(session_id) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
