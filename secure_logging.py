"""
Secure logging system with encryption and audit capabilities
"""
import logging
import logging.handlers
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

# Optional cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None
    hashes = None
    PBKDF2HMAC = None
    base64 = None

class SecureLogFormatter(logging.Formatter):
    """Custom log formatter with security features"""

    def __init__(self, encrypt_sensitive: bool = False, encryption_key: Optional[str] = None):
        super().__init__()
        self.encrypt_sensitive = encrypt_sensitive and CRYPTOGRAPHY_AVAILABLE
        self.cipher = None

        if self.encrypt_sensitive and encryption_key:
            self.cipher = self._setup_cipher(encryption_key)
        elif encrypt_sensitive and not CRYPTOGRAPHY_AVAILABLE:
            print("Warning: cryptography module not available, disabling log encryption")

    def _setup_cipher(self, key: str):
        """Setup encryption cipher"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography module is required for encryption")

        # Derive key using PBKDF2
        salt = b'sifu_log_salt_2024'  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_bytes = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(key_bytes)

    def _encrypt_sensitive_data(self, message: str) -> str:
        """Encrypt sensitive data in log messages"""
        if not self.cipher:
            return message

        # Find and encrypt sensitive patterns
        sensitive_patterns = [
            r'DATABASE_URL=[^\s]+',
            r'SECRET_KEY=[^\s]+',
            r'API_KEY=[^\s]+',
            r'password=[^\s]+',
            r'token=[^\s]+',
            r'Bearer\s+[^\s]+',
        ]

        encrypted_message = message
        for pattern in sensitive_patterns:
            import re
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                if self.cipher:
                    encrypted = self.cipher.encrypt(match.encode()).decode()
                    encrypted_message = encrypted_message.replace(match, f'[ENCRYPTED:{encrypted}]')

        return encrypted_message

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with security features"""
        # Add security metadata
        record.security_level = getattr(record, 'security_level', 'INFO')
        record.request_id = getattr(record, 'request_id', 'N/A')
        record.user_id = getattr(record, 'user_id', 'N/A')
        record.ip_address = getattr(record, 'ip_address', 'N/A')

        # Format message
        message = super().format(record)

        # Encrypt sensitive data if enabled
        if self.encrypt_sensitive:
            message = self._encrypt_sensitive_data(message)

        # Add integrity hash for critical logs
        if record.levelno >= logging.WARNING:
            message_hash = hashlib.sha256(message.encode()).hexdigest()[:16]
            message = f"{message} [HASH:{message_hash}]"

        return message

class SecurityAuditHandler(logging.Handler):
    """Handler for security audit logs"""

    def __init__(self, log_file: str = 'logs/security_audit.log', max_bytes: int = 10*1024*1024, backup_count: int = 5):
        super().__init__()
        self.log_file = Path(log_file)

        # Create rotating file handler
        self.handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # Set format for audit logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(security_level)s - '
            '%(request_id)s - %(user_id)s - %(ip_address)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.handler.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit security audit log"""
        # Only log security-related events
        if hasattr(record, 'security_event') and record.security_event:
            self.handler.emit(record)

