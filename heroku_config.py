"""Heroku-specific configuration overrides."""
import os
from app.config import ProductionConfig


class HerokuConfig(ProductionConfig):
    """Configuration for Heroku deployment."""

    # Use DATABASE_URL if provided (for future database integration)
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Force SSL redirect in production
    SSL_REDIRECT = True

    # Trust Heroku's proxy headers
    PROXY_FIX = True

    @classmethod
    def init_app(cls, app):
        """Initialize Heroku-specific settings."""
        ProductionConfig.init_app(app)

        # Trust the proxy headers from Heroku
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix
            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        except ImportError:
            # If werkzeug version doesn't have ProxyFix, that's okay
            pass

        # Configure logging for Heroku
        import logging
        from logging import StreamHandler

        # Set up logging to stdout for Heroku logs
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Heroku deployment startup complete')

        print(f"Heroku config initialized successfully")
        print(f"SECRET_KEY set: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
        print(f"DEBUG mode: {app.config.get('DEBUG')}")
