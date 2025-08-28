"""Tests for centralized environment variable configuration module."""

import os
from unittest.mock import patch

import pytest

from app.env_config import (
    LoggingConfig,
    get_flask_env,
    get_flask_env_for_wsgi,
    get_logging_config,
    get_port,
    get_web_concurrency,
    is_heroku_environment,
)


@pytest.mark.unit
class TestLoggingConfig:
    """Test logging configuration functionality."""

    def test_logging_config_tuple_structure(self):
        """Test LoggingConfig named tuple structure."""
        config = LoggingConfig(log_level="INFO", debug_mode=False)
        assert config.log_level == "INFO"
        assert config.debug_mode is False

        # Test that it's immutable
        with pytest.raises(AttributeError):
            config.log_level = "DEBUG"

    @pytest.mark.unit
    def test_get_logging_config_debug_level(self):
        """Test get_logging_config with DEBUG level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
            config = get_logging_config()
            assert config.log_level == "DEBUG"
            assert config.debug_mode is True

    @pytest.mark.unit
    def test_get_logging_config_info_level(self):
        """Test get_logging_config with INFO level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "info"}):
            config = get_logging_config()
            assert config.log_level == "INFO"
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_warning_level(self):
        """Test get_logging_config with WARNING level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "warning"}):
            config = get_logging_config()
            assert config.log_level == "WARNING"
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_error_level(self):
        """Test get_logging_config with ERROR level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "error"}):
            config = get_logging_config()
            assert config.log_level == "ERROR"
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_critical_level(self):
        """Test get_logging_config with CRITICAL level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "critical"}):
            config = get_logging_config()
            assert config.log_level == "CRITICAL"
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_case_insensitive(self):
        """Test get_logging_config handles case variations."""
        test_cases = [
            ("Debug", "DEBUG", True),
            ("INFO", "INFO", False),
            ("Warning", "WARNING", False),
            ("ERROR", "ERROR", False),
            ("Critical", "CRITICAL", False),
        ]

        for input_level, expected_level, expected_debug in test_cases:
            with patch.dict(os.environ, {"LOG_LEVEL": input_level}):
                config = get_logging_config()
                assert config.log_level == expected_level
                assert config.debug_mode == expected_debug

    @pytest.mark.unit
    def test_get_logging_config_invalid_level(self):
        """Test get_logging_config with invalid level defaults to INFO."""
        invalid_levels = ["invalid", "trace", "verbose", "123", ""]

        for invalid_level in invalid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": invalid_level}):
                config = get_logging_config()
                assert config.log_level == "INFO"
                assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_no_env_var(self):
        """Test get_logging_config with no LOG_LEVEL environment variable."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove LOG_LEVEL if it exists
            os.environ.pop("LOG_LEVEL", None)
            config = get_logging_config()
            assert config.log_level == "INFO"
            assert config.debug_mode is False


@pytest.mark.unit
class TestFlaskEnvironmentConfig:
    """Test Flask environment configuration."""

    @pytest.mark.unit
    def test_get_flask_env_with_environment_variable(self):
        """Test get_flask_env with FLASK_ENV set."""
        with patch.dict(os.environ, {"FLASK_ENV": "production"}):
            assert get_flask_env() == "production"

    @pytest.mark.unit
    def test_get_flask_env_default(self):
        """Test get_flask_env default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FLASK_ENV", None)
            assert get_flask_env() == "development"

    @pytest.mark.unit
    def test_get_flask_env_for_wsgi_with_environment_variable(self):
        """Test get_flask_env_for_wsgi with FLASK_ENV set."""
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            assert get_flask_env_for_wsgi() == "development"

    @pytest.mark.unit
    def test_get_flask_env_for_wsgi_default(self):
        """Test get_flask_env_for_wsgi default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FLASK_ENV", None)
            assert get_flask_env_for_wsgi() == "production"


