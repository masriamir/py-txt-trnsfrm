import os
from app import create_app
from app.config import config


def main():
    """Entry point for the application."""
    # Get configuration from environment variable, default to 'development'
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    # Special handling for Heroku
    if os.environ.get('DYNO'):  # DYNO env var indicates Heroku
        config_name = 'heroku'
        # Import Heroku config
        from heroku_config import HerokuConfig
        config['heroku'] = HerokuConfig

    print(f"Starting application with config: {config_name}")

    try:
        app = create_app(config[config_name])

        port = int(os.environ.get('PORT', 5000))
        debug = config_name == 'development'

        print(f"Running on port: {port}")
        print(f"Debug mode: {debug}")

        if config_name == 'heroku':
            # In Heroku, we rely on the Procfile to run gunicorn
            # This is mainly for local testing of Heroku config
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            app.run(host='0.0.0.0', port=port, debug=debug)

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure all required environment variables are set.")
        exit(1)


# For Heroku and WSGI servers
config_name = os.environ.get('FLASK_CONFIG', 'development')
if os.environ.get('DYNO'):  # Running on Heroku
    from heroku_config import HerokuConfig
    config['heroku'] = HerokuConfig
    config_name = 'heroku'

app = create_app(config[config_name])

if __name__ == '__main__':
    main()
