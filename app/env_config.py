"""Centralized environment variable configuration module.

This module provides a single source of truth for handling LOG_LEVEL and DEBUG
environment variables across all application entry points (app.py, wsgi.py,
app/__init__.py, etc.). It ensures consistent behavior and simplifies
configuration management.
"""

import os
from typing import NamedTuple


class LoggingConfig(NamedTuple):
    """Configuration tuple for logging settings.

    Attributes:
        log_level: Validated log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug_mode: Boolean flag indicating if debug mode should be enabled
    """

    log_level: str
    debug_mode: bool


def get_logging_config() -> LoggingConfig:
    """Get centralized logging configuration from environment variables.

    This function provides the single source of truth for LOG_LEVEL and DEBUG
    environment variable handling. It processes these variables with consistent
    logic and validation across all entry points.

    Logic:
    1. Check LOG_LEVEL environment variable first
    2. Validate LOG_LEVEL against known values
    3. If LOG_LEVEL is "DEBUG", enable debug mode
    4. If LOG_LEVEL is invalid/missing, fall back to INFO level
    5. Return consistent configuration tuple

    Environment Variables:
        LOG_LEVEL: Logging level ('debug', 'info', 'warning', 'error', 'critical')
                  Case-insensitive. Defaults to 'info' if not set or invalid.

    Returns:
        LoggingConfig: Named tuple with validated log_level and debug_mode

    Examples:
        >>> # With LOG_LEVEL=debug
        >>> config = get_logging_config()
        >>> config.log_level
        'DEBUG'
        >>> config.debug_mode
        True

        >>> # With LOG_LEVEL=info or no LOG_LEVEL
        >>> config = get_logging_config()
        >>> config.log_level
        'INFO'
        >>> config.debug_mode
        False
    """
    # Get LOG_LEVEL from environment with default
    log_level_env = os.environ.get("LOG_LEVEL", "info").upper()

    # Valid logging levels
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    # Validate and set log level
    if log_level_env in valid_levels:
        log_level = log_level_env
    else:
        # Default to INFO for invalid values
        log_level = "INFO"

    # Enable debug mode only for DEBUG level
    debug_mode = log_level == "DEBUG"

    return LoggingConfig(log_level=log_level, debug_mode=debug_mode)


def get_flask_env() -> str:
    """Get Flask environment configuration.

    Returns the FLASK_ENV environment variable with appropriate default.

    Returns:
        str: Flask environment ('development', 'production', etc.)
             Defaults to 'development' for app.py, 'production' for wsgi.py
    """
    return os.environ.get("FLASK_ENV", "development")


def get_flask_env_for_wsgi() -> str:
    """Get Flask environment configuration for WSGI deployment.

    Returns the FLASK_ENV environment variable with production default,
    appropriate for WSGI server deployments.

    Returns:
        str: Flask environment, defaults to 'production' for WSGI contexts
    """
    return os.environ.get("FLASK_ENV", "production")


def is_heroku_environment() -> bool:
    """Check if application is running in Heroku environment.

    Returns:
        bool: True if DYNO environment variable is set (indicating Heroku)
    """
    return bool(os.environ.get("DYNO"))


def get_port() -> int:
    """Get port number from environment.

    Returns:
        int: Port number from PORT environment variable, defaults to 5000
    """
    return int(os.environ.get("PORT", 5000))


def get_web_concurrency() -> str:
    """Get web concurrency setting from environment.

    Returns:
        str: Web concurrency setting from WEB_CONCURRENCY environment variable,
             defaults to 'auto' for Gunicorn auto-detection
    """
    return os.environ.get("WEB_CONCURRENCY", "auto")
