"""
Secure configuration management for SIFU
Handles environment variables, secrets validation, and secure defaults
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
import secrets
import string
from dotenv import load_dotenv


class SecretManager:
    """Manages application secrets and configuration securely"""

    # Critical security secrets that must be set
    REQUIRED_SECRETS = [
        "DATABASE_URL",  # Database connection string
        "SECRET_KEY",  # For session management/cookies
        "API_KEY",  # For external API access (if needed)
    ]

    # Optional but recommended secrets
    OPTIONAL_SECRETS = [
        "ENCRYPTION_KEY",  # For data encryption
        "JWT_SECRET",  # For JWT tokens (if implemented)
        "REDIS_URL",  # For caching (if used)
        "LOG_ENCRYPTION_KEY",  # For log encryption
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._secrets: Dict[str, str] = {}
        self._validated = False

    def load_secrets(self) -> Dict[str, str]:
        """Load all secrets from environment variables"""
        # Load .env file if it exists
        load_dotenv()

        secrets = {}

        # Load required secrets
        for secret_name in self.REQUIRED_SECRETS:
            value = os.getenv(secret_name)
            if value:
                secrets[secret_name] = value
            else:
                self.logger.warning(
                    f"Required secret {secret_name} not found in environment"
                )

        # Load optional secrets
        for secret_name in self.OPTIONAL_SECRETS:
            value = os.getenv(secret_name)
            if value:
                secrets[secret_name] = value

        # Load CORS and other configuration
        cors_origins = os.getenv("ALLOW_ORIGINS", "")
        if cors_origins:
            secrets["ALLOW_ORIGINS"] = cors_origins

        # Load security settings
        secrets["ENVIRONMENT"] = os.getenv("ENVIRONMENT", "development")
        secrets["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"
        secrets["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")

        self._secrets = secrets
        return secrets

    def validate_secrets(self) -> tuple[bool, List[str]]:
        """Validate that all required secrets are properly configured"""
        missing_secrets = []
        validation_errors = []

        # Check required secrets
        for secret_name in self.REQUIRED_SECRETS:
            if secret_name not in self._secrets:
                missing_secrets.append(secret_name)
            else:
                # Validate secret format/strength
                error = self._validate_secret_format(
                    secret_name, self._secrets[secret_name]
                )
                if error:
                    validation_errors.append(error)

        # Validate CORS configuration
        if "ALLOW_ORIGINS" in self._secrets:
            cors_error = self._validate_cors_origins(self._secrets["ALLOW_ORIGINS"])
            if cors_error:
                validation_errors.append(cors_error)

        # Validate environment-specific settings
        env_errors = self._validate_environment_settings()
        validation_errors.extend(env_errors)

        self._validated = len(missing_secrets) == 0 and len(validation_errors) == 0

        return self._validated, missing_secrets + validation_errors

    def _validate_secret_format(self, name: str, value: str) -> Optional[str]:
        """Validate individual secret format and strength"""
        if not value or len(value.strip()) == 0:
            return f"{name}: Secret cannot be empty"

        if name == "SECRET_KEY" and len(value) < 32:
            return f"{name}: Secret key must be at least 32 characters long"

        if name == "DATABASE_URL":
            if not value.startswith(("postgresql://", "sqlite://", "mysql://")):
                return f"{name}: Invalid database URL format"

        if name == "API_KEY" and len(value) < 20:
            return f"{name}: API key must be at least 20 characters long"

        return None

    def _validate_cors_origins(self, origins_str: str) -> Optional[str]:
        """Validate CORS origins configuration"""
        if not origins_str:
            return None

        origins = [o.strip() for o in origins_str.split(",") if o.strip()]

        for origin in origins:
            if origin == "*":
                return "CORS: Wildcard origin (*) not allowed in production"
            if not origin.startswith(("http://", "https://")):
                return f"CORS: Invalid origin format: {origin}"

        return None

    def _validate_environment_settings(self) -> List[str]:
        """Validate environment-specific security settings"""
        errors = []
        environment = self._secrets.get("ENVIRONMENT", "development")

        if environment == "production":
            # Production-specific validations
            if self._secrets.get("DEBUG", False):
                errors.append("DEBUG: Debug mode must be disabled in production")

            if not self._secrets.get("ALLOW_ORIGINS"):
                errors.append("ALLOW_ORIGINS: Must be configured in production")

            log_level = self._secrets.get("LOG_LEVEL", "INFO")
            if log_level.upper() not in ["INFO", "WARNING", "ERROR"]:
                errors.append(
                    "LOG_LEVEL: Must be INFO, WARNING, or ERROR in production"
                )

        return errors

    def generate_secure_defaults(self) -> Dict[str, str]:
        """Generate secure default values for development/testing"""
        defaults = {}

        # Generate a secure random secret key
        defaults["SECRET_KEY"] = self._generate_secret_key()

        # Generate API key
        defaults["API_KEY"] = self._generate_api_key()

        # Default database URL for development
        defaults["DATABASE_URL"] = "sqlite:///test_ur.db"

        # Default CORS for development
        defaults["ALLOW_ORIGINS"] = (
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
        )

        return defaults

    def _generate_secret_key(self, length: int = 64) -> str:
        """Generate a cryptographically secure secret key"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _generate_api_key(self, length: int = 32) -> str:
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value safely"""
        return self._secrets.get(name, default)

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self._secrets.get("ENVIRONMENT", "development") == "production"

    def should_encrypt_logs(self) -> bool:
        """Check if logs should be encrypted"""
        return "LOG_ENCRYPTION_KEY" in self._secrets and self.is_production()

    def get_security_config(self) -> Dict[str, Any]:
        """Get security-related configuration"""
        return {
            "environment": self._secrets.get("ENVIRONMENT", "development"),
            "debug": self._secrets.get("DEBUG", False),
            "log_level": self._secrets.get("LOG_LEVEL", "INFO"),
            "cors_origins": self._secrets.get("ALLOW_ORIGINS", ""),
            "rate_limiting_enabled": not self._secrets.get(
                "DISABLE_RATE_LIMITING", False
            ),
            "encryption_enabled": "ENCRYPTION_KEY" in self._secrets,
            "audit_logging_enabled": self.is_production(),
        }

    def save_env_template(self, filepath: str = ".env.template"):
        """Save environment template file with secure defaults"""
        template_content = f"""# SIFU Environment Configuration Template
