from flask import Flask
from app.config import Config


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

    # Initialize the config (this will validate production settings if needed)
    config_class.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
