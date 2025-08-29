"""Tests for centralized environment variable configuration module."""

import os
from unittest.mock import patch

import pytest

from app.env_config import (
    FlaskEnvironment,
    LoggingConfig,
    LogLevel,
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
        config = LoggingConfig(log_level=LogLevel.INFO, debug_mode=False)
        assert config.log_level == LogLevel.INFO
        assert config.debug_mode is False

        # Test that it's immutable
        with pytest.raises(AttributeError):
            config.log_level = LogLevel.DEBUG

    @pytest.mark.unit
    def test_get_logging_config_debug_level(self):
        """Test get_logging_config with DEBUG level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
            config = get_logging_config()
            assert config.log_level == LogLevel.DEBUG
            assert config.debug_mode is True

    @pytest.mark.unit
    def test_get_logging_config_info_level(self):
        """Test get_logging_config with INFO level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "info"}):
            config = get_logging_config()
            assert config.log_level == LogLevel.INFO
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_warning_level(self):
        """Test get_logging_config with WARNING level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "warning"}):
            config = get_logging_config()
            assert config.log_level == LogLevel.WARNING
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_error_level(self):
        """Test get_logging_config with ERROR level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "error"}):
            config = get_logging_config()
            assert config.log_level == LogLevel.ERROR
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_critical_level(self):
        """Test get_logging_config with CRITICAL level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "critical"}):
            config = get_logging_config()
            assert config.log_level == LogLevel.CRITICAL
            assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_case_insensitive(self):
        """Test get_logging_config handles case variations."""
        test_cases = [
            ("Debug", LogLevel.DEBUG, True),
            ("INFO", LogLevel.INFO, False),
            ("Warning", LogLevel.WARNING, False),
            ("ERROR", LogLevel.ERROR, False),
            ("Critical", LogLevel.CRITICAL, False),
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
                assert config.log_level == LogLevel.INFO
                assert config.debug_mode is False

    @pytest.mark.unit
    def test_get_logging_config_no_env_var(self):
        """Test get_logging_config with no LOG_LEVEL environment variable."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove LOG_LEVEL if it exists
            os.environ.pop("LOG_LEVEL", None)
            config = get_logging_config()
            assert config.log_level == LogLevel.INFO
            assert config.debug_mode is False


