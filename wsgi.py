#!/usr/bin/env python3
"""
WSGI entry point for the Flask application.
This file is used by Gunicorn to serve the application in production environments.
It handles environment detection and proper configuration selection.
"""

# Load environment variables from .env file before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, skip loading
    pass

import os
import platform
import sys
from pathlib import Path

# Add the current directory to the Python path before any local imports
sys.path.insert(0, str(Path(__file__).parent))

# Standard library and third-party imports first
# Local imports after sys.path manipulation
from app import create_app
from app.config import config
from app.logging_config import get_logger, setup_logging

# Initialize logging based on LOG_LEVEL environment variable
log_level = os.environ.get("LOG_LEVEL", "info").lower()
debug_mode = log_level == "debug"
setup_logging(debug=debug_mode, log_level=log_level.upper())

# Get logger for WSGI startup
logger = get_logger("wsgi")

# 🚀 Log startup banner with detailed system information
logger.info("=" * 60)
logger.info("🚀 Starting py-txt-trnsfrm Flask Application")
logger.info("=" * 60)

# Detect environment and select appropriate configuration
config_name = os.environ.get("FLASK_ENV", "production")

# Log configuration details
logger.info("📋 Configuration Details:")
logger.info(f"   • Environment: {config_name}")
logger.info(f"   • Log Level: {log_level}")
logger.info(f"   • Port: {os.environ.get('PORT', '5000')}")
logger.info(f"   • Workers: {os.environ.get('WEB_CONCURRENCY', 'auto')}")

# Log system information for debugging
logger.info("🖥️  System Information:")
logger.info(f"   • Python Version: {platform.python_version()}")
logger.info(f"   • Python Implementation: {platform.python_implementation()}")
logger.info(f"   • Python Executable: {sys.executable}")
logger.info(f"   • Platform: {platform.platform()}")
logger.info(f"   • Architecture: {platform.machine()}")
logger.info(f"   • Working Directory: {Path.cwd()}")
logger.info(f"   • WSGI File Path: {Path(__file__).resolve()}")

# Log Python path information (debug only)
if debug_mode:
    logger.debug("🔍 Python Path Details:")
    for i, path in enumerate(sys.path[:10]):  # Show first 10 paths
        logger.debug(f"   [{i}] {path}")
    if len(sys.path) > 10:
        logger.debug(f"   ... and {len(sys.path) - 10} more paths")

# Log environment variables (debug only, exclude sensitive ones)
if debug_mode:
    logger.debug("🌍 Environment Variables:")
    sensitive_vars = {"SECRET_KEY", "DATABASE_URL", "API_KEY", "PASSWORD", "TOKEN"}
    for key, value in sorted(os.environ.items()):
        if any(sensitive in key.upper() for sensitive in sensitive_vars):
            logger.debug(f"   • {key}: [REDACTED]")
        else:
            logger.debug(f"   • {key}: {value}")

# Handle Heroku-specific configuration if running on Heroku
if os.environ.get("DYNO"):  # Running on Heroku
    try:
        # Import here is necessary because heroku_config may not exist in all deployments
        from heroku_config import HerokuConfig

        config["heroku"] = HerokuConfig
        config_name = "heroku"
        logger.info("☁️  Detected Heroku environment, using Heroku config")
        logger.info(f"   • Dyno: {os.environ.get('DYNO')}")
        logger.info(f"   • Dyno RAM: {os.environ.get('WEB_MEMORY', 'unknown')}")
    except ImportError as e:
        logger.warning(f"⚠️  Warning: Could not import HerokuConfig: {e}")
        logger.info("🔄 Falling back to production config")
        config_name = "production"

# Log additional deployment information
logger.info("🚀 Deployment Information:")
logger.info(f"   • Container: {'Yes' if Path('/.dockerenv').exists() else 'No'}")
logger.info(
    f"   • Kubernetes: {'Yes' if os.environ.get('KUBERNETES_SERVICE_HOST') else 'No'}"
)
logger.info(f"   • Cloud Run: {'Yes' if os.environ.get('K_SERVICE') else 'No'}")
logger.info(
    f"   • AWS Lambda: {'Yes' if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') else 'No'}"
)

# Create the Flask application instance with appropriate configuration
try:
    logger.info(f"⚙️  Creating Flask application with {config_name} configuration...")

    # Log memory usage before application creation (if psutil is available)
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        logger.info(
            f"💾 Memory Usage (before app creation): {memory_info.rss / 1024 / 1024:.1f} MB"
        )
    except ImportError:
        logger.debug("📊 psutil not available, skipping memory information")

    application = create_app(config.get(config_name, config["production"]))

    # Log memory usage after application creation
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        logger.info(
            f"💾 Memory Usage (after app creation): {memory_info.rss / 1024 / 1024:.1f} MB"
        )
    except ImportError:
        pass

    logger.info("✅ WSGI application created successfully!")
    logger.info("🎯 Ready to serve requests")
    logger.info("=" * 60)

except Exception as e:
    logger.error(f"❌ Error creating WSGI application: {e}")
    logger.error("🔍 Traceback details:", exc_info=True)
    logger.error("=" * 60)
    # Re-raise the exception - let Gunicorn handle the failure
    raise

if __name__ == "__main__":
    # For development/testing when running wsgi.py directly
    logger.info("🧪 Running WSGI application directly (development mode)")
    application.run(
        host="0.0.0.0",  # noqa: S104  # Development server
        port=int(os.environ.get("PORT", 5000)),
        debug=config_name == "development",
    )
