"""Heroku-specific configuration module.

This module provides configuration overrides specifically tailored for
Heroku deployment environments. It extends the base ProductionConfig
with Heroku-specific settings including proxy configuration, SSL settings,
and environment validation.
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

try:
    from app.config import ProductionConfig as BaseProductionConfig
    
    _has_production_config = True
except ImportError as e:
    import logging

    logging.warning(f"Could not import ProductionConfig: {e}")
    _has_production_config = False

    # Fallback base config
    class _FallbackBaseConfig:
        """Fallback configuration class if main config cannot be imported."""

        DEBUG = False
        TESTING = False
        SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")

        @classmethod
        def init_app(cls, app: "Flask") -> None:
            """Initialize fallback configuration.

            Args:
                app: Flask application instance.
            """
            pass
    
    BaseProductionConfig = _FallbackBaseConfig  # type: ignore[misc, assignment]


class HerokuConfig(BaseProductionConfig):
    """Configuration class optimized for Heroku deployment.

    This configuration extends ProductionConfig with Heroku-specific
    settings including proxy trust configuration, SSL settings, and
    enhanced logging for the Heroku environment.

    Attributes:
        DATABASE_URL: Database connection URL (for future use).
        SSL_REDIRECT: Whether to force SSL redirects in production.
        PROXY_FIX: Whether to apply proxy fix middleware.
    """

    # Use DATABASE_URL if provided (for future database integration)
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Force SSL redirect in production
    SSL_REDIRECT = True

    # Trust Heroku's proxy headers
    PROXY_FIX = True

    @classmethod
    def init_app(cls, app: "Flask") -> None:
        """Initialize Heroku-specific application settings.

        Configures the Flask application for Heroku deployment including
        proxy header handling, SSL configuration, and environment validation.

        Args:
            app: Flask application instance to configure.

        Raises:
            ValueError: If required environment variables are not set.
        """
        # Import logger after app initialization to avoid circular imports
        try:
            from app.logging_config import get_logger

            logger = get_logger("heroku_config")
        except ImportError:
            import logging

            logger = logging.getLogger("heroku_config")

        try:
            super().init_app(app)
            logger.info("Base ProductionConfig initialized")
        except Exception as e:
            logger.warning(f"Base config init_app failed: {e}")

        # Validate SECRET_KEY
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            logger.critical("No SECRET_KEY set for Heroku production environment")
            raise ValueError("No SECRET_KEY set for Heroku production environment")

        app.config["SECRET_KEY"] = secret_key
        logger.info("SECRET_KEY configured for Heroku")

        # Trust the proxy headers from Heroku
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix

            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore[method-assign]
            logger.info("ProxyFix middleware applied for Heroku")
        except ImportError as e:
            logger.warning(f"Could not apply ProxyFix: {e}")

        logger.info("Heroku configuration initialization complete")
