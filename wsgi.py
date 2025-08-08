"""
WSGI entry point for Heroku deployment.
This file is separate from app.py to avoid any conflicts.
"""
import os
import sys
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up basic logging for WSGI initialization (before app logging is configured)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] WSGI: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('wsgi')

logger.info("=== WSGI Initialization Starting ===")
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f"Python path: {sys.path[:3]}")  # Show first 3 entries
logger.info("Environment variables:")
logger.info(f"  DYNO: {os.environ.get('DYNO', 'Not set')}")
logger.info(f"  FLASK_CONFIG: {os.environ.get('FLASK_CONFIG', 'Not set')}")
logger.info(f"  SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")

try:
    logger.info("Importing application configuration...")
    from app.config import config
    logger.info("✓ Config imported successfully")

    # Determine configuration
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    logger.info(f"Using config: {config_name}")

    # Special handling for Heroku
    if os.environ.get('DYNO'):  # DYNO env var indicates Heroku
        logger.info("Detected Heroku environment")
        config_name = 'heroku'
        try:
            from heroku_config import HerokuConfig
            config['heroku'] = HerokuConfig
            logger.info("✓ Heroku config loaded")
        except Exception as e:
            logger.warning(f"Failed to load Heroku config: {e}")
            # Fallback to production config
            config_name = 'production'
            logger.info("Falling back to production config")

    logger.info("Creating Flask application...")
    from app import create_app
    app = create_app(config[config_name])
    logger.info("✓ Flask app created successfully")

    # Test that the app works
    with app.app_context():
        logger.info(f"✓ App context working. Debug mode: {app.debug}")

    logger.info("=== WSGI Setup Complete ===")

except Exception as e:
    logger.error(f"Error during WSGI setup: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    # Create a minimal app as fallback
    logger.warning("Creating minimal fallback Flask app")
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def error():
        return "Application failed to initialize properly. Check logs for details.", 500

# Ensure app is available for WSGI server
if __name__ == "__main__":
    logger.info("Running application directly (testing production config)")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
