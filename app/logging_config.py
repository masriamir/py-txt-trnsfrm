"""Centralized logging configuration module.

This module provides centralized logging setup and configuration for the Flask
application. It supports different logging levels, output formats, and deployment
environments including development, production, and containerized deployments.
"""

import logging
import logging.config
import os
from typing import Any


def setup_logging(debug: bool = False) -> None:
    """Setup centralized logging configuration for the application.

    Configures logging with appropriate handlers, formatters, and log levels
    based on the deployment environment and debug setting. Supports both
    console and file logging with automatic detection of container environments.

    Args:
        debug: If True, enables DEBUG level logging with detailed formatting.
            If False, uses INFO level with standard formatting.
    """
    log_level = 'DEBUG' if debug else 'INFO'

    # Determine log file path - use logs directory in container, current directory otherwise
    log_dir = '/app/logs' if os.path.exists('/app/logs') else '.'
    log_file_path = os.path.join(log_dir, 'app.log')

    logging_config: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%dT%H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'standard' if not debug else 'detailed',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'app': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'WARNING',  # Reduce Flask's built-in server noise
                'handlers': ['console'],
                'propagate': False
            },
            'gunicorn.error': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'gunicorn.access': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }

    # Add file handler only if not in container or if logs directory is writable
    if not os.environ.get('DYNO') and os.access(log_dir, os.W_OK):
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'detailed',
            'filename': log_file_path,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        # Add file handler to app logger
        logging_config['loggers']['app']['handlers'].append('file')

    # In production containers, use structured logging for better log aggregation
    if os.environ.get('FLASK_CONFIG') == 'production' and os.environ.get('CONTAINER_ENV'):
        logging_config['handlers']['console']['formatter'] = 'json'

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the application's logging configuration.

    Creates and returns a logger instance that follows the application's
    centralized logging configuration. Automatically ensures all loggers
    are under the 'app' namespace for consistent logging hierarchy.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: Configured logger instance ready for use.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.debug("Debug information")
    """
    # Ensure all app loggers are under the 'app' namespace
    if not name.startswith('app.'):
        name = f'app.{name}'

    return logging.getLogger(name)
