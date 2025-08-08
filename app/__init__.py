"""Flask application factory module.

This module contains the Flask application factory function that creates and configures
the Flask application instance with all necessary components including logging,
middleware, and blueprints.
"""
from flask import Flask

from app.config import Config
from app.logging_config import get_logger, setup_logging


def create_app(config_class=None):
    """Create and configure Flask application instance.

    This function implements the application factory pattern, creating a Flask
    application with all necessary configuration, logging, middleware, and blueprints.

    Args:
        config_class: Configuration class to use. If None, determines config from
            FLASK_CONFIG environment variable (defaults to 'development').

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
        import os

        from app.config import config
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        config_class = config[config_name]

    app.config.from_object(config_class)

    # Initialize logging based on DEBUG setting
    setup_logging(debug=app.config.get('DEBUG', False))
    logger = get_logger(__name__)
    logger.info(f"Starting application with config: {config_class.__name__}")
    logger.debug(f"Debug mode: {app.config.get('DEBUG', False)}")

    # Initialize the config (this will validate production settings if needed)
    config_class.init_app(app)

    # Set up request logging middleware
    from app.middleware import setup_request_logging
    setup_request_logging(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    logger.info("Application blueprints registered successfully")

    # Log application startup completion
    logger.info("Flask application initialization complete")

    return app
