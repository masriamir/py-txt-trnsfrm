"""Flask application configuration module.

This module contains configuration classes for different deployment environments
(development, testing, production) and provides a centralized way to manage
application settings and environment-specific configurations.
"""

import os
from typing import TYPE_CHECKING, Type

from app.env_config import FlaskEnvironment

if TYPE_CHECKING:
    from flask import Flask


def get_host_for_environment(config_name: str | FlaskEnvironment) -> str:
    """Determine the appropriate host address based on the deployment environment.

    Returns '0.0.0.0' for production environments to allow external access,
    and '127.0.0.1' for development environments for security.

    This follows security best practices by:
    - Restricting network exposure in development environments
    - Only binding to all interfaces when explicitly in production
    - Preventing accidental exposure of development servers

    Args:
        config_name: The configuration environment name (str or FlaskEnvironment enum)
                    e.g., 'development', FlaskEnvironment.PRODUCTION, etc.

    Returns:
        str: Host address to bind to ('127.0.0.1' for dev, '0.0.0.0' for production)

    Production environments (bind to 0.0.0.0):
        - config_name == "production" or FlaskEnvironment.PRODUCTION
        - config_name == "heroku" (legacy string support)
        - DYNO environment variable is set (Heroku detection)

    Development environments (bind to 127.0.0.1):
        - config_name == "development" or FlaskEnvironment.DEVELOPMENT
        - config_name == "testing" or FlaskEnvironment.TESTING
        - All other environments
    """
    # Check for Heroku environment first (most specific)
    if os.environ.get("DYNO"):
        return "0.0.0.0"  # noqa: S104  # Intentional production binding

    # Handle FlaskEnvironment enum values
    if isinstance(config_name, FlaskEnvironment):
        if config_name in {FlaskEnvironment.PRODUCTION}:
            return "0.0.0.0"  # noqa: S104  # Intentional production binding
    else:
        # Handle legacy string values for backward compatibility
        production_configs = {"production", "heroku"}
        if config_name in production_configs:
            return "0.0.0.0"  # noqa: S104  # Intentional production binding

    # Default to localhost for development/testing environments
    return "127.0.0.1"


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
    def init_app(cls, app: "Flask") -> None:
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
    @classmethod
    def init_app(cls, app: "Flask") -> None:
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


config: dict[str | FlaskEnvironment, Type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    FlaskEnvironment.DEVELOPMENT: DevelopmentConfig,
    FlaskEnvironment.TESTING: TestConfig,
    FlaskEnvironment.PRODUCTION: ProductionConfig,
}
