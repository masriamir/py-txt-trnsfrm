"""Unit tests for Flask routes module.

This module contains comprehensive unit tests for Flask routes,
including the index page, health check endpoint, and transform API endpoint,
with proper mocking and isolation of dependencies.
"""

import json
from unittest.mock import Mock, patch, MagicMock
import pytest
from flask import Flask

from app.main.routes import index, health_check, transform_text


@pytest.mark.unit
class TestIndexRoute:
    """Test suite for index route functionality."""

    @pytest.mark.unit
    @patch("app.main.routes.render_template")
    @patch("app.main.routes.get_logger")
    def test_index_route_renders_template(self, mock_get_logger, mock_render_template):
        """Test that index route renders the correct template."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_render_template.return_value = "<html>Index Page</html>"
        
        result = index()
        
        mock_render_template.assert_called_once_with("index.html")
        mock_logger.info.assert_called_once_with("Index page requested")
        assert result == "<html>Index Page</html>"

    @pytest.mark.unit
    @patch("app.main.routes.get_logger")
    def test_index_route_logging(self, mock_get_logger):
        """Test that index route properly logs requests."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        with patch("app.main.routes.render_template", return_value="test"):
            index()
        
        mock_get_logger.assert_called_once_with("app.main.routes")
        mock_logger.info.assert_called_once_with("Index page requested")


@pytest.mark.unit
class TestHealthCheckRoute:
    """Test suite for health check route functionality."""

    @pytest.mark.unit
    @patch("app.main.routes.get_application_version")
    def test_health_check_success(self, mock_get_version):
        """Test successful health check response."""
        mock_get_version.return_value = "1.0.0"
        
        response, status_code = health_check()
        
        assert status_code == 200
        assert response.json["status"] == "healthy"
        assert response.json["service"] == "py-txt-trnsfrm"
        assert response.json["version"] == "1.0.0"
        mock_get_version.assert_called_once()

    @pytest.mark.unit
    @patch("app.main.routes.get_application_version")
    @patch("app.main.routes.get_logger")
    def test_health_check_exception_handling(self, mock_get_logger, mock_get_version):
        """Test health check exception handling."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_get_version.side_effect = Exception("Version error")
        
        response, status_code = health_check()
        
        assert status_code == 503
        assert response.json["status"] == "unhealthy"
        assert response.json["error"] == "Version error"
        mock_logger.error.assert_called_once_with("Health check failed: Version error")

    @pytest.mark.unit
    @patch("app.main.routes.get_application_version")
    def test_health_check_version_types(self, mock_get_version):
        """Test health check with different version types."""
        test_versions = ["1.0.0", "2.1.0-beta", "unknown", ""]
        
        for version in test_versions:
            mock_get_version.return_value = version
            
            response, status_code = health_check()
            
            assert status_code == 200
            assert response.json["version"] == version

    @pytest.mark.unit
    @patch("app.main.routes.jsonify")
    @patch("app.main.routes.get_application_version")
    def test_health_check_json_response_structure(self, mock_get_version, mock_jsonify):
        """Test that health check uses proper JSON response structure."""
        mock_get_version.return_value = "1.0.0"
        mock_jsonify.return_value = Mock()
        
        health_check()
        
        # Verify jsonify was called with correct structure
        mock_jsonify.assert_called_with({
            "status": "healthy",
            "service": "py-txt-trnsfrm", 
            "version": "1.0.0"
        })


@pytest.mark.unit
class TestTransformRoute:
    """Test suite for transform route functionality."""

    @pytest.fixture
    def mock_request_data(self):
        """Fixture providing mock request data."""
        return {"text": "Hello World", "transformation": "alternate_case"}

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.TextTransformer")
    @patch("app.main.routes.get_logger")
    def test_transform_text_success(self, mock_get_logger, mock_transformer_class, mock_request, mock_request_data):
        """Test successful text transformation."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = mock_request_data
        
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "HeLLo WoRLd"
        mock_transformer_class.return_value = mock_transformer
        
        response, status_code = transform_text()
        
        assert status_code == 200
        response_data = response.json
        assert response_data["success"] is True
        assert response_data["original_text"] == "Hello World"
        assert response_data["transformed_text"] == "HeLLo WoRLd"
        assert response_data["transformation"] == "alternate_case"
        
        mock_transformer.transform.assert_called_once_with("Hello World", "alternate_case")

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_missing_json_data(self, mock_get_logger, mock_request):
        """Test transform endpoint with missing JSON data."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = None
        
        response, status_code = transform_text()
        
        assert status_code == 400
        assert response.json["error"] == "Missing text or transformation type"
        mock_logger.warning.assert_called_with(
            "Invalid transformation request - missing text or transformation type"
        )

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_missing_text_field(self, mock_get_logger, mock_request):
        """Test transform endpoint with missing text field."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = {"transformation": "alternate_case"}
        
        response, status_code = transform_text()
        
        assert status_code == 400
        assert response.json["error"] == "Missing text or transformation type"

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_missing_transformation_field(self, mock_get_logger, mock_request):
        """Test transform endpoint with missing transformation field."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = {"text": "Hello World"}
        
        response, status_code = transform_text()
        
        assert status_code == 400
        assert response.json["error"] == "Missing text or transformation type"

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.TextTransformer")
    @patch("app.main.routes.get_logger")
    def test_transform_text_invalid_transformation(self, mock_get_logger, mock_transformer_class, mock_request, mock_request_data):
        """Test transform endpoint with invalid transformation type."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = mock_request_data
        
        mock_transformer = Mock()
        mock_transformer.transform.side_effect = ValueError("Invalid transformation")
        mock_transformer_class.return_value = mock_transformer
        
        response, status_code = transform_text()
        
        assert status_code == 400
        assert response.json["error"] == "Invalid transformation"
        mock_logger.error.assert_called_with(
            "Transformation failed - Type: 'alternate_case', Error: Invalid transformation"
        )

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_request_logging(self, mock_get_logger, mock_request, mock_request_data):
        """Test that transform endpoint properly logs requests."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = mock_request_data
        
        with patch("app.main.routes.TextTransformer") as mock_transformer_class:
            mock_transformer = Mock()
            mock_transformer.transform.return_value = "result"
            mock_transformer_class.return_value = mock_transformer
            
            transform_text()
        
        # Check logging calls
        mock_logger.info.assert_any_call("Text transformation request received")
        mock_logger.info.assert_any_call("Transformation request - Type: 'alternate_case', Text: 'Hello World'")
        mock_logger.info.assert_any_call("Transformation 'alternate_case' completed successfully")

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_long_text_truncation_in_logs(self, mock_get_logger, mock_request):
        """Test that long text is truncated in log messages."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        long_text = "A" * 150  # Text longer than 100 characters
        request_data = {"text": long_text, "transformation": "alternate_case"}
        mock_request.get_json.return_value = request_data
        
        with patch("app.main.routes.TextTransformer") as mock_transformer_class:
            mock_transformer = Mock()
            mock_transformer.transform.return_value = "result"
            mock_transformer_class.return_value = mock_transformer
            
            transform_text()
        
        # Check that text is truncated in logs
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        transformation_log = next((call for call in log_calls if "Transformation request" in call), None)
        assert transformation_log is not None
        assert "..." in transformation_log  # Should contain truncation indicator

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_debug_logging(self, mock_get_logger, mock_request, mock_request_data):
        """Test debug logging in transform endpoint."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = mock_request_data
        
        with patch("app.main.routes.TextTransformer") as mock_transformer_class:
            mock_transformer = Mock()
            mock_transformer.transform.return_value = "transformed result"
            mock_transformer_class.return_value = mock_transformer
            
            transform_text()
        
        # Check debug logging calls
        mock_logger.debug.assert_any_call("Full text length: 11 characters")
        mock_logger.debug.assert_any_call("Result length: 18 characters")

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.TextTransformer")
    @patch("app.main.routes.get_logger")
    def test_transform_text_empty_string_handling(self, mock_get_logger, mock_transformer_class, mock_request):
        """Test transform endpoint with empty string input."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = {"text": "", "transformation": "alternate_case"}
        
        mock_transformer = Mock()
        mock_transformer.transform.return_value = ""
        mock_transformer_class.return_value = mock_transformer
        
        response, status_code = transform_text()
        
        assert status_code == 200
        response_data = response.json
        assert response_data["success"] is True
        assert response_data["original_text"] == ""
        assert response_data["transformed_text"] == ""

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.jsonify")
    @patch("app.main.routes.TextTransformer")
    @patch("app.main.routes.get_logger")
    def test_transform_text_json_response_structure(self, mock_get_logger, mock_transformer_class, mock_jsonify, mock_request, mock_request_data):
        """Test that transform endpoint returns properly structured JSON."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = mock_request_data
        
        mock_transformer = Mock()
        mock_transformer.transform.return_value = "HeLLo WoRLd"
        mock_transformer_class.return_value = mock_transformer
        mock_jsonify.return_value = Mock()
        
        transform_text()
        
        # Verify jsonify was called with correct structure
        expected_response = {
            "success": True,
            "original_text": "Hello World",
            "transformed_text": "HeLLo WoRLd",
            "transformation": "alternate_case",
        }
        mock_jsonify.assert_called_with(expected_response)

    @pytest.mark.unit
    @patch("app.main.routes.request")
    @patch("app.main.routes.get_logger")
    def test_transform_text_empty_json_object(self, mock_get_logger, mock_request):
        """Test transform endpoint with empty JSON object."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_request.get_json.return_value = {}
        
        response, status_code = transform_text()
        
        assert status_code == 400
        assert response.json["error"] == "Missing text or transformation type"


