#!/usr/bin/env python3
"""
Security verification script for SIFU
Tests all security components and provides recommendations
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_configuration_validation():
    """Test configuration validation"""
    print("🔍 Testing configuration validation...")

    try:
        from config_validator import ConfigurationValidator
        validator = ConfigurationValidator()
        success, errors, warnings = validator.validate_all()

        if success:
            print("✅ Configuration validation: PASSED")
            return True, errors, warnings
        else:
            print("❌ Configuration validation: FAILED")
            for error in errors:
                print(f"   • {error}")
            return False, errors, warnings
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False, [str(e)], []

def test_secret_management():
    """Test secret management"""
    print("🔐 Testing secret management...")

    try:
        from secret_manager import secret_manager
        secrets = secret_manager.load_secrets()
        is_valid, validation_errors = secret_manager.validate_secrets()

        if is_valid:
            print("✅ Secret management: PASSED")
            print(f"   • Loaded {len(secrets)} secrets")
            return True, validation_errors
        else:
            print("❌ Secret management: FAILED")
            for error in validation_errors:
                print(f"   • {error}")
            return False, validation_errors
    except Exception as e:
        print(f"❌ Secret management error: {e}")
        return False, [str(e)]

def test_secure_logging():
    """Test secure logging setup"""
    print("📊 Testing secure logging...")

    try:
        from secure_logging import init_security_logging, get_security_logger
        from secret_manager import secret_manager

        security_config = secret_manager.get_security_config()
        security_logger = init_security_logging({
            'log_level': 'INFO',
            'log_file': 'test_security.log',
            'audit_logging_enabled': True,
            'encrypt_logs': False,
            'max_log_size': 1024 * 1024,
            'log_backup_count': 2,
        })

        # Test logging
        security_logger.log_security_event('TEST', 'Security verification test')
        security_logger.log_authentication(True, 'test_user', '127.0.0.1')

        print("✅ Secure logging: PASSED")
        return True, []
    except Exception as e:
        print(f"❌ Secure logging error: {e}")
        return False, [str(e)]

def test_security_imports():
    """Test that all security modules can be imported"""
    print("📦 Testing security module imports...")

    modules_to_test = [
        'secret_manager',
        'secure_logging',
        'config_validator',
        'pydantic_models',
        'security_utils',
        'rate_limit'
    ]

    failed_imports = []

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: FAILED - {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"⚠️  {module}: ERROR - {e}")
            failed_imports.append(module)

    return len(failed_imports) == 0, failed_imports

def check_file_permissions():
    """Check file permissions for sensitive files"""
    print("🔒 Checking file permissions...")

    sensitive_files = [
        '.env',
        'secrets.json',
        'security_audit.log',
        'sifu.log'
    ]

    issues = []

    for file_path in sensitive_files:
        if Path(file_path).exists():
            try:
                stat_info = os.stat(file_path)
                # Check if file is world-readable
                if stat_info.st_mode & 0o004:
                    issues.append(f"{file_path} is world-readable")
                    print(f"⚠️  {file_path}: World-readable (security risk)")
                else:
                    print(f"✅ {file_path}: OK")
            except OSError as e:
                issues.append(f"Cannot check {file_path}: {e}")
                print(f"⚠️  {file_path}: Cannot check permissions")
        else:
            print(f"ℹ️  {file_path}: Not found")

    return len(issues) == 0, issues

def generate_security_report(results: Dict[str, Any]):
    """Generate security report"""
    print("\n" + "="*60)
    print("🛡️  SIFU SECURITY VERIFICATION REPORT")
    print("="*60)

    all_passed = all(result['status'] for result in results.values())

    for test_name, result in results.items():
        status = "✅ PASSED" if result['status'] else "❌ FAILED"
        print(f"\n{test_name}:")
        print(f"  Status: {status}")

        if result.get('errors'):
            print("  Errors:")
            for error in result['errors']:
                print(f"    • {error}")

        if result.get('warnings'):
            print("  Warnings:")
            for warning in result['warnings']:
                print(f"    • {warning}")

        if result.get('details'):
            for key, value in result['details'].items():
                print(f"    {key}: {value}")

    print("\n" + "="*60)
    print(f"OVERALL STATUS: {'✅ ALL TESTS PASSED' if all_passed else '❌ ISSUES DETECTED'}")
    print("="*60)

    if all_passed:
        print("🎉 Your SIFU installation is secure!")
        print("\nNext steps:")
        print("1. Review the generated .env.template file")
        print("2. Configure your production secrets")
        print("3. Run: python start_secure.py")
    else:
        print("⚠️  Security issues detected. Please address them before deploying.")

    return all_passed

def main():
    """Main verification function"""
    print("🛡️  SIFU Security Verification")
    print("="*50)

    results = {}

    # Test 1: Module imports
    status, failed_imports = test_security_imports()
    results["Module Imports"] = {
        'status': status,
        'errors': failed_imports if not status else [],
        'details': {'failed_modules': failed_imports} if not status else {}
    }

    # Test 2: Configuration validation
    status, errors, warnings = test_configuration_validation()
    results["Configuration Validation"] = {
        'status': status,
        'errors': errors,
        'warnings': warnings
    }

    # Test 3: Secret management
    status, errors = test_secret_management()
    results["Secret Management"] = {
        'status': status,
        'errors': errors
    }

    # Test 4: Secure logging
    status, errors = test_secure_logging()
    results["Secure Logging"] = {
        'status': status,
        'errors': errors
    }

    # Test 5: File permissions
    status, issues = check_file_permissions()
    results["File Permissions"] = {
        'status': status,
        'errors': issues
    }

    # Generate report
    all_passed = generate_security_report(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
