#!/usr/bin/env python3
"""
Secure application startup script
Validates configuration and starts SIFU with security checks
"""
import os
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_secure_logging():
    """Setup basic logging before configuration validation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main startup function with security validation"""
    setup_secure_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 Starting SIFU with security validation...")

        # Step 1: Validate configuration and secrets
        logger.info("📋 Validating configuration...")
        from config_validator import validate_configuration_on_startup
        config_valid = validate_configuration_on_startup()

        if not config_valid:
            logger.error("❌ Configuration validation failed")
            logger.error("Please fix the configuration issues above and try again")
            sys.exit(1)

        # Step 2: Load and validate secrets
        logger.info("🔐 Loading secrets...")
        from secret_manager import secret_manager
        secrets = secret_manager.load_secrets()
        is_valid, validation_errors = secret_manager.validate_secrets()

        if not is_valid:
            logger.error("❌ Secret validation failed:")
            for error in validation_errors:
                logger.error(f"  • {error}")
            sys.exit(1)

        # Step 3: Generate .env template if needed
        if not Path('.env').exists():
            logger.info("📄 Generating .env template...")
            secret_manager.save_env_template()

        # Step 4: Initialize secure logging
        logger.info("📊 Initializing secure logging...")
        from secure_logging import init_security_logging
        security_config = secret_manager.get_security_config()
        # Ensure logs directory exists
        logs_dir = Path('logs')
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.warning("Could not create 'logs' directory; falling back to current directory")
            logs_dir = Path('.')

        security_logger = init_security_logging({
            'log_level': security_config['log_level'],
            'log_file': str(logs_dir / 'sifu.log'),
            'audit_logging_enabled': security_config['audit_logging_enabled'],
            'encrypt_logs': secret_manager.should_encrypt_logs(),
            'log_encryption_key': secrets.get('LOG_ENCRYPTION_KEY'),
            'max_log_size': 100 * 1024 * 1024,  # 100MB
            'log_backup_count': 5,
        })

        # Log successful validation
        security_logger.log_security_event(
            'STARTUP_VALIDATION',
            'Configuration and secrets validated successfully',
            extra_data={
                'secrets_loaded': len(secrets),
                'environment': security_config['environment']
            }
        )

        logger.info("✅ Security validation completed successfully")
        logger.info("🌐 Starting FastAPI application...")

        # Step 5: Start the FastAPI application
        import uvicorn

        # Get server configuration from environment
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', '8000'))
        reload = os.getenv('RELOAD', 'false').lower() == 'true'

        logger.info(f"📡 Starting server on {host}:{port} (reload={reload})")

        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=security_config['log_level'].lower()
        )

    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"💥 Startup failed: {e}")
        # Log security event for failed startup
        try:
            from secure_logging import get_security_logger
            security_logger = get_security_logger()
            if security_logger:
                security_logger.log_security_event('STARTUP_FAILURE', f'Application startup failed: {str(e)}')
        except Exception:
            pass  # Ignore logging errors during startup failure
        sys.exit(1)

if __name__ == "__main__":
    main()
