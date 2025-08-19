"""Main application entry point module.

This module serves as the primary entry point for running the Flask text
transformation application directly (not through a WSGI server). It handles
configuration detection, environment setup, and server startup.
"""

# Set up basic logging for main entry point
import logging
import os

from app import create_app
from app.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


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
    config_name = os.environ.get("FLASK_ENV", "development")
    logger.info(f"Starting application with config: {config_name}")
    logger.info(f"Log level: {os.environ.get('LOG_LEVEL', 'default')}")

    try:
        if os.environ.get("DYNO"):  # Running on Heroku
            from heroku_config import HerokuConfig

            config["heroku"] = HerokuConfig
            config_name = "heroku"
            logger.info("Detected Heroku environment, using Heroku config")

        app = create_app(config[config_name])

        port = int(os.environ.get("PORT", 5000))
        debug = config_name == "development"

        logger.info(f"Starting server on port: {port}")
        logger.info(f"Debug mode: {debug}")

        app.run(host="0.0.0.0", port=port, debug=debug)  # noqa: S104  # Development server

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        exit(1)


if __name__ == "__main__":
    main()
