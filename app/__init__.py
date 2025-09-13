"""Flask application factory module.

This module contains the Flask application factory function that creates and configures
the Flask application instance with all necessary components including logging,
middleware, and blueprints.
"""

# Load environment variables from .env file before any other imports
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not available, skip loading
    pass

from typing import Type

from flask import Flask

from app.config import Config, config
from app.env_config import FlaskEnvironment, get_flask_env, get_logging_config
from app.logging_config import get_logger, setup_logging
from app.main import bp as main_bp
from app.middleware import setup_request_logging


def create_app(config_class: Type[Config] | None = None) -> Flask:
    """Create and configure Flask application instance.

    This function implements the application factory pattern, creating a Flask
    application with all necessary configuration, logging, middleware, and blueprints.

    Args:
        config_class: Configuration class to use. If None, determines config from
            FLASK_ENV environment variable (defaults to FlaskEnvironment.DEVELOPMENT).

    Returns:
        Flask: Configured Flask application instance.

    Example:
        >>> from app import create_app
        >>> app = create_app()
        >>> app.run()
    """
    app = Flask(__name__)

    # Use default config if none provided
    if config_class is None:
        config_env = get_flask_env()
        config_class = config.get(config_env, config[FlaskEnvironment.DEVELOPMENT])

    app.config.from_object(config_class)

    # Initialize logging using centralized environment configuration
    logging_config = get_logging_config()
    setup_logging(logging_config)

    logger = get_logger(__name__)
    logger.info(f"Starting application with config: {config_class.__name__}")
    logger.info(f"Log level: {logging_config.log_level}")
    logger.debug(f"Debug mode: {logging_config.debug_mode}")

    # Initialize the config (this will validate production settings if needed)
    config_class.init_app(app)

    # Set up request logging middleware
    setup_request_logging(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    logger.info("Application blueprints registered successfully")

    # Log application startup completion
    logger.info("Flask application initialization complete")

    return app
