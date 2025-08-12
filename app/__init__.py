"""Flask application factory module.

This module contains the Flask application factory function that creates and configures
the Flask application instance with all necessary components including logging,
middleware, and blueprints.
"""
import os

from flask import Flask

from app.config import config
from app.logging_config import get_logger, setup_logging
from app.main import bp as main_bp
from app.middleware import setup_request_logging


def create_app(config_class=None):
    """Create and configure Flask application instance.

    This function implements the application factory pattern, creating a Flask
    application with all necessary configuration, logging, middleware, and blueprints.

    Args:
        config_class: Configuration class to use. If None, determines config from
            FLASK_ENV environment variable (defaults to 'development').

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
        config_name = os.environ.get('FLASK_ENV', 'development')
        config_class = config.get(config_name, config['development'])

    app.config.from_object(config_class)

    # Initialize logging based on LOG_LEVEL environment variable
    # LOG_LEVEL takes precedence over DEBUG setting for logging configuration
    log_level_env = os.environ.get('LOG_LEVEL', '').upper()
    if log_level_env in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        debug_mode = log_level_env == 'DEBUG'
        setup_logging(debug=debug_mode, log_level=log_level_env)
    else:
        # Fall back to Flask config DEBUG setting if LOG_LEVEL is not set or invalid
        debug_mode = app.config.get('DEBUG', False)
        setup_logging(debug=debug_mode, log_level='DEBUG' if debug_mode else 'INFO')

    logger = get_logger(__name__)
    logger.info(f"Starting application with config: {config_class.__name__}")
    logger.info(f"Log level: {log_level_env if log_level_env else ('DEBUG' if debug_mode else 'INFO')}")
    logger.debug(f"Debug mode: {debug_mode}")

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
