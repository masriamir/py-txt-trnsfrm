"""Flask application configuration module.

This module contains configuration classes for different deployment environments
(development, testing, production) and provides a centralized way to manage
application settings and environment-specific configurations.
"""

import os


class Config:
    """Base configuration class with common settings.

    This class contains configuration settings that are common to all environments.
    Environment-specific configuration classes inherit from this base class.

    Attributes:
        SECRET_KEY: Secret key for Flask sessions and CSRF protection.
        DEBUG: Debug mode flag, defaults to False for security.
        TESTING: Testing mode flag, defaults to False.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Flask settings
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    TESTING = False

    @classmethod
    def init_app(cls, app):
        """Initialize application with this configuration.

        Args:
            app: Flask application instance to configure.
        """
        pass


class DevelopmentConfig(Config):
    """Development environment configuration.

    Configuration optimized for local development with debugging enabled
    and relaxed security settings for ease of development.
    """

    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"


class TestConfig(Config):
    """Testing environment configuration.

    Configuration optimized for running automated tests with testing mode
    enabled and CSRF protection disabled for easier testing.
    """

    TESTING = True
    SECRET_KEY = "test-secret-key"  # noqa: S105  # Test configuration only
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration.

    Configuration optimized for production deployment with security
    hardening and environment validation.
    """

    DEBUG = False

    @classmethod
    def init_app(cls, app):
        """Initialize production application and validate required settings.

        Validates that all required production settings are properly configured
        and logs the initialization process.

        Args:
            app: Flask application instance to configure.

        Raises:
            ValueError: If SECRET_KEY is not set in production environment.
        """
        Config.init_app(app)

        from app.logging_config import get_logger

        logger = get_logger("config")

        # Validate that SECRET_KEY is set in production
        if not os.environ.get("SECRET_KEY"):
            logger.critical("No SECRET_KEY set for production environment")
            raise ValueError("No SECRET_KEY set for production environment")

        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
        logger.info("Production configuration initialized successfully")


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
}
