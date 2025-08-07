import os
from typing import Type


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    TESTING = False

    @classmethod
    def init_app(cls, app):
        """Initialize application with this config."""
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        """Initialize production app and validate required settings."""
        Config.init_app(app)

        # Validate that SECRET_KEY is set in production
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("No SECRET_KEY set for production environment")

        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


config: dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  # Changed default to DevelopmentConfig
}
