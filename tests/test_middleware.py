"""Unit tests for request logging middleware module.

This module contains comprehensive unit tests for request logging middleware,
error handlers, request/response logging, timing, and client information capture.
"""

import time
from unittest.mock import Mock, patch

import pytest
from flask import Flask, g

from app.middleware import setup_request_logging


@pytest.mark.unit
class TestMiddlewareSetup:
    """Test suite for middleware setup functionality."""

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_setup_request_logging_registers_handlers(self, mock_get_logger):
        """Test that setup_request_logging registers all required handlers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)

        setup_request_logging(app)

        # Should have registered before_request and after_request handlers
        assert len(app.before_request_funcs) > 0
        assert len(app.after_request_funcs) > 0

        # Should have registered error handlers
        assert 404 in app.error_handler_spec[None]
        assert 500 in app.error_handler_spec[None]

    @pytest.mark.unit
    @patch("app.middleware.logger")
    def test_middleware_logger_initialization(self, mock_logger):
        """Test that middleware properly initializes logger."""
        app = Flask(__name__)
        setup_request_logging(app)

        mock_logger.info.assert_called_with("Request logging middleware initialized")


@pytest.mark.unit
class TestRequestLogging:
    """Test suite for request logging functionality."""

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    @patch("time.time")
    def test_log_request_start_basic_logging(self, mock_time, mock_get_logger):
        """Test basic request start logging functionality."""
        mock_time.return_value = 123456789.0
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/test", method="GET"):
            # Trigger before_request handler
            for func in app.before_request_funcs[None]:
                func()

            # Should set start time in g
            assert hasattr(g, "start_time")
            assert g.start_time == 123456789.0

            # Should log request start
            mock_logger.info.assert_called_with("Request started: GET /test")

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_start_client_ip_extraction(self, mock_get_logger):
        """Test client IP extraction from headers."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        # Test with X-Forwarded-For header
        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        with app.test_request_context("/test", headers=headers):
            for func in app.before_request_funcs[None]:
                func()

            # Should extract first IP from X-Forwarded-For
            mock_logger.debug.assert_any_call("Client IP: 192.168.1.1")

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_start_query_parameters(self, mock_get_logger):
        """Test logging of query parameters."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/test?param1=value1&param2=value2"):
            for func in app.before_request_funcs[None]:
                func()

            # Should log query parameters
            mock_logger.debug.assert_any_call(
                "Query params: {'param1': ['value1'], 'param2': ['value2']}"
            )

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_start_headers_in_debug(self, mock_get_logger):
        """Test that headers are logged in debug mode."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        app.debug = True
        setup_request_logging(app)

        headers = {
            "User-Agent": "TestAgent",
            "Authorization": "Bearer secret",  # Should be filtered out
            "Content-Type": "application/json",
        }

        with app.test_request_context("/test", headers=headers):
            for func in app.before_request_funcs[None]:
                func()

            # Should log safe headers only
            debug_calls = [
                call
                for call in mock_logger.debug.call_args_list
                if "Request headers:" in str(call)
            ]
            assert len(debug_calls) > 0

            # Authorization header should be filtered out
            headers_call = str(debug_calls[0])
            assert "Authorization" not in headers_call
            assert "User-Agent" in headers_call

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_start_user_agent_logging(self, mock_get_logger):
        """Test User-Agent header logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        headers = {"User-Agent": "Mozilla/5.0 TestBrowser"}
        with app.test_request_context("/test", headers=headers):
            for func in app.before_request_funcs[None]:
                func()

            mock_logger.debug.assert_any_call("User Agent: Mozilla/5.0 TestBrowser")

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_start_referrer_logging(self, mock_get_logger):
        """Test Referrer header logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        headers = {"Referer": "https://example.com/previous-page"}
        with app.test_request_context("/test", headers=headers):
            for func in app.before_request_funcs[None]:
                func()

            mock_logger.debug.assert_any_call(
                "Referrer: https://example.com/previous-page"
            )


@pytest.mark.unit
class TestResponseLogging:
    """Test suite for response logging functionality."""

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    @patch("time.time")
    def test_log_request_end_basic_logging(self, mock_time, mock_get_logger):
        """Test basic request end logging functionality."""
        mock_time.side_effect = [123456789.0, 123456789.5]  # 0.5 second duration
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/test", method="POST"):
            # Set start time
            g.start_time = 123456789.0

            # Create mock response
            response = Mock()
            response.status_code = 200
            response.headers = {}
            response.content_length = None

            # Trigger after_request handler
            for func in app.after_request_funcs[None]:
                result = func(response)

            # Should return original response
            assert result is response

            # Should log request completion
            mock_logger.info.assert_called_with(
                "Request completed: POST /test - Status: 200 - Duration: 0.500s - IP: None"
            )

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "status_code,expected_level", [(200, "info"), (404, "warning"), (500, "error")]
    )
    @patch("app.middleware.get_logger")
    def test_log_request_end_status_code_log_levels(
        self, mock_get_logger, status_code, expected_level
    ):
        """Test that different status codes use appropriate log levels."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/test"):
            g.start_time = time.time()

            response = Mock()
            response.status_code = status_code
            response.headers = {}
            response.content_length = None

            for func in app.after_request_funcs[None]:
                func(response)

            # Check that appropriate log level was used
            log_method = getattr(mock_logger, expected_level)
            assert log_method.called

    @pytest.mark.unit
    @patch("app.middleware.logger")
    def test_log_request_end_response_details_in_debug(self, mock_logger):
        """Test that response details are logged in debug mode."""
        app = Flask(__name__)
        app.debug = True
        setup_request_logging(app)

        with app.test_request_context("/test"):
            g.start_time = time.time()

            response = Mock()
            response.status_code = 200
            response.headers = {"Content-Type": "application/json"}
            response.content_length = 1024

            for func in app.after_request_funcs[None]:
                func(response)

            # Should log response headers and size in debug mode
            mock_logger.debug.assert_any_call(
                "Response headers: {'Content-Type': 'application/json'}"
            )
            mock_logger.debug.assert_any_call("Response size: 1024 bytes")

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_log_request_end_client_ip_extraction(self, mock_get_logger):
        """Test client IP extraction in response logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        with app.test_request_context("/test", headers=headers):
            g.start_time = time.time()

            response = Mock()
            response.status_code = 200
            response.headers = {}
            response.content_length = None

            for func in app.after_request_funcs[None]:
                func(response)

            # Should extract first IP from X-Forwarded-For
            log_calls = mock_logger.info.call_args_list
            log_message = str(log_calls[-1])
            assert "IP: 192.168.1.1" in log_message