# Copy this file to .env and fill in your actual values
# Generated on: {os.getenv('CURRENT_DATE', '2025-08-29')}

# ===========================================
# REQUIRED SECRETS (Must be configured)
# ===========================================

# Database connection string
# Format: postgresql://user:password@host:port/database
# For development: sqlite:///sifu.db
DATABASE_URL=sqlite:///sifu.db

# Secret key for session management (min 32 chars)
SECRET_KEY={self._generate_secret_key()}

# API key for external services (min 20 chars)
API_KEY={self._generate_api_key()}

# ===========================================
# OPTIONAL SECRETS (Recommended for production)
# ===========================================

# Encryption key for sensitive data (32 chars)
ENCRYPTION_KEY={self._generate_secret_key(32)}

# JWT secret for token authentication (if implemented)
JWT_SECRET={self._generate_secret_key()}

# Redis URL for caching (if used)
REDIS_URL=redis://localhost:6379

# Log encryption key (for production log security)
LOG_ENCRYPTION_KEY={self._generate_secret_key(32)}

# ===========================================
# APPLICATION CONFIGURATION
# ===========================================

# Environment (development/production)
ENVIRONMENT=development

# Debug mode (disable in production)
DEBUG=false

# Logging level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO

# ===========================================
# SECURITY CONFIGURATION
# ===========================================

# CORS allowed origins (comma-separated)
# Production: https://yourdomain.com,https://www.yourdomain.com
# Development: http://localhost:3000,http://localhost:5173
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000

# Disable rate limiting (not recommended)
DISABLE_RATE_LIMITING=false

# ===========================================
# SCHEDULER CONFIGURATION
# ===========================================

# Enable/disable background scheduler
SIFU_SCHEDULER_ENABLED=true

# Timezone for scheduler
TIMEZONE=America/Montevideo

# Cron expressions for data refresh
CRON_UI_REFRESH=0 2 * * *
CRON_EXCHANGE_REFRESH=0 3 * * *
CRON_UR_REFRESH=0 4 1 * *

# ===========================================
# EXTERNAL API CONFIGURATION
# ===========================================

# BCU API settings
BCU_API_TIMEOUT=30
BCU_API_RETRIES=3

# BROU API settings
BROU_API_TIMEOUT=30
BROU_API_RETRIES=3

# ===========================================
# MONITORING & LOGGING
# ===========================================

# Enable security audit logging
AUDIT_LOGGING_ENABLED=true

# Log file path
LOG_FILE=sifu.log

# Maximum log file size (MB)
MAX_LOG_SIZE=100

# Log backup count
LOG_BACKUP_COUNT=5
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(template_content)

        self.logger.info(f"Environment template saved to {filepath}")

    def log_security_status(self):
        """Log current security configuration status"""
        if not self._validated:
            self.logger.warning("Security configuration not fully validated")

        # Log security status (without exposing secrets)
        status = {
            "environment": self._secrets.get("ENVIRONMENT"),
            "secrets_configured": len(
                [s for s in self.REQUIRED_SECRETS if s in self._secrets]
            ),
            "optional_secrets": len(
                [s for s in self.OPTIONAL_SECRETS if s in self._secrets]
            ),
            "cors_configured": "ALLOW_ORIGINS" in self._secrets,
            "encryption_enabled": "ENCRYPTION_KEY" in self._secrets,
            "production_mode": self.is_production(),
        }

        self.logger.info(f"Security status: {json.dumps(status, indent=2)}")


# Global instance
secret_manager = SecretManager()
