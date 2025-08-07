"""
WSGI entry point for Heroku deployment.
This file is separate from app.py to avoid any conflicts.
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

print("=== WSGI Debug Info ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries
print(f"Environment variables:")
print(f"  DYNO: {os.environ.get('DYNO', 'Not set')}")
print(f"  FLASK_CONFIG: {os.environ.get('FLASK_CONFIG', 'Not set')}")
print(f"  SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")

try:
    print("Importing config...")
    from app.config import config
    print("✓ Config imported successfully")

    # Determine configuration
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    print(f"Using config: {config_name}")

    # Special handling for Heroku
    if os.environ.get('DYNO'):  # DYNO env var indicates Heroku
        print("Detected Heroku environment")
        config_name = 'heroku'
        try:
            from heroku_config import HerokuConfig
            config['heroku'] = HerokuConfig
            print("✓ Heroku config loaded")
        except Exception as e:
            print(f"✗ Failed to load Heroku config: {e}")
            # Fallback to production config
            config_name = 'production'

    print("Creating Flask app...")
    from app import create_app
    app = create_app(config[config_name])
    print("✓ Flask app created successfully")

    # Test that the app works
    with app.app_context():
        print(f"✓ App context working. Debug mode: {app.debug}")

    print("=== WSGI Setup Complete ===")

except Exception as e:
    print(f"✗ Error during setup: {e}")
    import traceback
    traceback.print_exc()
    # Create a minimal app as fallback
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def error():
        return f"Error loading app: {str(e)}", 500

# Export the app for gunicorn
application = app

# For backwards compatibility
if __name__ == '__main__':
    app.run()