@pytest.mark.unit
class TestHerokuEnvironmentDetection:
    """Test Heroku environment detection."""

    @pytest.mark.unit
    def test_is_heroku_environment_true(self):
        """Test is_heroku_environment returns True when DYNO is set."""
        with patch.dict(os.environ, {"DYNO": "web.1"}):
            assert is_heroku_environment() is True

    @pytest.mark.unit
    def test_is_heroku_environment_false(self):
        """Test is_heroku_environment returns False when DYNO is not set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DYNO", None)
            assert is_heroku_environment() is False

    @pytest.mark.unit
    def test_is_heroku_environment_empty_string(self):
        """Test is_heroku_environment returns False for empty DYNO."""
        with patch.dict(os.environ, {"DYNO": ""}):
            assert is_heroku_environment() is False


@pytest.mark.unit
class TestPortConfiguration:
    """Test port configuration."""

    @pytest.mark.unit
    def test_get_port_with_environment_variable(self):
        """Test get_port with PORT environment variable set."""
        with patch.dict(os.environ, {"PORT": "8080"}):
            assert get_port() == 8080

    @pytest.mark.unit
    def test_get_port_default(self):
        """Test get_port default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PORT", None)
            assert get_port() == 5000

    @pytest.mark.unit
    def test_get_port_string_conversion(self):
        """Test get_port converts string to integer."""
        with patch.dict(os.environ, {"PORT": "3000"}):
            port = get_port()
            assert isinstance(port, int)
            assert port == 3000

    @pytest.mark.unit
    def test_get_web_concurrency_with_environment_variable(self):
        """Test get_web_concurrency with WEB_CONCURRENCY environment variable set."""
        with patch.dict(os.environ, {"WEB_CONCURRENCY": "4"}):
            assert get_web_concurrency() == "4"

    @pytest.mark.unit
    def test_get_web_concurrency_default(self):
        """Test get_web_concurrency default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEB_CONCURRENCY", None)
            assert get_web_concurrency() == "auto"

    @pytest.mark.unit
    def test_get_web_concurrency_string_type(self):
        """Test get_web_concurrency returns string type."""
        with patch.dict(os.environ, {"WEB_CONCURRENCY": "2"}):
            concurrency = get_web_concurrency()
            assert isinstance(concurrency, str)
            assert concurrency == "2"


@pytest.mark.integration
class TestEnvironmentConfigIntegration:
    """Integration tests for environment configuration."""

    @pytest.mark.integration
    def test_logging_config_integration_with_flask_creation(self):
        """Test logging config integration with Flask app creation."""
        with patch.dict(os.environ, {"LOG_LEVEL": "debug", "FLASK_ENV": "development"}):
            config = get_logging_config()
            flask_env = get_flask_env()

            assert config.log_level == "DEBUG"
            assert config.debug_mode is True
            assert flask_env == "development"

    @pytest.mark.integration
    def test_production_environment_configuration(self):
        """Test production environment configuration."""
        with patch.dict(
            os.environ,
            {
                "LOG_LEVEL": "info",
                "FLASK_ENV": "production",
                "PORT": "80",
                "WEB_CONCURRENCY": "4",
            },
        ):
            config = get_logging_config()
            flask_env = get_flask_env_for_wsgi()
            port = get_port()
            web_concurrency = get_web_concurrency()

            assert config.log_level == "INFO"
            assert config.debug_mode is False
            assert flask_env == "production"
            assert port == 80
            assert web_concurrency == "4"

    @pytest.mark.integration
    def test_heroku_environment_configuration(self):
        """Test Heroku environment configuration."""
        with patch.dict(
            os.environ, {"DYNO": "web.1", "LOG_LEVEL": "info", "PORT": "5000"}
        ):
            is_heroku = is_heroku_environment()
            config = get_logging_config()
            port = get_port()

            assert is_heroku is True
            assert config.log_level == "INFO"
            assert config.debug_mode is False
            assert port == 5000

    @pytest.mark.integration
    def test_all_environment_functions_work_together(self):
        """Test that all environment configuration functions work together."""
        test_env = {
            "LOG_LEVEL": "warning",
            "FLASK_ENV": "testing",
            "PORT": "8000",
            "DYNO": "worker.1",
        }

        with patch.dict(os.environ, test_env):
            config = get_logging_config()
            flask_env = get_flask_env()
            flask_env_wsgi = get_flask_env_for_wsgi()
            port = get_port()
            is_heroku = is_heroku_environment()

            # Verify all functions return expected values
            assert config.log_level == "WARNING"
            assert config.debug_mode is False
            assert flask_env == "testing"
            assert flask_env_wsgi == "testing"
            assert port == 8000
            assert is_heroku is True
