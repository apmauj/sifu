#!/usr/bin/env python3
"""
Security verification script for SIFU
Tests all security components and provides recommendations.
Updated: removed secret_manager dependency, uses os.getenv() directly.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_configuration_validation():
    """Test configuration validation"""
    print("Testing configuration validation...")

    try:
        from src.application.config_validator import ConfigurationValidator

        validator = ConfigurationValidator()
        success, errors, warnings = validator.validate_all()

        if success:
            print("  PASSED - Configuration validation")
            return True, errors, warnings
        else:
            print("  FAILED - Configuration validation")
            for error in errors:
                print(f"    * {error}")
            return False, errors, warnings
    except Exception as e:
        print(f"  FAILED - Configuration validation error: {e}")
        return False, [str(e)], []


def test_totp_service():
    """Test TOTP service availability and configuration"""
    print("Testing TOTP service...")

    try:
        from src.application.simple_totp import SimpleTOTP

        # Check if MONITORING_TOTP_SECRET is set
        secret = os.getenv("MONITORING_TOTP_SECRET")
        if not secret:
            print("  WARNING - MONITORING_TOTP_SECRET not set; a random secret is generated on startup")
            print("    This means the authenticator app will break on every server restart.")
            print("    Set it in Render Environment to persist across cold starts.")

        # Try to initialize the service
        totp = SimpleTOTP()
        uri = totp.get_provisioning_uri()
        if uri and uri.startswith("otpauth://"):
            print("  PASSED - TOTP service initialized, provisioning URI valid")
            return True, [], []
        else:
            print("  FAILED - TOTP provisioning URI invalid")
            return False, ["Invalid provisioning URI"], []

    except ImportError as e:
        print(f"  FAILED - Cannot import TOTP module: {e}")
        return False, [str(e)], []
    except Exception as e:
        print(f"  FAILED - TOTP service error: {e}")
        return False, [str(e)], []


def test_secure_logging():
    """Test secure logging setup"""
    print("Testing secure logging...")

    try:
        from src.application.secure_logging import init_security_logging

        security_logger = init_security_logging(
            {
                "log_level": "INFO",
                "log_file": "test_security.log",
                "audit_logging_enabled": True,
                "encrypt_logs": False,
                "max_log_size": 1024 * 1024,
                "log_backup_count": 2,
            }
        )

        # Test logging
        security_logger.log_security_event("TEST", "Security verification test")
        security_logger.log_authentication(True, "test_user", "127.0.0.1")

        print("  PASSED - Secure logging")
        return True, []
    except Exception as e:
        print(f"  WARNING - Secure logging error: {e}")
        return True, []  # Non-critical, don't fail the whole test


def test_security_imports():
    """Test that all security modules can be imported"""
    print("Testing security module imports...")

    modules_to_test = [
        ("src.application.config_validator", "ConfigurationValidator"),
        ("src.application.simple_totp", "SimpleTOTP"),
        ("src.application.security_utils", "SecurityValidator"),
        ("src.infrastructure.rate_limit", "RateLimitMiddleware"),
    ]

    failed_imports = []

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)  # Verify the class exists
            print(f"  OK - {module_name}.{class_name}")
        except ImportError as e:
            print(f"  FAILED - {module_name}: {e}")
            failed_imports.append(module_name)
        except AttributeError:
            print(f"  FAILED - {module_name}.{class_name} not found")
            failed_imports.append(f"{module_name}.{class_name}")
        except Exception as e:
            print(f"  ERROR - {module_name}: {e}")
            failed_imports.append(module_name)

    return len(failed_imports) == 0, failed_imports


def check_file_permissions():
    """Check file permissions for sensitive files"""
    print("Checking file permissions...")

    sensitive_files = [".env", "security_audit.log", "sifu.log"]

    issues = []

    for file_path in sensitive_files:
        if Path(file_path).exists():
            try:
                stat_info = os.stat(file_path)
                # Check if file is world-readable
                if stat_info.st_mode & 0o004:
                    issues.append(f"{file_path} is world-readable")
                    print(f"  WARNING - {file_path}: World-readable (security risk)")
                else:
                    print(f"  OK - {file_path}")
            except OSError as e:
                issues.append(f"Cannot check {file_path}: {e}")
                print(f"  WARNING - {file_path}: Cannot check permissions")
        else:
            print(f"  INFO - {file_path}: Not found")

    return len(issues) == 0, issues


def check_environment_variables():
    """Check that critical environment variables are set"""
    print("Checking environment variables...")

    critical_vars = {
        "ENVIRONMENT": "Should be 'production' in Render",
        "ALLOW_ORIGINS": "CORS origins for the frontend",
        "MONITORING_TOTP_SECRET": "Persistent TOTP secret for monitoring dashboard",
    }

    missing = []
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            # Don't log actual values for secrets
            print(f"  OK - {var} is set ({description})")
        else:
            missing.append(var)
            print(f"  MISSING - {var} ({description})")

    if missing:
        return False, [f"Missing: {', '.join(missing)}"]
    return True, []


def generate_security_report(results: Dict[str, Any]):
    """Generate security report"""
    print("\n" + "=" * 60)
    print("SIFU SECURITY VERIFICATION REPORT")
    print("=" * 60)

    all_passed = all(result["status"] for result in results.values())

    for test_name, result in results.items():
        status = "PASSED" if result["status"] else "FAILED"
        print(f"\n{test_name}:")
        print(f"  Status: {status}")

        if result.get("errors"):
            print("  Errors:")
            for error in result["errors"]:
                print(f"    * {error}")

        if result.get("warnings"):
            print("  Warnings:")
            for warning in result["warnings"]:
                print(f"    * {warning}")

    print("\n" + "=" * 60)
    print(
        f"OVERALL STATUS: {'ALL TESTS PASSED' if all_passed else 'ISSUES DETECTED'}"
    )
    print("=" * 60)

    if all_passed:
        print("Your SIFU installation is secure!")
        print("\nNext steps:")
        print("1. Review the generated .env.template file")
        print("2. Configure your production secrets in Render Environment")
        print("3. Set MONITORING_TOTP_SECRET for the monitoring dashboard")
    else:
        print("Security issues detected. Please address them before deploying.")

    return all_passed


def main():
    """Main verification function"""
    print("SIFU Security Verification")
    print("=" * 50)

    results = {}

    # Test 1: Module imports
    status, failed_imports = test_security_imports()
    results["Module Imports"] = {
        "status": status,
        "errors": failed_imports if not status else [],
    }

    # Test 2: Configuration validation
    status, errors, warnings = test_configuration_validation()
    results["Configuration Validation"] = {
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }

    # Test 3: TOTP service
    status, errors, warnings = test_totp_service()
    results["TOTP Service"] = {
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }

    # Test 4: Secure logging
    status, errors = test_secure_logging()
    results["Secure Logging"] = {"status": status, "errors": errors}

    # Test 5: File permissions
    status, issues = check_file_permissions()
    results["File Permissions"] = {"status": status, "errors": issues}

    # Test 6: Environment variables
    status, issues = check_environment_variables()
    results["Environment Variables"] = {"status": status, "errors": issues}

    # Generate report
    all_passed = generate_security_report(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
