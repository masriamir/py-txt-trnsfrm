"""Main application entry point module.

This module serves as the primary entry point for running the Flask text
transformation application directly (not through a WSGI server). It handles
configuration detection, environment setup, and server startup.
"""

# Load environment variables from .env file before any other imports
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not available, skip loading
    pass

# Set up centralized logging for main entry point

from app import create_app
from app.config import config, get_host_for_environment
from app.env_config import (
    get_flask_env,
    get_logging_config,
    get_port,
    is_heroku_environment,
    FlaskEnvironment,
)
from app.logging_config import get_logger, setup_logging

# Initialize logging using centralized environment configuration
logging_config = get_logging_config()
setup_logging(logging_config)

# Get logger for main startup
logger = get_logger("main")


def main():
    """Entry point for running the Flask application directly.

    Detects the appropriate configuration based on environment variables,
    handles Heroku-specific setup if needed, creates the Flask application
    instance, and starts the development server.

    Environment Variables:
        FLASK_ENV: Configuration environment ('development', 'production', etc.)
        LOG_LEVEL: Logging level ('debug', 'info', 'warning', 'error', 'critical')
        PORT: Port number to run the server on (defaults to 5000)
        DYNO: Heroku environment indicator

    Raises:
        SystemExit: If configuration fails or an unhandled exception occurs.

    Example:
        Run the application directly:
            $ python app.py

        Run with specific configuration:
            $ FLASK_ENV=production LOG_LEVEL=info python app.py
    """
    config_name = get_flask_env()
    logger.info(f"Starting application with config: {config_name}")
    logger.info(f"Log level: {logging_config.log_level}")

    try:
        if is_heroku_environment():  # Running on Heroku
            from heroku_config import HerokuConfig

            config["heroku"] = HerokuConfig
            config_name = "heroku"
            logger.info("Detected Heroku environment, using Heroku config")

        app = create_app(config[config_name])

        port = get_port()
        debug = config_name == FlaskEnvironment.DEVELOPMENT
        host = get_host_for_environment(config_name)

        logger.info(f"Starting server on host: {host}, port: {port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Environment: {config_name}")

        app.run(
            host=host, port=port, debug=debug
        )  # Conditional host binding for security - see get_host_for_environment()

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        exit(1)


if __name__ == "__main__":
    main()