@pytest.mark.integration
class TestRoutesIntegration:
    """Integration tests for routes with real Flask application."""

    @pytest.mark.integration
    def test_index_route_integration(self):
        """Test index route integration with real Flask app."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            assert b"Text Transformer" in response.data

    @pytest.mark.integration
    def test_health_check_integration(self):
        """Test health check integration with real Flask app."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.get_json()
            assert data["status"] == "healthy"
            assert data["service"] == "py-txt-trnsfrm"
            assert "version" in data

    @pytest.mark.integration
    def test_transform_route_integration(self):
        """Test transform route integration with real Flask app."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            response = client.post("/transform", 
                                 json={"text": "Hello", "transformation": "alternate_case"})
            assert response.status_code == 200
            
            data = response.get_json()
            assert data["success"] is True
            assert "transformed_text" in data
            assert data["original_text"] == "Hello"

    @pytest.mark.integration
    def test_routes_error_handling_integration(self):
        """Test routes error handling integration."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            # Test invalid transformation
            response = client.post("/transform", 
                                 json={"text": "Hello", "transformation": "invalid"})
            assert response.status_code == 400
            
            data = response.get_json()
            assert "error" in data

    @pytest.mark.integration
    def test_routes_with_middleware_integration(self):
        """Test that routes work properly with middleware."""
        from app import create_app
        from app.config import TestConfig
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            # Multiple requests to test middleware consistency
            for i in range(3):
                response = client.get("/health")
                assert response.status_code == 200
                
                response = client.post("/transform", 
                                     json={"text": f"Test {i}", "transformation": "backwards"})
                assert response.status_code == 200