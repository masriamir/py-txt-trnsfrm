from flask import Flask
from app.config import Config
from app.logging_config import setup_logging, get_logger


def create_app(config_class=None):
    """Application factory pattern."""
    app = Flask(__name__)

    # Use default config if none provided
    if config_class is None:
        from app.config import config
        import os
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
