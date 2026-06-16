"""
Configuration validator for secure startup
Validates environment variables and configuration before application starts.
Updated: removed secret_manager dependency, uses os.getenv() directly.
"""

import os
import sys
import logging
from typing import List, Tuple
from pathlib import Path


class ConfigurationValidator:
    """Validates application configuration and environment variables"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _get_env(self, key: str, default: str = "") -> str:
        """Get environment variable value, handling bool-like values."""
        value = os.getenv(key, default)
        if isinstance(value, bool):
            return str(value).lower()
        return str(value) if value else ""

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all configuration validations"""
        self.errors = []
        self.warnings = []

        # Validate required environment variables
        self._validate_required_vars()

        # Validate database configuration
        self._validate_database_config()

        # Validate security settings
        self._validate_security_config()

        # Validate CORS configuration
        self._validate_cors_config()

        # Validate environment-specific settings
        self._validate_environment_config()

        # Validate file permissions
        self._validate_file_permissions()

        success = len(self.errors) == 0
        return success, self.errors, self.warnings

    def _validate_required_vars(self):
        """Validate that all required environment variables are present"""
        required_vars = ["DATABASE_URL", "SECRET_KEY", "API_KEY"]

        missing_vars = []
        for var in required_vars:
            if not self._get_env(var):
                missing_vars.append(var)

        if missing_vars:
            self.errors.append(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            self.errors.append(
                "Please set these environment variables or use the .env.template file"
            )

    def _validate_database_config(self):
        """Validate database configuration"""
        db_url = self._get_env("DATABASE_URL")
        if not db_url:
            return  # Already caught by required vars validation

        # Validate URL format
        if not db_url.startswith(("postgresql://", "sqlite:///", "mysql://")):
            self.errors.append(
                "DATABASE_URL must start with postgresql://, sqlite:///, or mysql://"
            )

        # Check for insecure configurations
        if "password" in db_url and "localhost" not in db_url:
            self.warnings.append(
                "Database URL contains password - ensure connection is encrypted in production"
            )

        # SQLite specific validations
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            if db_path != ":memory:" and not Path(db_path).parent.exists():
                self.warnings.append(
                    f"SQLite database directory does not exist: {Path(db_path).parent}"
                )

    def _validate_security_config(self):
        """Validate security-related configuration"""
        # SECRET_KEY validation
        secret_key = self._get_env("SECRET_KEY")
        if secret_key and len(secret_key) < 32:
            self.errors.append("SECRET_KEY must be at least 32 characters long")

        # API_KEY validation
        api_key = self._get_env("API_KEY")
        if api_key and len(api_key) < 20:
            self.warnings.append(
                "API_KEY should be at least 20 characters long for security"
            )

        # JWT_SECRET_KEY validation
        jwt_secret = self._get_env("JWT_SECRET_KEY")
        if jwt_secret and len(jwt_secret) < 32:
            self.errors.append("JWT_SECRET_KEY must be at least 32 characters long")

        # MONITORING_TOTP_SECRET validation
        totp_secret = self._get_env("MONITORING_TOTP_SECRET")
        if not totp_secret:
            self.warnings.append(
                "MONITORING_TOTP_SECRET is not set. The monitoring dashboard will "
                "generate a new secret on every server restart, invalidating your "
                "authenticator app setup. Set it in Render Environment variables to "
                "persist across restarts."
            )
        elif len(totp_secret) < 16:
            self.errors.append(
                "MONITORING_TOTP_SECRET should be at least 16 characters (base32). "
                "Generate one with: python -c \"import pyotp; print(pyotp.random_base32())\""
            )

        # Environment validation
        environment = self._get_env("ENVIRONMENT", "development")
        if environment not in ["development", "staging", "production"]:
            self.warnings.append(
                f"ENVIRONMENT should be one of: development, staging, production. Got: {environment}"
            )

        # Debug mode validation
        debug = self._get_env("DEBUG", "false").lower() == "true"
        if debug and environment == "production":
            self.errors.append("DEBUG mode must be disabled in production environment")

        # Log level validation
        log_level = self._get_env("LOG_LEVEL", "INFO").upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            self.warnings.append(
                f"LOG_LEVEL should be one of: {', '.join(valid_levels)}. Got: {log_level}"
            )

    def _validate_cors_config(self):
        """Validate CORS configuration"""
        allow_origins = self._get_env("ALLOW_ORIGINS", "")

        if not allow_origins:
            if self._get_env("ENVIRONMENT") == "production":
                self.errors.append("ALLOW_ORIGINS must be configured in production")
            else:
                self.warnings.append(
                    "ALLOW_ORIGINS not configured - using restrictive defaults"
                )
            return

        # Check for wildcard in production
        env_check = self._get_env("ENVIRONMENT")
        if "*" in allow_origins and env_check == "production":
            self.errors.append(
                "Wildcard (*) in ALLOW_ORIGINS is not allowed in production"
            )

        # Validate origin formats
        origins = [o.strip() for o in allow_origins.split(",") if o.strip()]
        for origin in origins:
            if not origin.startswith(("http://", "https://")) and origin != "*":
                self.errors.append(
                    f"Invalid CORS origin format: {origin}. Must start with http:// or https://"
                )

    def _validate_environment_config(self):
        """Validate environment-specific configuration"""
        environment = self._get_env("ENVIRONMENT", "development")

        if environment == "production":
            # Production-specific validations
            required_prod_vars = ["ALLOW_ORIGINS", "LOG_LEVEL"]

            for var in required_prod_vars:
                if not self._get_env(var):
                    self.errors.append(
                        f"{var} must be configured in production environment"
                    )

            # Check for development settings in production
            dev_indicators = {"DEBUG": "true", "LOG_LEVEL": "debug"}

            for var, bad_value in dev_indicators.items():
                if self._get_env(var).lower() == bad_value.lower():
                    self.errors.append(f"{var}={bad_value} is not allowed in production")

        elif environment == "development":
            # Development-specific validations
            if not self._get_env("DEBUG"):
                self.warnings.append("Consider setting DEBUG=true for development")

    def _validate_file_permissions(self):
        """Validate file and directory permissions"""
        sensitive_files = [".env", "security_audit.log", "sifu.log"]

        for file_path in sensitive_files:
            if Path(file_path).exists():
                try:
                    stat_info = os.stat(file_path)
                    # Check if file is world-readable
                    if stat_info.st_mode & 0o004:
                        self.warnings.append(
                            f"File {file_path} is world-readable. Consider restricting permissions."
                        )
                except OSError:
                    self.warnings.append(f"Cannot check permissions for {file_path}")

    def generate_config_report(self) -> str:
        """Generate a configuration validation report"""
        success, errors, warnings = self.validate_all()

        report_lines = [
            "=" * 60,
            "SIFU CONFIGURATION VALIDATION REPORT",
            "=" * 60,
            f"Status: {'PASSED' if success else 'FAILED'}",
            f"Errors: {len(errors)}",
            f"Warnings: {len(warnings)}",
            "",
        ]

        if errors:
            report_lines.extend(
                [
                    "ERRORS:",
                    "-" * 20,
                ]
            )
            report_lines.extend(f"  * {error}" for error in errors)
            report_lines.append("")

        if warnings:
            report_lines.extend(
                [
                    "WARNINGS:",
                    "-" * 20,
                ]
            )
            report_lines.extend(f"  * {warning}" for warning in warnings)
            report_lines.append("")

        if success:
            report_lines.extend(
                [
                    "CONFIGURATION VALID",
                    "All security checks passed. Application is ready to start.",
                ]
            )
        else:
            report_lines.extend(
                [
                    "CONFIGURATION INVALID",
                    "Please fix the errors above before starting the application.",
                ]
            )

        report_lines.extend(
            [
                "",
                "=" * 60,
            ]
        )

        return "\n".join(report_lines)

    def save_report(self, filepath: str = "config_validation_report.txt"):
        """Save validation report to file"""
        report = self.generate_config_report()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        self.logger.info(f"Configuration report saved to {filepath}")


def validate_configuration_on_startup():
    """Validate configuration at application startup"""
    validator = ConfigurationValidator()
    success, errors, warnings = validator.validate_all()

    # Log results
    if errors:
        for error in errors:
            logging.error(f"Configuration error: {error}")

    if warnings:
        for warning in warnings:
            logging.warning(f"Configuration warning: {warning}")

    if success:
        logging.info("Configuration validation passed")
    else:
        logging.error("Configuration validation failed")
        print("\n" + "=" * 60)
        print("CONFIGURATION VALIDATION FAILED")
        print("=" * 60)
        for error in errors:
            print(f"  * {error}")
        print("\nPlease fix these issues before starting the application.")
        print("=" * 60)

        # Exit with error code in production
        if os.getenv("ENVIRONMENT") == "production":
            sys.exit(1)

    return success


if __name__ == "__main__":
    # Run validation when script is executed directly
    validator = ConfigurationValidator()
    report = validator.generate_config_report()
    print(report)

    # Save report to file
    validator.save_report()
