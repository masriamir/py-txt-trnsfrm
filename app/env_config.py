"""Centralized environment variable configuration module.

This module provides a single source of truth for handling LOG_LEVEL and DEBUG
environment variables across all application entry points (app.py, wsgi.py,
app/__init__.py, etc.). It ensures consistent behavior and simplifies
configuration management.
"""

import os
from enum import Enum
from typing import NamedTuple


class LogLevel(Enum):
    """Enumeration of standard logging levels.

    Provides type-safe logging level constants that correspond to Python's
    standard logging levels. This enum ensures consistent usage and enables
    IDE autocompletion while maintaining compatibility with logging.config.

    Attributes:
        DEBUG: Debug level logging
        INFO: Informational level logging
        WARNING: Warning level logging
        ERROR: Error level logging
        CRITICAL: Critical level logging
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class FlaskEnvironment(Enum):
    """Enum for Flask environment configuration.

    This enum provides type-safe environment values with validation,
    improving IDE autocompletion and catching invalid environment
    values early in the development process.

    Values:
        DEVELOPMENT: Development environment with debugging enabled
        TESTING: Testing environment for automated tests
        PRODUCTION: Production environment with security hardening
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    @classmethod
    def from_string(cls, value: str) -> "FlaskEnvironment":
        """Convert string environment value to FlaskEnvironment enum.

        Provides backward compatibility for string environment variables
        while adding validation for invalid values.

        Args:
            value: String environment value (case-insensitive)

        Returns:
            FlaskEnvironment: Corresponding enum value

        Raises:
            ValueError: If the environment value is not valid

        Examples:
            >>> FlaskEnvironment.from_string("development")
            FlaskEnvironment.DEVELOPMENT
            >>> FlaskEnvironment.from_string("PRODUCTION")
            FlaskEnvironment.PRODUCTION
            >>> FlaskEnvironment.from_string("invalid")
            ValueError: Invalid Flask environment: 'invalid'
        """
        try:
            # Convert to lowercase and try to match enum values
            normalized_value = value.lower()
            for env in cls:
                if env.value == normalized_value:
                    return env
            # If no match found, raise ValueError
            raise ValueError(
                f"Invalid Flask environment: '{value}'. Valid values are: {', '.join([e.value for e in cls])}"
            )
        except (AttributeError, TypeError) as err:
            # Handle None or non-string inputs
            raise ValueError(
                f"Invalid Flask environment: '{value}'. Valid values are: {', '.join([e.value for e in cls])}"
            ) from err


class LoggingConfig(NamedTuple):
    """Configuration tuple for logging settings.

    Attributes:
        log_level: Validated log level from LogLevel enum
        debug_mode: Boolean flag indicating if debug mode should be enabled
    """

    log_level: LogLevel
    debug_mode: bool


def get_logging_config() -> LoggingConfig:
    """Get centralized logging configuration from environment variables.

    This function provides the single source of truth for LOG_LEVEL and DEBUG
    environment variable handling. It processes these variables with consistent
    logic and validation across all entry points.

    Logic:
    1. Check LOG_LEVEL environment variable first
    2. Validate LOG_LEVEL against LogLevel enum values
    3. If LOG_LEVEL is "DEBUG", enable debug mode
    4. If LOG_LEVEL is invalid/missing, fall back to INFO level
    5. Return consistent configuration tuple

    Environment Variables:
        LOG_LEVEL: Logging level ('debug', 'info', 'warning', 'error', 'critical')
                  Case-insensitive. Defaults to 'info' if not set or invalid.

    Returns:
        LoggingConfig: Named tuple with validated LogLevel enum and debug_mode

    Examples:
        >>> # With LOG_LEVEL=debug
        >>> config = get_logging_config()
        >>> config.log_level
        <LogLevel.DEBUG: 'DEBUG'>
        >>> config.debug_mode
        True

        >>> # With LOG_LEVEL=info or no LOG_LEVEL
        >>> config = get_logging_config()
        >>> config.log_level
        <LogLevel.INFO: 'INFO'>
        >>> config.debug_mode
        False
    """
    # Get LOG_LEVEL from environment with default
    log_level_env = os.environ.get("LOG_LEVEL", "info").upper()

    # Try to convert string to LogLevel enum
    try:
        log_level = LogLevel(log_level_env)
    except ValueError:
        # Default to INFO for invalid values
        log_level = LogLevel.INFO

    # Enable debug mode only for DEBUG level
    debug_mode = log_level == LogLevel.DEBUG

    return LoggingConfig(log_level=log_level, debug_mode=debug_mode)


def get_flask_env() -> FlaskEnvironment:
    """Get Flask environment configuration using FlaskEnvironment enum.

    Returns the FLASK_ENV environment variable with appropriate default,
    converted to a type-safe FlaskEnvironment enum value.

    Returns:
        FlaskEnvironment: Flask environment enum value
                         Defaults to FlaskEnvironment.DEVELOPMENT for app.py

    Raises:
        ValueError: If FLASK_ENV contains an invalid environment value

    Examples:
        >>> # With FLASK_ENV=production
        >>> get_flask_env()
        FlaskEnvironment.PRODUCTION
        >>> # With no FLASK_ENV set
        >>> get_flask_env()
        FlaskEnvironment.DEVELOPMENT
    """
    env_value = os.environ.get("FLASK_ENV", "development")
    return FlaskEnvironment.from_string(env_value)


def get_flask_env_for_wsgi() -> FlaskEnvironment:
    """Get Flask environment configuration for WSGI deployment using FlaskEnvironment enum.

    Returns the FLASK_ENV environment variable with production default,
    appropriate for WSGI server deployments, converted to a type-safe enum.

    Returns:
        FlaskEnvironment: Flask environment enum value,
                         defaults to FlaskEnvironment.PRODUCTION for WSGI contexts

    Raises:
        ValueError: If FLASK_ENV contains an invalid environment value

    Examples:
        >>> # With FLASK_ENV=development
        >>> get_flask_env_for_wsgi()
        FlaskEnvironment.DEVELOPMENT
        >>> # With no FLASK_ENV set
        >>> get_flask_env_for_wsgi()
        FlaskEnvironment.PRODUCTION
    """
    env_value = os.environ.get("FLASK_ENV", "production")
    return FlaskEnvironment.from_string(env_value)


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
