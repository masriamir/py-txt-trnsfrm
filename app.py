import os
from app import create_app
from app.config import config


def main():
    """Entry point for the application."""
    # Get configuration from environment variable, default to 'development'
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    print(f"Starting application with config: {config_name}")

    try:
        app = create_app(config[config_name])

        port = int(os.environ.get('PORT', 5000))
        debug = config_name == 'development'

        print(f"Running on http://localhost:{port}")
        print(f"Debug mode: {debug}")

        app.run(host='0.0.0.0', port=port, debug=debug)

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure all required environment variables are set.")
        exit(1)


if __name__ == '__main__':
    main()
