"""Heroku-specific configuration overrides."""
import os

try:
    from app.config import ProductionConfig
except ImportError as e:
    import logging
    logging.warning(f"Could not import ProductionConfig: {e}")
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
        # Import logger after app initialization to avoid circular imports
        try:
            from app.logging_config import get_logger
            logger = get_logger('heroku_config')
        except ImportError:
            import logging
            logger = logging.getLogger('heroku_config')

        try:
            ProductionConfig.init_app(app)
            logger.info("Base ProductionConfig initialized")
        except Exception as e:
            logger.warning(f"ProductionConfig.init_app failed: {e}")

        # Validate SECRET_KEY
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            logger.critical("No SECRET_KEY set for Heroku production environment")
            raise ValueError("No SECRET_KEY set for Heroku production environment")

        app.config['SECRET_KEY'] = secret_key
        logger.info("SECRET_KEY configured for Heroku")

        # Trust the proxy headers from Heroku
        try:
            from werkzeug.middleware.proxy_fix import ProxyFix
            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
            logger.info("ProxyFix middleware applied for Heroku")
        except ImportError as e:
            logger.warning(f"Could not apply ProxyFix: {e}")

        logger.info("Heroku configuration initialization complete")
