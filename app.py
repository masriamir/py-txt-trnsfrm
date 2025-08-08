"""Main application entry point."""
import os
from app import create_app
from app.config import config
from app.logging_config import get_logger

# Set up basic logging for main entry point
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('main')

def main():
    """Entry point for running the application directly."""
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    logger.info(f"Starting application with config: {config_name}")

    try:
        if os.environ.get('DYNO'):  # Running on Heroku
            from heroku_config import HerokuConfig
            config['heroku'] = HerokuConfig
            config_name = 'heroku'
            logger.info("Detected Heroku environment, using Heroku config")

        app = create_app(config[config_name])

        port = int(os.environ.get('PORT', 5000))
        debug = config_name == 'development'

        logger.info(f"Starting server on port: {port}")
        logger.info(f"Debug mode: {debug}")

        app.run(host='0.0.0.0', port=port, debug=debug)

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        exit(1)

if __name__ == '__main__':
    main()
