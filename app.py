"""Main application entry point."""
import os
from app import create_app
from app.config import config

def main():
    """Entry point for running the application directly."""
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    print(f"Starting application with config: {config_name}")

    try:
        if os.environ.get('DYNO'):  # Running on Heroku
            from heroku_config import HerokuConfig
            config['heroku'] = HerokuConfig
            config_name = 'heroku'

        app = create_app(config[config_name])

        port = int(os.environ.get('PORT', 5000))
        debug = config_name == 'development'

        print(f"Running on port: {port}")
        print(f"Debug mode: {debug}")

        app.run(host='0.0.0.0', port=port, debug=debug)

    except Exception as e:
        print(f"Configuration error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