@pytest.mark.unit
class TestLogLevelEnum:
    """Test LogLevel enum functionality."""

    @pytest.mark.unit
    def test_log_level_enum_values(self):
        """Test LogLevel enum has correct values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    @pytest.mark.unit
    def test_log_level_enum_comparison(self):
        """Test LogLevel enum comparison works correctly."""
        debug_config = LoggingConfig(log_level=LogLevel.DEBUG, debug_mode=True)
        info_config = LoggingConfig(log_level=LogLevel.INFO, debug_mode=False)

        assert debug_config.log_level == LogLevel.DEBUG
        assert info_config.log_level == LogLevel.INFO
        assert debug_config.log_level != info_config.log_level

    @pytest.mark.unit
    def test_log_level_enum_string_conversion(self):
        """Test LogLevel enum can be converted to string."""
        assert str(LogLevel.DEBUG.value) == "DEBUG"
        assert str(LogLevel.INFO.value) == "INFO"

    @pytest.mark.unit
    def test_log_level_enum_from_string_valid(self):
        """Test LogLevel enum creation from valid strings."""
        assert LogLevel("DEBUG") == LogLevel.DEBUG
        assert LogLevel("INFO") == LogLevel.INFO
        assert LogLevel("WARNING") == LogLevel.WARNING
        assert LogLevel("ERROR") == LogLevel.ERROR
        assert LogLevel("CRITICAL") == LogLevel.CRITICAL

    @pytest.mark.unit
    def test_log_level_enum_from_string_invalid(self):
        """Test LogLevel enum raises ValueError for invalid strings."""
        with pytest.raises(ValueError):
            LogLevel("INVALID")
        with pytest.raises(ValueError):
            LogLevel("TRACE")
        with pytest.raises(ValueError):
            LogLevel("VERBOSE")


@pytest.mark.unit
class TestFlaskEnvironmentEnum:
    """Test FlaskEnvironment enum functionality."""

    @pytest.mark.unit
    def test_flask_environment_enum_values(self):
        """Test FlaskEnvironment enum has correct values."""
        assert FlaskEnvironment.DEVELOPMENT.value == "development"
        assert FlaskEnvironment.TESTING.value == "testing"
        assert FlaskEnvironment.PRODUCTION.value == "production"

    @pytest.mark.unit
    def test_flask_environment_from_string_valid(self):
        """Test FlaskEnvironment.from_string with valid values."""
        test_cases = [
            ("development", FlaskEnvironment.DEVELOPMENT),
            ("testing", FlaskEnvironment.TESTING),
            ("production", FlaskEnvironment.PRODUCTION),
            ("DEVELOPMENT", FlaskEnvironment.DEVELOPMENT),
            ("Testing", FlaskEnvironment.TESTING),
            ("PRODUCTION", FlaskEnvironment.PRODUCTION),
        ]

        for input_str, expected_enum in test_cases:
            result = FlaskEnvironment.from_string(input_str)
            assert result == expected_enum
            assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_flask_environment_from_string_invalid(self):
        """Test FlaskEnvironment.from_string with invalid values."""
        invalid_values = ["invalid", "staging", "local", "123", "", None]

        for invalid_value in invalid_values:
            with pytest.raises(ValueError) as exc_info:
                FlaskEnvironment.from_string(invalid_value)
            assert "Invalid Flask environment" in str(exc_info.value)

    @pytest.mark.unit
    def test_flask_environment_from_string_error_message(self):
        """Test FlaskEnvironment.from_string error message includes valid values."""
        with pytest.raises(ValueError) as exc_info:
            FlaskEnvironment.from_string("invalid")

        error_message = str(exc_info.value)
        assert "Invalid Flask environment: 'invalid'" in error_message
        assert "development" in error_message
        assert "testing" in error_message
        assert "production" in error_message


@pytest.mark.unit
class TestFlaskEnvironmentConfig:
    """Test Flask environment configuration."""

    @pytest.mark.unit
    def test_get_flask_env_with_environment_variable(self):
        """Test get_flask_env with FLASK_ENV set."""
        with patch.dict(os.environ, {"FLASK_ENV": "production"}):
            result = get_flask_env()
            assert result == FlaskEnvironment.PRODUCTION
            assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_get_flask_env_default(self):
        """Test get_flask_env default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FLASK_ENV", None)
            result = get_flask_env()
            assert result == FlaskEnvironment.DEVELOPMENT
            assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_get_flask_env_for_wsgi_with_environment_variable(self):
        """Test get_flask_env_for_wsgi with FLASK_ENV set."""
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            result = get_flask_env_for_wsgi()
            assert result == FlaskEnvironment.DEVELOPMENT
            assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_get_flask_env_for_wsgi_default(self):
        """Test get_flask_env_for_wsgi default value."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FLASK_ENV", None)
            result = get_flask_env_for_wsgi()
            assert result == FlaskEnvironment.PRODUCTION
            assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_get_flask_env_case_insensitive(self):
        """Test get_flask_env handles case variations."""
        test_cases = [
            ("Development", FlaskEnvironment.DEVELOPMENT),
            ("PRODUCTION", FlaskEnvironment.PRODUCTION),
            ("Testing", FlaskEnvironment.TESTING),
        ]

        for input_env, expected_enum in test_cases:
            with patch.dict(os.environ, {"FLASK_ENV": input_env}):
                result = get_flask_env()
                assert result == expected_enum
                assert isinstance(result, FlaskEnvironment)

    @pytest.mark.unit
    def test_get_flask_env_invalid_value(self):
        """Test get_flask_env with invalid environment value raises ValueError."""
        invalid_environments = ["invalid", "staging", "local", "123", ""]

        for invalid_env in invalid_environments:
            with patch.dict(os.environ, {"FLASK_ENV": invalid_env}):
                with pytest.raises(ValueError) as exc_info:
                    get_flask_env()
                assert "Invalid Flask environment" in str(exc_info.value)
                assert invalid_env in str(exc_info.value)

    @pytest.mark.unit
    def test_get_flask_env_for_wsgi_invalid_value(self):
        """Test get_flask_env_for_wsgi with invalid environment value raises ValueError."""
        with patch.dict(os.environ, {"FLASK_ENV": "invalid"}):
            with pytest.raises(ValueError) as exc_info:
                get_flask_env_for_wsgi()
            assert "Invalid Flask environment" in str(exc_info.value)
            assert "invalid" in str(exc_info.value)


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

            assert config.log_level == LogLevel.DEBUG
            assert config.debug_mode is True
            assert flask_env == FlaskEnvironment.DEVELOPMENT
            assert isinstance(flask_env, FlaskEnvironment)

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

            assert config.log_level == LogLevel.INFO
            assert config.debug_mode is False
            assert flask_env == FlaskEnvironment.PRODUCTION
            assert isinstance(flask_env, FlaskEnvironment)
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
            assert config.log_level == LogLevel.INFO
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
            assert config.log_level == LogLevel.WARNING
            assert config.debug_mode is False
            assert flask_env == FlaskEnvironment.TESTING
            assert isinstance(flask_env, FlaskEnvironment)
            assert flask_env_wsgi == FlaskEnvironment.TESTING
            assert isinstance(flask_env_wsgi, FlaskEnvironment)
            assert port == 8000
            assert is_heroku is True

    @pytest.mark.integration
    def test_flask_app_creation_with_enum_environment(self):
        """Test Flask app creation works with enum environment values."""
        from app import create_app

        with patch.dict(os.environ, {"FLASK_ENV": "testing", "LOG_LEVEL": "info"}):
            app = create_app()
            assert app is not None
            assert app.config["TESTING"] is True  # TestConfig should be loaded
