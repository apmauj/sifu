#!/usr/bin/env python3
"""
Security verification script for SIFU
Tests security components and provides recommendations

Adapted for Render deployment: uses os.getenv() directly instead of secret_manager.
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
            print("  Configuration validation: PASSED")
            return True, errors, warnings
        else:
            print("  Configuration validation: FAILED")
            for error in errors:
                print(f"   - {error}")
            return False, errors, warnings
    except Exception as e:
        print(f"  Configuration validation error: {e}")
        return False, [str(e)], []


def test_environment_variables():
    """Test critical environment variables"""
    print("Testing environment variables...")

    critical_vars = ["ENVIRONMENT", "ALLOW_ORIGINS"]
    recommended_vars = ["MONITORING_TOTP_SECRET", "JWT_SECRET_KEY"]

    missing_critical = [v for v in critical_vars if not os.getenv(v)]
    missing_recommended = [v for v in recommended_vars if not os.getenv(v)]

    errors = []
    if missing_critical:
        errors.append(f"Missing critical env vars: {', '.join(missing_critical)}")

    if missing_recommended:
        errors.append(f"Missing recommended env vars: {', '.join(missing_recommended)}")

    if errors:
        for error in errors:
            print(f"  - {error}")
        return False, errors

    print("  Environment variables: PASSED")
    return True, []


def test_secure_logging():
    """Test secure logging setup"""
    print("Testing secure logging...")

    try:
        from src.infrastructure.secure_logging import init_security_logging

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

        print("  Secure logging: PASSED")
        return True, []
    except Exception as e:
        print(f"  Secure logging error: {e}")
        return False, [str(e)]


def test_security_imports():
    """Test that security modules can be imported"""
    print("Testing security module imports...")

    modules_to_test = [
        ("src.application.config_validator", "config_validator"),
        ("src.application.security_utils", "security_utils"),
        ("src.infrastructure.rate_limit", "rate_limit"),
        ("src.application.simple_totp", "simple_totp"),
    ]

    failed_imports = []

    for module_path, display_name in modules_to_test:
        try:
            __import__(module_path)
            print(f"  {display_name}: OK")
        except ImportError as e:
            print(f"  {display_name}: FAILED - {e}")
            failed_imports.append(display_name)
        except Exception as e:
            print(f"  {display_name}: ERROR - {e}")
            failed_imports.append(display_name)

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
                    print(f"  {file_path}: World-readable (security risk)")
                else:
                    print(f"  {file_path}: OK")
            except OSError as e:
                issues.append(f"Cannot check {file_path}: {e}")
                print(f"  {file_path}: Cannot check permissions")
        else:
            print(f"  {file_path}: Not found")

    return len(issues) == 0, issues


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
                print(f"    - {error}")

        if result.get("warnings"):
            print("  Warnings:")
            for warning in result["warnings"]:
                print(f"    - {warning}")

    print("\n" + "=" * 60)
    print(
        f"OVERALL STATUS: {'ALL TESTS PASSED' if all_passed else 'ISSUES DETECTED'}"
    )
    print("=" * 60)

    if all_passed:
        print("SIFU installation is secure!")
        print("\nNext steps:")
        print("1. Review environment variables in Render Dashboard")
        print("2. Set MONITORING_TOTP_SECRET for TOTP dashboard access")
        print("3. Set JWT_SECRET_KEY for authentication features")
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

    # Test 3: Environment variables
    status, errors = test_environment_variables()
    results["Environment Variables"] = {"status": status, "errors": errors}

    # Test 4: Secure logging
    status, errors = test_secure_logging()
    results["Secure Logging"] = {"status": status, "errors": errors}

    # Test 5: File permissions
    status, issues = check_file_permissions()
    results["File Permissions"] = {"status": status, "errors": issues}

    # Generate report
    all_passed = generate_security_report(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