@pytest.mark.unit
class TestErrorHandlers:
    """Test suite for error handler functionality."""

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_404_error_handler(self, mock_get_logger):
        """Test 404 error handler functionality."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        headers = {"User-Agent": "TestAgent"}
        with app.test_request_context("/nonexistent", headers=headers):
            # Get 404 error handler
            error_handler = app.error_handler_spec[None][404][Exception]

            error = Mock()
            response, status_code = error_handler(error)

            assert status_code == 404
            assert response == {"error": "Not found"}

            # Should log 404 error with details
            mock_logger.warning.assert_called()
            log_call = mock_logger.warning.call_args[0][0]
            assert "404 Not Found" in log_call
            assert "/nonexistent" in log_call
            assert "TestAgent" in log_call

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_500_error_handler(self, mock_get_logger):
        """Test 500 error handler functionality."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/error"):
            # Get 500 error handler
            error_handler = app.error_handler_spec[None][500][Exception]

            error = Exception("Test error message")
            response, status_code = error_handler(error)

            assert status_code == 500
            assert response == {"error": "Internal server error"}

            # Should log 500 error with details
            mock_logger.error.assert_called()
            log_call = mock_logger.error.call_args[0][0]
            assert "500 Server Error" in log_call
            assert "/error" in log_call
            assert "Test error message" in log_call

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_error_handlers_client_ip_extraction(self, mock_get_logger):
        """Test that error handlers properly extract client IP."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        with app.test_request_context("/test", headers=headers):
            # Test 404 handler
            error_handler_404 = app.error_handler_spec[None][404][Exception]
            error_handler_404(Mock())

            # Should log client IP
            log_call = mock_logger.warning.call_args[0][0]
            assert "IP: 192.168.1.1" in log_call

    @pytest.mark.unit
    @patch("app.middleware.get_logger")
    def test_error_handlers_missing_user_agent(self, mock_get_logger):
        """Test error handlers handle missing User-Agent gracefully."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app = Flask(__name__)
        setup_request_logging(app)

        with app.test_request_context("/test"):  # No User-Agent header
            error_handler = app.error_handler_spec[None][404][Exception]
            error_handler(Mock())

            # Should handle missing User-Agent gracefully
            log_call = mock_logger.warning.call_args[0][0]
            assert "User Agent: Unknown" in log_call


@pytest.mark.integration
class TestMiddlewareIntegration:
    """Integration tests for middleware with Flask application."""

    @pytest.mark.integration
    def test_middleware_integration_with_real_requests(self):
        """Test middleware integration with real Flask requests."""
        from app import create_app
        from app.config import TestConfig

        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test successful request
            response = client.get("/health")
            assert response.status_code == 200

            # Test POST request
            response = client.post(
                "/transform", json={"text": "test", "transformation": "alternate_case"}
            )
            assert response.status_code == 200

    @pytest.mark.integration
    def test_middleware_integration_with_404_errors(self):
        """Test middleware 404 error handling integration."""
        from app import create_app
        from app.config import TestConfig

        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.get("/nonexistent-endpoint")
            assert response.status_code == 404

            data = response.get_json()
            assert data["error"] == "Not found"

    @pytest.mark.integration
    def test_middleware_timing_integration(self):
        """Test that middleware properly times requests."""
        from app import create_app
        from app.config import TestConfig

        app = create_app(TestConfig)

        with app.test_client() as client:
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()

            assert response.status_code == 200
            # Request should complete within reasonable time
            assert end_time - start_time < 1.0

    @pytest.mark.integration
    def test_middleware_with_different_http_methods(self):
        """Test middleware works with different HTTP methods."""
        from app import create_app
        from app.config import TestConfig

        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test GET
            response = client.get("/")
            assert response.status_code == 200

            # Test POST
            response = client.post(
                "/transform", json={"text": "test", "transformation": "alternate_case"}
            )
            assert response.status_code == 200

            # Test HEAD
            response = client.head("/health")
            assert response.status_code == 200

    @pytest.mark.integration
    def test_middleware_request_context_preservation(self):
        """Test that middleware preserves Flask request context."""
        from app import create_app
        from app.config import TestConfig

        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.get("/health?test=value")
            assert response.status_code == 200

            # Request context should be properly maintained
            data = response.get_json()
            assert "status" in data
            assert data["status"] == "healthy"
