"""
Configuration validator for secure startup
Validates secrets and configuration before application starts
"""

import os
import sys
import logging
from typing import List, Tuple
from pathlib import Path
from src.application.secret_manager import secret_manager


class ConfigurationValidator:
    """Validates application configuration and secrets"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        # Load secrets using the secret manager
        self._secrets = secret_manager.load_secrets()

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all configuration validations"""
        self.errors = []
        self.warnings = []

        # Validate required secrets
        self._validate_required_secrets()

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

    def _validate_required_secrets(self):
        """Validate that all required secrets are present"""
        required_secrets = ["DATABASE_URL", "SECRET_KEY", "API_KEY"]

        missing_secrets = []
        for secret in required_secrets:
            if secret not in self._secrets or not self._secrets[secret]:
                missing_secrets.append(secret)

        if missing_secrets:
            self.errors.append(
                f"Missing required secrets: {', '.join(missing_secrets)}"
            )
            self.errors.append(
                "Please set these environment variables or use the .env.template file"
            )

    def _validate_database_config(self):
        """Validate database configuration"""
        db_url = self._secrets.get("DATABASE_URL")
        if not db_url:
            return  # Already caught by required secrets validation

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
        secret_key = self._secrets.get("SECRET_KEY")
        if secret_key and len(secret_key) < 32:
            self.errors.append("SECRET_KEY must be at least 32 characters long")

        # API_KEY validation
        api_key = self._secrets.get("API_KEY")
        if api_key and len(api_key) < 20:
            self.warnings.append(
                "API_KEY should be at least 20 characters long for security"
            )

        # Environment validation
        environment_value = self._secrets.get("ENVIRONMENT", "development")
        if isinstance(environment_value, str):
            environment = environment_value
        else:
            environment = str(environment_value)
        if environment not in ["development", "staging", "production"]:
            self.warnings.append(
                f"ENVIRONMENT should be one of: development, staging, production. Got: {environment}"
            )

        # Debug mode validation
        debug_value = self._secrets.get("DEBUG", "false")
        if isinstance(debug_value, bool):
            debug = debug_value
        else:
            debug = str(debug_value).lower() == "true"
        if debug and environment == "production":
            self.errors.append("DEBUG mode must be disabled in production environment")

        # Log level validation
        log_level_value = self._secrets.get("LOG_LEVEL", "INFO")
        if isinstance(log_level_value, str):
            log_level = log_level_value.upper()
        else:
            log_level = str(log_level_value).upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            self.warnings.append(
                f"LOG_LEVEL should be one of: {', '.join(valid_levels)}. Got: {log_level}"
            )

    def _validate_cors_config(self):
        """Validate CORS configuration"""
        allow_origins = self._secrets.get("ALLOW_ORIGINS", "")

        if not allow_origins:
            if self._secrets.get("ENVIRONMENT") == "production":
                self.errors.append("ALLOW_ORIGINS must be configured in production")
            else:
                self.warnings.append(
                    "ALLOW_ORIGINS not configured - using restrictive defaults"
                )
            return

        # Check for wildcard in production
        env_value = self._secrets.get("ENVIRONMENT")
        if isinstance(env_value, str):
            env_check = env_value
        else:
            env_check = str(env_value)
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
        environment_value = self._secrets.get("ENVIRONMENT", "development")
        if isinstance(environment_value, str):
            environment = environment_value
        else:
            environment = str(environment_value)

        if environment == "production":
            # Production-specific validations
            required_prod_vars = ["ALLOW_ORIGINS", "LOG_LEVEL"]

            for var in required_prod_vars:
                if var not in self._secrets or not self._secrets[var]:
                    self.errors.append(
                        f"{var} must be configured in production environment"
                    )

            # Check for development settings in production
            dev_indicators = ["DEBUG=true", "LOG_LEVEL=DEBUG"]

            for indicator in dev_indicators:
                var, expected = indicator.split("=")
                actual_value = self._secrets.get(var, "")
                # Handle boolean values
                if isinstance(actual_value, bool):
                    actual_str = str(actual_value).lower()
                else:
                    actual_str = str(actual_value).lower()
                if actual_str == expected.lower():
                    self.errors.append(f"{var}={expected} is not allowed in production")

        elif environment == "development":
            # Development-specific validations
            if "DEBUG" not in self._secrets or not self._secrets.get("DEBUG"):
                self.warnings.append("Consider setting DEBUG=true for development")

    def _validate_file_permissions(self):
        """Validate file and directory permissions"""
        sensitive_files = [".env", "secrets.json", "security_audit.log", "sifu.log"]

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
            f"Status: {'✅ VALID' if success else '❌ INVALID'}",
            f"Errors: {len(errors)}",
            f"Warnings: {len(warnings)}",
            "",
        ]

        if errors:
            report_lines.extend(
                [
                    "❌ ERRORS:",
                    "-" * 20,
                ]
            )
            report_lines.extend(f"  • {error}" for error in errors)
            report_lines.append("")

        if warnings:
            report_lines.extend(
                [
                    "⚠️  WARNINGS:",
                    "-" * 20,
                ]
            )
            report_lines.extend(f"  • {warning}" for warning in warnings)
            report_lines.append("")

        if success:
            report_lines.extend(
                [
                    "✅ CONFIGURATION VALID",
                    "All security checks passed. Application is ready to start.",
                ]
            )
        else:
            report_lines.extend(
                [
                    "❌ CONFIGURATION INVALID",
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
            print(f"❌ {error}")
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
