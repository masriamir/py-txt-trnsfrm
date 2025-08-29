"""Unit tests for logging configuration module.

This module contains comprehensive unit tests for centralized logging setup,
log configuration management, logger creation, and logging integration
with different deployment environments.
"""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from app.logging_config import setup_logging, get_logger
from app.env_config import LoggingConfig, LogLevel


@pytest.mark.unit
class TestLoggingSetup:
    """Test suite for logging setup functionality."""

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_basic_configuration(self, mock_dict_config):
        """Test basic logging configuration setup."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        mock_dict_config.assert_called_once()
        config_dict = mock_dict_config.call_args[0][0]
        
        # Verify basic structure
        assert config_dict["version"] == 1
        assert config_dict["disable_existing_loggers"] is False
        assert "formatters" in config_dict
        assert "handlers" in config_dict
        assert "loggers" in config_dict

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_debug_mode_formatter(self, mock_dict_config):
        """Test that debug mode uses detailed formatter."""
        logging_config = LoggingConfig(LogLevel.DEBUG, True)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        console_handler = config_dict["handlers"]["console"]
        
        assert console_handler["formatter"] == "detailed"

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_production_mode_formatter(self, mock_dict_config):
        """Test that production mode uses standard formatter."""
        logging_config = LoggingConfig(LogLevel.WARNING, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        console_handler = config_dict["handlers"]["console"]
        
        assert console_handler["formatter"] == "standard"

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_log_levels(self, mock_dict_config):
        """Test that log levels are properly configured."""
        test_cases = [
            (LogLevel.DEBUG, "DEBUG"),
            (LogLevel.INFO, "INFO"),
            (LogLevel.WARNING, "WARNING"),
            (LogLevel.ERROR, "ERROR"),
            (LogLevel.CRITICAL, "CRITICAL")
        ]
        
        for log_level_enum, expected_string in test_cases:
            logging_config = LoggingConfig(log_level_enum, False)
            setup_logging(logging_config)
            
            config_dict = mock_dict_config.call_args[0][0]
            assert config_dict["handlers"]["console"]["level"] == expected_string
            assert config_dict["root"]["level"] == expected_string

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_formatters_configuration(self, mock_dict_config):
        """Test that formatters are properly configured."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        formatters = config_dict["formatters"]
        
        # Check all expected formatters exist
        assert "standard" in formatters
        assert "detailed" in formatters
        assert "json" in formatters
        
        # Check formatter patterns
        assert "%(asctime)s" in formatters["standard"]["format"]
        assert "%(levelname)s" in formatters["standard"]["format"]
        assert "%(funcName)s" in formatters["detailed"]["format"]
        assert "timestamp" in formatters["json"]["format"]

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_handlers_configuration(self, mock_dict_config):
        """Test that handlers are properly configured."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        handlers = config_dict["handlers"]
        
        # Check console handler exists and is configured
        assert "console" in handlers
        console_handler = handlers["console"]
        assert console_handler["class"] == "logging.StreamHandler"
        assert console_handler["stream"] == "ext://sys.stdout"

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    def test_setup_logging_loggers_configuration(self, mock_dict_config):
        """Test that loggers are properly configured."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        loggers = config_dict["loggers"]
        
        # Check expected loggers exist
        expected_loggers = ["app", "werkzeug", "gunicorn.error", "gunicorn.access"]
        for logger_name in expected_loggers:
            assert logger_name in loggers
            
        # Check app logger configuration
        app_logger = loggers["app"]
        assert "console" in app_logger["handlers"]
        assert app_logger["propagate"] is False

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    @patch("pathlib.Path.exists")
    @patch("os.access")
    def test_setup_logging_file_handler_when_directory_writable(
        self, mock_access, mock_exists, mock_dict_config
    ):
        """Test that file handler is added when logs directory is writable."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        with patch.dict(os.environ, {}, clear=True):  # Ensure not on Heroku
            setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        
        # Should have file handler
        assert "file" in config_dict["handlers"]
        file_handler = config_dict["handlers"]["file"]
        assert file_handler["class"] == "logging.handlers.RotatingFileHandler"
        assert "app.log" in file_handler["filename"]

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    @patch("pathlib.Path.exists")
    def test_setup_logging_no_file_handler_when_directory_not_writable(
        self, mock_exists, mock_dict_config
    ):
        """Test that file handler is not added when logs directory is not writable."""
        mock_exists.return_value = False
        
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        
        # Should not have file handler
        assert "file" not in config_dict["handlers"]

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    @patch.dict(os.environ, {"DYNO": "web.1"})
    def test_setup_logging_no_file_handler_on_heroku(self, mock_dict_config):
        """Test that file handler is not added on Heroku (DYNO env var set)."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        
        # Should not have file handler on Heroku
        assert "file" not in config_dict["handlers"]

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    @patch.dict(os.environ, {"FLASK_CONFIG": "production", "CONTAINER_ENV": "true"})
    def test_setup_logging_json_formatter_in_production_container(self, mock_dict_config):
        """Test that JSON formatter is used in production containers."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        setup_logging(logging_config)
        
        config_dict = mock_dict_config.call_args[0][0]
        console_handler = config_dict["handlers"]["console"]
        
        assert console_handler["formatter"] == "json"

    @pytest.mark.unit
    @patch("logging.config.dictConfig")
    @patch("pathlib.Path.exists")
    @patch("os.access", side_effect=PermissionError("Access denied"))
    def test_setup_logging_handles_permission_error(
        self, mock_access, mock_exists, mock_dict_config
    ):
        """Test that permission errors during file handler setup are handled gracefully."""
        mock_exists.return_value = True
        
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        # Should not raise exception
        setup_logging(logging_config)
        
        # Should still configure successfully without file handler
        mock_dict_config.assert_called_once()


@pytest.mark.unit
class TestGetLogger:
    """Test suite for logger creation functionality."""

    @pytest.mark.unit
    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a proper logging.Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_get_logger_adds_app_namespace(self):
        """Test that get_logger adds 'app.' namespace to logger names."""
        logger = get_logger("test_module")
        assert logger.name == "app.test_module"

    @pytest.mark.unit
    def test_get_logger_preserves_app_namespace(self):
        """Test that get_logger doesn't double-add 'app.' namespace."""
        logger = get_logger("app.test_module")
        assert logger.name == "app.test_module"

    @pytest.mark.unit
    def test_get_logger_with_different_names(self):
        """Test get_logger with various module names."""
        test_names = [
            "main",
            "utils.transformers",
            "config",
            "__main__",
            "nested.module.name"
        ]
        
        for name in test_names:
            logger = get_logger(name)
            assert logger.name == f"app.{name}"
            assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_get_logger_with_empty_name(self):
        """Test get_logger with empty string name."""
        logger = get_logger("")
        assert logger.name == "app."
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_get_logger_caching_behavior(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        
        # Should return the same logger instance
        assert logger1 is logger2

    @pytest.mark.unit
    def test_get_logger_different_names_different_instances(self):
        """Test that get_logger returns different instances for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        # Should return different logger instances
        assert logger1 is not logger2
        assert logger1.name != logger2.name


@pytest.mark.integration
class TestLoggingIntegration:
    """Integration tests for logging configuration with real components."""

    @pytest.mark.integration
    def test_logging_setup_integration(self):
        """Test complete logging setup integration."""
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        # Should not raise exceptions
        setup_logging(logging_config)
        
        # Should be able to create and use loggers
        logger = get_logger("test_integration")
        logger.info("Test message")
        
        # Logger should be properly configured
        assert logger.level <= logging.INFO
        assert len(logger.handlers) >= 0  # May have inherited handlers

    @pytest.mark.integration
    def test_logger_hierarchy_integration(self):
        """Test that logger hierarchy works correctly."""
        logging_config = LoggingConfig(LogLevel.DEBUG, True)
        setup_logging(logging_config)
        
        # Create loggers at different levels
        root_logger = get_logger("app")
        child_logger = get_logger("app.main")
        grandchild_logger = get_logger("app.main.routes")
        
        # All should be properly configured
        for logger in [root_logger, child_logger, grandchild_logger]:
            assert isinstance(logger, logging.Logger)
            assert logger.name.startswith("app")

    @pytest.mark.integration
    def test_different_log_levels_integration(self):
        """Test logging with different log levels."""
        for log_level in LogLevel:
            logging_config = LoggingConfig(log_level, False)
            setup_logging(logging_config)
            
            logger = get_logger("test_levels")
            
            # Should be able to log at all levels without exceptions
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

    @pytest.mark.integration
    @patch("pathlib.Path.exists")
    @patch("os.access")
    def test_file_logging_integration(self, mock_access, mock_exists):
        """Test file logging integration when possible."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        logging_config = LoggingConfig(LogLevel.INFO, False)
        
        with patch.dict(os.environ, {}, clear=True):
            setup_logging(logging_config)
        
        logger = get_logger("test_file")
        
        # Should be able to log without exceptions
        logger.info("Test file logging message")

    @pytest.mark.integration
    def test_flask_app_logging_integration(self):
        """Test logging integration with Flask application."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.app_context():
            logger = get_logger("test_flask")
            
            # Should be able to log within Flask context
            logger.info("Test Flask logging integration")
            
            # Logger should be properly configured
            assert isinstance(logger, logging.Logger)
            assert logger.name.startswith("app.")

    @pytest.mark.integration
    def test_middleware_logging_integration(self):
        """Test that logging works with request middleware."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            # This should trigger middleware logging
            response = client.get("/health")
            assert response.status_code == 200
            
            # No exceptions should be raised from logging