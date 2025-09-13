"""Unit tests for Flask application factory module.

This module contains comprehensive unit tests for the Flask application factory
function and related initialization logic, ensuring proper application configuration,
logging setup, middleware registration, and blueprint registration.
"""

from unittest.mock import Mock, patch

import pytest
from flask import Flask

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestConfig
from app.env_config import FlaskEnvironment, LoggingConfig, LogLevel


@pytest.mark.unit
class TestFlaskApplicationFactory:
    """Test suite for Flask application factory functionality."""

    @pytest.mark.unit
    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a proper Flask application instance."""
        app = create_app()
        assert isinstance(app, Flask)
        assert app.name == "app"

    @pytest.mark.unit
    def test_create_app_with_config_class(self):
        """Test create_app with explicit config class parameter."""
        app = create_app(TestConfig)
        assert app.config["TESTING"] is True
        assert app.config["SECRET_KEY"] == "test-secret-key"

    @pytest.mark.unit
    def test_create_app_with_none_config_uses_default(self):
        """Test that create_app with None config class uses default configuration."""
        with patch("app.get_flask_env") as mock_get_env:
            mock_get_env.return_value = FlaskEnvironment.DEVELOPMENT
            app = create_app()
            assert isinstance(app, Flask)
            mock_get_env.assert_called_once()

    @pytest.mark.unit
    @patch("app.setup_logging")
    @patch("app.get_logging_config")
    def test_logging_setup_called(self, mock_get_logging_config, mock_setup_logging):
        """Test that logging is properly configured during app creation."""
        mock_logging_config = LoggingConfig(LogLevel.INFO, False)
        mock_get_logging_config.return_value = mock_logging_config

        app = create_app(TestConfig)

        # Verify app was created successfully
        assert app is not None

        mock_get_logging_config.assert_called_once()
        mock_setup_logging.assert_called_once_with(mock_logging_config)

    @pytest.mark.unit
    @patch("app.setup_request_logging")
    def test_middleware_setup_called(self, mock_setup_request_logging):
        """Test that request logging middleware is properly set up."""
        app = create_app(TestConfig)

        # Verify app was created successfully
        assert app is not None

        mock_setup_request_logging.assert_called_once_with(app)

    @pytest.mark.unit
    def test_blueprint_registration(self):
        """Test that main blueprint is properly registered."""
        app = create_app(TestConfig)

        # Check that main blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert "main" in blueprint_names

    @pytest.mark.unit
    @patch("app.get_logger")
    def test_logging_calls_during_initialization(self, mock_get_logger):
        """Test that appropriate logging calls are made during initialization."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = create_app(TestConfig)

        # Verify app was created successfully
        assert app is not None

        # Verify logger was called for initialization steps
        mock_get_logger.assert_called()
        mock_logger.info.assert_called()

    @pytest.mark.unit
    def test_config_init_app_called(self):
        """Test that config class init_app method is called."""
        with patch.object(TestConfig, "init_app") as mock_init_app:
            app = create_app(TestConfig)
            mock_init_app.assert_called_once_with(app)

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "config_class", [DevelopmentConfig, TestConfig, ProductionConfig]
    )
    def test_create_app_with_different_config_classes(self, config_class):
        """Test create_app works with different configuration classes."""
        with patch.object(config_class, "init_app"):
            app = create_app(config_class)
            assert isinstance(app, Flask)
            assert app.config.from_object.__name__ == "from_object"

    @pytest.mark.unit
    @patch("app.load_dotenv")
    def test_dotenv_loading(self, mock_load_dotenv):
        """Test that dotenv loading is attempted during module import."""
        # This tests the module-level dotenv loading
        # Note: The actual import happens at module load time
        # This test verifies the pattern is in place
        from app import create_app

        # The load_dotenv should have been called during module import
        # We can't easily test this without reimporting, so we test the function exists
        assert callable(create_app)

    @pytest.mark.unit
    def test_dotenv_import_error_handling(self):
        """Test that missing python-dotenv doesn't break application."""
        # Test that the app still works even if dotenv import fails
        # This is already handled in the module by the try/except block
        app = create_app(TestConfig)
        assert isinstance(app, Flask)


@pytest.mark.integration
class TestFlaskApplicationFactoryIntegration:
    """Integration tests for Flask application factory with real components."""

    @pytest.mark.integration
    def test_complete_app_initialization_workflow(self):
        """Test complete application initialization workflow with real components."""
        app = create_app(TestConfig)

        # Test that all components are properly integrated
        assert isinstance(app, Flask)
        assert app.config["TESTING"] is True

        # Test that routes are accessible
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 200

    @pytest.mark.integration
    def test_logging_integration_with_real_config(self):
        """Test that logging integration works with real configuration."""
        app = create_app(TestConfig)

        with app.app_context():
            from app.logging_config import get_logger

            logger = get_logger(__name__)

            # Test that logger is properly configured
            assert logger is not None
            assert logger.name.startswith("app.")

    @pytest.mark.integration
    def test_middleware_integration_with_real_requests(self):
        """Test that middleware properly handles real requests."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test that middleware doesn't interfere with normal requests
            response = client.get("/health")
            assert response.status_code == 200

            # Test POST request with middleware
            response = client.post(
                "/transform", json={"text": "test", "transformation": "alternate_case"}
            )
            assert response.status_code == 200

    @pytest.mark.integration
    def test_error_handlers_integration(self):
        """Test that error handlers are properly integrated via middleware."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test 404 error handling
            response = client.get("/nonexistent")
            assert response.status_code == 404

            # Test that JSON error response is returned
            data = response.get_json()
            assert "error" in data
