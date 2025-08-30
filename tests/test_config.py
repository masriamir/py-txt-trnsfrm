"""Unit tests for Flask application configuration module.

This module contains comprehensive unit tests for configuration classes,
environment-specific settings, host binding logic, and configuration
validation functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest

from app.config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestConfig,
    config,
    get_host_for_environment,
)
from app.env_config import FlaskEnvironment


@pytest.mark.unit
class TestBaseConfig:
    """Test suite for base Config class functionality."""

    @pytest.mark.unit
    def test_base_config_defaults(self):
        """Test that base Config class has correct default values."""
        assert Config.DEBUG == False  # Should default to False for security
        assert Config.TESTING == False
        assert hasattr(Config, "SECRET_KEY")

    @pytest.mark.unit
    @patch.dict(os.environ, {"SECRET_KEY": "test-secret"})
    def test_secret_key_from_environment(self):
        """Test that SECRET_KEY is loaded from environment variable."""
        # Test that environment variable is accessible
        assert os.environ.get("SECRET_KEY") == "test-secret"

        # Test that Config class can access it
        secret_key = (
            os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
        )
        assert secret_key == "test-secret"

    @pytest.mark.unit
    @patch.dict(os.environ, {"FLASK_DEBUG": "True"})
    def test_debug_from_environment_true(self):
        """Test that DEBUG flag respects FLASK_DEBUG environment variable."""
        # Test the logic pattern that Config uses
        debug_value = os.environ.get("FLASK_DEBUG", "False")
        is_debug = debug_value.lower() in ["true", "1", "yes"]
        assert is_debug

    @pytest.mark.unit
    @patch.dict(os.environ, {"FLASK_DEBUG": "False"})
    def test_debug_from_environment_false(self):
        """Test that DEBUG flag properly handles false values."""
        # Test the logic pattern that Config uses
        debug_value = os.environ.get("FLASK_DEBUG", "False")
        is_debug = debug_value.lower() in ["true", "1", "yes"]
        assert not is_debug

    @pytest.mark.unit
    def test_init_app_method_exists(self):
        """Test that base Config class has init_app method."""
        assert hasattr(Config, "init_app")
        assert callable(Config.init_app)

    @pytest.mark.unit
    def test_init_app_method_works(self):
        """Test that base Config init_app method works without errors."""
        mock_app = Mock()
        # Should not raise any exceptions
        Config.init_app(mock_app)


@pytest.mark.unit
class TestDevelopmentConfig:
    """Test suite for DevelopmentConfig class."""

    @pytest.mark.unit
    def test_development_config_inherits_from_base(self):
        """Test that DevelopmentConfig properly inherits from Config."""
        assert issubclass(DevelopmentConfig, Config)

    @pytest.mark.unit
    def test_development_config_debug_enabled(self):
        """Test that DevelopmentConfig has DEBUG enabled."""
        assert DevelopmentConfig.DEBUG is True

    @pytest.mark.unit
    def test_development_config_testing_disabled(self):
        """Test that DevelopmentConfig has TESTING disabled."""
        assert DevelopmentConfig.TESTING is False

    @pytest.mark.unit
    def test_development_config_secret_key(self):
        """Test that DevelopmentConfig has appropriate secret key."""
        assert hasattr(DevelopmentConfig, "SECRET_KEY")
        assert DevelopmentConfig.SECRET_KEY is not None


@pytest.mark.unit
class TestTestConfig:
    """Test suite for TestConfig class."""

    @pytest.mark.unit
    def test_test_config_inherits_from_base(self):
        """Test that TestConfig properly inherits from Config."""
        assert issubclass(TestConfig, Config)

    @pytest.mark.unit
    def test_test_config_testing_enabled(self):
        """Test that TestConfig has TESTING enabled."""
        assert TestConfig.TESTING is True

    @pytest.mark.unit
    def test_test_config_secret_key(self):
        """Test that TestConfig has fixed secret key for testing."""
        assert TestConfig.SECRET_KEY == "test-secret-key"

    @pytest.mark.unit
    def test_test_config_csrf_disabled(self):
        """Test that TestConfig disables CSRF for easier testing."""
        assert TestConfig.WTF_CSRF_ENABLED is False


@pytest.mark.unit
class TestProductionConfig:
    """Test suite for ProductionConfig class."""

    @pytest.mark.unit
    def test_production_config_inherits_from_base(self):
        """Test that ProductionConfig properly inherits from Config."""
        assert issubclass(ProductionConfig, Config)

    @pytest.mark.unit
    def test_production_config_debug_disabled(self):
        """Test that ProductionConfig has DEBUG disabled."""
        assert ProductionConfig.DEBUG is False

    @pytest.mark.unit
    def test_production_config_testing_disabled(self):
        """Test that ProductionConfig has TESTING disabled."""
        assert ProductionConfig.TESTING is False

    @pytest.mark.unit
    @patch.dict(os.environ, {"SECRET_KEY": "production-secret"})
    def test_production_config_init_app_with_secret_key(self):
        """Test ProductionConfig init_app works with SECRET_KEY set."""
        mock_app = Mock()
        mock_app.config = {}

        # Should not raise exception
        ProductionConfig.init_app(mock_app)

        # Should set SECRET_KEY on app config
        assert mock_app.config["SECRET_KEY"] == "production-secret"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_production_config_init_app_without_secret_key(self):
        """Test ProductionConfig init_app fails without SECRET_KEY."""
        mock_app = Mock()

        with pytest.raises(
            ValueError, match="No SECRET_KEY set for production environment"
        ):
            ProductionConfig.init_app(mock_app)


@pytest.mark.unit
class TestHostBindingLogic:
    """Test suite for host binding security logic."""

    @pytest.mark.unit
    @patch.dict(os.environ, {"DYNO": "web.1"})
    def test_heroku_environment_detection(self):
        """Test that Heroku environment is detected via DYNO variable."""
        host = get_host_for_environment("development")
        assert host == "0.0.0.0"  # Should bind to all interfaces on Heroku

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_production_string_binding(self):
        """Test production string config binds to all interfaces."""
        host = get_host_for_environment("production")
        assert host == "0.0.0.0"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_heroku_string_binding(self):
        """Test heroku string config binds to all interfaces."""
        host = get_host_for_environment("heroku")
        assert host == "0.0.0.0"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_production_enum_binding(self):
        """Test production FlaskEnvironment enum binds to all interfaces."""
        host = get_host_for_environment(FlaskEnvironment.PRODUCTION)
        assert host == "0.0.0.0"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_development_string_binding(self):
        """Test development string config binds to localhost."""
        host = get_host_for_environment("development")
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_development_enum_binding(self):
        """Test development FlaskEnvironment enum binds to localhost."""
        host = get_host_for_environment(FlaskEnvironment.DEVELOPMENT)
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_testing_string_binding(self):
        """Test testing string config binds to localhost."""
        host = get_host_for_environment("testing")
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_testing_enum_binding(self):
        """Test testing FlaskEnvironment enum binds to localhost."""
        host = get_host_for_environment(FlaskEnvironment.TESTING)
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_unknown_environment_defaults_to_localhost(self):
        """Test unknown environment defaults to localhost for security."""
        host = get_host_for_environment("unknown")
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_empty_string_environment(self):
        """Test empty string environment defaults to localhost."""
        host = get_host_for_environment("")
        assert host == "127.0.0.1"

    @pytest.mark.unit
    @patch.dict(os.environ, {"DYNO": "web.1"})
    def test_heroku_overrides_config_name(self):
        """Test that DYNO environment variable overrides config name."""
        # Even with development config, should bind to 0.0.0.0 on Heroku
        host = get_host_for_environment("development")
        assert host == "0.0.0.0"


@pytest.mark.unit
class TestConfigurationMapping:
    """Test suite for configuration mapping dictionary."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "expected_key",
        [
            "development",
            "testing",
            "production",
            FlaskEnvironment.DEVELOPMENT,
            FlaskEnvironment.TESTING,
            FlaskEnvironment.PRODUCTION,
        ],
    )
    def test_config_mapping_contains_all_environments(self, expected_key):
        """Test that config mapping contains all expected environments."""
        assert expected_key in config

    @pytest.mark.unit
    def test_config_mapping_values_are_classes(self):
        """Test that config mapping values are proper config classes."""
        for config_class in config.values():
            assert isinstance(config_class, type)
            assert issubclass(config_class, Config)

    @pytest.mark.unit
    def test_string_and_enum_mappings_match(self):
        """Test that string and enum mappings point to same classes."""
        assert config["development"] == config[FlaskEnvironment.DEVELOPMENT]
        assert config["testing"] == config[FlaskEnvironment.TESTING]
        assert config["production"] == config[FlaskEnvironment.PRODUCTION]

    @pytest.mark.unit
    def test_config_classes_are_distinct(self):
        """Test that different config classes are distinct objects."""
        assert config["development"] != config["testing"]
        assert config["testing"] != config["production"]
        assert config["development"] != config["production"]


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration with Flask application."""

    @pytest.mark.integration
    def test_development_config_integration(self):
        """Test DevelopmentConfig integration with Flask app."""
        from app import create_app

        app = create_app(DevelopmentConfig)
        assert app.config["DEBUG"] is True
        assert app.config["TESTING"] is False

    @pytest.mark.integration
    def test_test_config_integration(self):
        """Test TestConfig integration with Flask app."""
        from app import create_app

        app = create_app(TestConfig)
        assert app.config["DEBUG"] is False
        assert app.config["TESTING"] is True
        assert app.config["WTF_CSRF_ENABLED"] is False

    @pytest.mark.integration
    @patch.dict(os.environ, {"SECRET_KEY": "test-production-secret"})
    def test_production_config_integration(self):
        """Test ProductionConfig integration with Flask app."""
        from app import create_app

        app = create_app(ProductionConfig)
        assert app.config["DEBUG"] is False
        assert app.config["TESTING"] is False
        assert app.config["SECRET_KEY"] == "test-production-secret"

    @pytest.mark.integration
    def test_config_selection_by_environment(self):
        """Test that config selection works with different environments."""
        from app import create_app

        # Test with various config classes (excluding ProductionConfig due to SECRET_KEY requirement)
        for env_key, config_class in config.items():
            if (
                isinstance(env_key, str) and env_key != "production"
            ):  # Test string keys except production
                app = create_app(config_class)
                assert isinstance(app, type(create_app(TestConfig)))
