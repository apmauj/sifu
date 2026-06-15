"""
Configuration validator for secure startup
Validates environment variables and configuration before application starts

Adapted for Render deployment: uses os.getenv() directly instead of secret_manager.
Secrets are managed via Render Dashboard → Environment.
"""

import os
import sys
import logging
from typing import List, Tuple
from pathlib import Path


class ConfigurationValidator:
    """Validates application configuration via environment variables"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all configuration validations"""
        self.errors = []
        self.warnings = []

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

    def _validate_database_config(self):
        """Validate database configuration"""
        db_url = os.getenv("DATABASE_URL", "")
        db_path = os.getenv("DATABASE_PATH", "")

        if not db_url and not db_path:
            # Neither DATABASE_URL nor DATABASE_PATH set — acceptable for SQLite default
            self.warnings.append(
                "Neither DATABASE_URL nor DATABASE_PATH set. Using default SQLite path."
            )
            return

        if db_url:
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
                db_file_path = db_url.replace("sqlite:///", "")
                if db_file_path != ":memory:" and not Path(db_file_path).parent.exists():
                    self.warnings.append(
                        f"SQLite database directory does not exist: {Path(db_file_path).parent}"
                    )

        if db_path:
            # Validate DATABASE_PATH is writable
            parent = Path(db_path).parent
            if parent.exists() and not os.access(parent, os.W_OK):
                self.errors.append(f"DATABASE_PATH parent directory is not writable: {parent}")

    def _validate_security_config(self):
        """Validate security-related configuration"""
        # JWT Secret Key validation
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if jwt_secret and len(jwt_secret) < 32:
            self.errors.append("JWT_SECRET_KEY must be at least 32 characters long")

        # TOTP Secret validation
        totp_secret = os.getenv("MONITORING_TOTP_SECRET", "")
        if not totp_secret:
            self.warnings.append(
                "MONITORING_TOTP_SECRET not set. A new secret will be generated on each deploy, "
                "invalidating existing authenticator configurations. Set this in Render Dashboard → Environment."
            )

        # Environment validation
        environment = os.getenv("ENVIRONMENT", "development")
        if environment not in ["development", "staging", "production"]:
            self.warnings.append(
                f"ENVIRONMENT should be one of: development, staging, production. Got: {environment}"
            )

        # Debug mode validation
        debug = os.getenv("DEBUG", "false").lower() == "true"
        if debug and environment == "production":
            self.errors.append("DEBUG mode must be disabled in production environment")

        # Log level validation
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            self.warnings.append(
                f"LOG_LEVEL should be one of: {', '.join(valid_levels)}. Got: {log_level}"
            )

    def _validate_cors_config(self):
        """Validate CORS configuration"""
        allow_origins = os.getenv("ALLOW_ORIGINS", "")
        environment = os.getenv("ENVIRONMENT", "development")

        if not allow_origins:
            if environment == "production":
                self.errors.append("ALLOW_ORIGINS must be configured in production")
            else:
                self.warnings.append(
                    "ALLOW_ORIGINS not configured - using restrictive defaults"
                )
            return

        # Check for wildcard in production
        if "*" in allow_origins and environment == "production":
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
        environment = os.getenv("ENVIRONMENT", "development")

        if environment == "production":
            # Production-specific validations
            required_prod_vars = ["ALLOW_ORIGINS"]

            for var in required_prod_vars:
                if not os.getenv(var):
                    self.errors.append(
                        f"{var} must be configured in production environment"
                    )

            # Check for development settings in production
            if os.getenv("DEBUG", "false").lower() == "true":
                self.errors.append("DEBUG=true is not allowed in production")

            if os.getenv("LOG_LEVEL", "").upper() == "DEBUG":
                self.errors.append("LOG_LEVEL=DEBUG is not allowed in production")

        elif environment == "development":
            # Development-specific validations
            if not os.getenv("DEBUG"):
                self.warnings.append("Consider setting DEBUG=true for development")

    def _validate_file_permissions(self):
        """Validate file and directory permissions"""
        sensitive_files = [".env", "security_audit.log", "sifu.log"]

        for file_path in sensitive_files:
            if Path(file_path).exists():
                # Check if file is readable by others (basic check)
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
            report_lines.extend(f"  - {error}" for error in errors)
            report_lines.append("")

        if warnings:
            report_lines.extend(
                [
                    "WARNINGS:",
                    "-" * 20,
                ]
            )
            report_lines.extend(f"  - {warning}" for warning in warnings)
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
            print(f"  - {error}")
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