class LogEncryptor:
    """Handles log encryption/decryption for sensitive data"""

    def __init__(self, key: str):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography module is required for log encryption")
        self.cipher = self._setup_cipher(key)

    def _setup_cipher(self, key: str):
        """Setup encryption cipher"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography module is required for encryption")

        salt = b'sifu_log_encrypt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_bytes = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        return Fernet(key_bytes)

    def encrypt_log_entry(self, log_entry: str) -> str:
        """Encrypt a log entry"""
        return self.cipher.encrypt(log_entry.encode()).decode()

    def decrypt_log_entry(self, encrypted_entry: str) -> str:
        """Decrypt a log entry"""
        return self.cipher.decrypt(encrypted_entry.encode()).decode()

class SecurityLogger:
    """Centralized security logging"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('sifu.security')
        self.logger.setLevel(getattr(logging, config.get('log_level', 'INFO')))

        # Setup formatters
        encrypt_logs = config.get('encrypt_logs', False)
        encryption_key = config.get('log_encryption_key')

        formatter = SecureLogFormatter(encrypt_logs, encryption_key)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler for general logs
        if config.get('log_file'):
            # Auto-redirect plain filenames *.log or *.txt into logs/ if path not provided
            raw_path = Path(config['log_file'])
            if not raw_path.parent or str(raw_path.parent) == '.':
                if raw_path.suffix in {'.log', '.txt'}:
                    raw_path = Path('logs') / raw_path.name
            try:
                raw_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            file_handler = logging.handlers.RotatingFileHandler(
                raw_path,
                maxBytes=config.get('max_log_size', 100*1024*1024),
                backupCount=config.get('log_backup_count', 5),
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Security audit handler
        if config.get('audit_logging_enabled', True):
            audit_path = config.get('audit_log_file', 'logs/security_audit.log')
            # Redirect plain audit filename
            ap = Path(audit_path)
            if not ap.parent or str(ap.parent) == '.':
                if ap.suffix in {'.log', '.txt'}:
                    audit_path = str(Path('logs') / ap.name)
            audit_handler = SecurityAuditHandler(audit_path)
            self.logger.addHandler(audit_handler)

        # Log encryptor for sensitive data
        self.log_encryptor = None
        if encrypt_logs and encryption_key:
            self.log_encryptor = LogEncryptor(encryption_key)

    def log_security_event(self, event_type: str, message: str,
                          request_id: str = 'N/A', user_id: str = 'N/A',
                          ip_address: str = 'N/A', extra_data: Optional[Dict] = None):
        """Log a security event"""
        extra = {
            'security_event': True,
            'security_level': event_type.upper(),
            'request_id': request_id,
            'user_id': user_id,
            'ip_address': ip_address,
        }

        if extra_data:
            extra.update(extra_data)

        if event_type.upper() in ['CRITICAL', 'ERROR']:
            self.logger.error(message, extra=extra)
        elif event_type.upper() == 'WARNING':
            self.logger.warning(message, extra=extra)
        else:
            self.logger.info(message, extra=extra)

    def log_authentication(self, success: bool, username: str,
                          ip_address: str, user_agent: str = 'N/A'):
        """Log authentication attempt"""
        event_type = 'SUCCESS' if success else 'FAILURE'
        message = f'Authentication {event_type} for user: {username}'
        extra_data = {
            'user_agent': user_agent,
            'auth_success': success
        }
        self.log_security_event('AUTH', message, user_id=username,
                               ip_address=ip_address, extra_data=extra_data)

    def log_rate_limit(self, ip_address: str, endpoint: str, request_count: int):
        """Log rate limiting event"""
        message = f'Rate limit exceeded: {request_count} requests from {ip_address} to {endpoint}'
        self.log_security_event('RATE_LIMIT', message, ip_address=ip_address)

    def log_suspicious_activity(self, ip_address: str, activity: str, details: str = ''):
        """Log suspicious activity"""
        message = f'Suspicious activity detected: {activity} from {ip_address}'
        if details:
            message += f' - {details}'
        self.log_security_event('SUSPICIOUS', message, ip_address=ip_address)

    def log_config_change(self, change_type: str, key: str, old_value: str = 'N/A', new_value: str = 'N/A'):
        """Log configuration changes"""
        message = f'Configuration change: {change_type} - {key}: {old_value} -> {new_value}'
        # Encrypt sensitive config changes
        if self.log_encryptor and any(sensitive in key.upper() for sensitive in ['SECRET', 'KEY', 'PASSWORD']):
            if old_value != 'N/A':
                old_value = self.log_encryptor.encrypt_log_entry(old_value)
            if new_value != 'N/A':
                new_value = self.log_encryptor.encrypt_log_entry(new_value)
            message = f'Configuration change: {change_type} - {key}: [ENCRYPTED] -> [ENCRYPTED]'

        self.log_security_event('CONFIG', message)

    def log_data_access(self, user_id: str, resource: str, action: str, ip_address: str):
        """Log data access events"""
        message = f'Data access: {action} on {resource} by {user_id}'
        self.log_security_event('DATA_ACCESS', message, user_id=user_id, ip_address=ip_address)

class LogAnalyzer:
    """Analyze logs for security patterns"""

    def __init__(self, log_file: str):
        self.log_file = Path(log_file)

    def analyze_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze recent security activity"""
        if not self.log_file.exists():
            return {'error': 'Log file not found'}

        analysis = {
            'total_events': 0,
            'security_events': 0,
            'auth_failures': 0,
            'rate_limit_events': 0,
            'suspicious_activity': 0,
            'ip_addresses': {},
            'event_types': {},
        }

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    analysis['total_events'] += 1

                    if 'security_event' in line.lower():
                        analysis['security_events'] += 1

                    if 'authentication failure' in line.lower():
                        analysis['auth_failures'] += 1

                    if 'rate limit' in line.lower():
                        analysis['rate_limit_events'] += 1

                    if 'suspicious activity' in line.lower():
                        analysis['suspicious_activity'] += 1

                    # Extract IP addresses
                    import re
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        analysis['ip_addresses'][ip] = analysis['ip_addresses'].get(ip, 0) + 1

        except Exception as e:
            analysis['error'] = f'Analysis failed: {str(e)}'

        return analysis

# Global security logger instance
security_logger = None

def init_security_logging(config: Dict[str, Any]) -> SecurityLogger:
    """Initialize security logging system"""
    global security_logger
    security_logger = SecurityLogger(config)
    return security_logger

def get_security_logger() -> Optional[SecurityLogger]:
    """Get the global security logger instance"""
    return security_logger
