"""Heroku-specific configuration overrides."""
import os

try:
    from app.config import ProductionConfig
except ImportError as e:
    print(f"Warning: Could not import ProductionConfig: {e}")
    # Fallback base config
    class ProductionConfig:
        DEBUG = False
        TESTING = False
        SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

        @classmethod
        def init_app(cls, app):
            pass

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
        try:
            ProductionConfig.init_app(app)
        except Exception as e:
            print(f"Warning: ProductionConfig.init_app failed: {e}")

        # Validate SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("No SECRET_KEY set for Heroku production environment")
        app.config['SECRET_KEY'] = secret_key

        # Trust the proxy headers from Heroku
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix
            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
            print("✓ ProxyFix middleware applied")
        except ImportError as e:
            print(f"Warning: Could not apply ProxyFix: {e}")

        # Configure logging for Heroku
        try:
            import logging
            from logging import StreamHandler

            # Set up logging to stdout for Heroku logs
            if not app.logger.handlers:  # Avoid duplicate handlers
                stream_handler = StreamHandler()
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
                app.logger.setLevel(logging.INFO)

            app.logger.info('Heroku deployment startup complete')
            print("✓ Logging configured for Heroku")

        except Exception as e:
            print(f"Warning: Logging setup failed: {e}")

        print(f"✓ Heroku config initialized")
        print(f"  SECRET_KEY: {'Set' if app.config.get('SECRET_KEY') else 'Not set'}")
        print(f"  DEBUG: {app.config.get('DEBUG', 'Not set')}")
