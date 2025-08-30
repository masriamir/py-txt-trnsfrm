"""Integration tests for key application workflows.

This module contains comprehensive integration tests that verify complete
workflows spanning multiple components, including application initialization,
request processing, text transformation, and error handling scenarios.
"""

import time
from unittest.mock import patch

import pytest
from flask import Flask

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestConfig


@pytest.mark.integration
class TestApplicationInitializationWorkflow:
    """Integration tests for complete application initialization workflow."""

    @pytest.mark.integration
    def test_complete_development_app_initialization(self):
        """Test complete development application initialization workflow."""
        app = create_app(DevelopmentConfig)

        # Verify app is properly configured
        assert isinstance(app, Flask)
        assert app.config["DEBUG"] is True
        assert app.config["TESTING"] is False

        # Verify blueprints are registered
        assert "main" in app.blueprints

        # Verify routes are accessible
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/health")
            assert response.status_code == 200

    @pytest.mark.integration
    def test_complete_test_app_initialization(self):
        """Test complete test application initialization workflow."""
        app = create_app(TestConfig)

        # Verify app is properly configured for testing
        assert isinstance(app, Flask)
        assert app.config["TESTING"] is True
        assert app.config["WTF_CSRF_ENABLED"] is False

        # Verify all endpoints work in test mode
        with app.test_client() as client:
            # Test GET endpoints
            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/health")
            assert response.status_code == 200

            # Test POST endpoint
            response = client.post(
                "/transform", json={"text": "test", "transformation": "alternate_case"}
            )
            assert response.status_code == 200

    @pytest.mark.integration
    @patch.dict("os.environ", {"SECRET_KEY": "test-production-secret"})
    def test_complete_production_app_initialization(self):
        """Test complete production application initialization workflow."""
        app = create_app(ProductionConfig)

        # Verify app is properly configured for production
        assert isinstance(app, Flask)
        assert app.config["DEBUG"] is False
        assert app.config["TESTING"] is False
        assert app.config["SECRET_KEY"] == "test-production-secret"

        # Verify production endpoints work
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

            data = response.get_json()
            assert data["status"] == "healthy"

    @pytest.mark.integration
    def test_logging_middleware_blueprint_integration(self):
        """Test integration of logging, middleware, and blueprint components."""
        app = create_app(TestConfig)

        # Verify all components work together
        with app.test_client() as client:
            # This request exercises:
            # 1. Logging configuration
            # 2. Request middleware (before_request)
            # 3. Blueprint routing
            # 4. Response middleware (after_request)
            response = client.get("/health")

            assert response.status_code == 200
            data = response.get_json()
            assert "status" in data
            assert "version" in data

    @pytest.mark.integration
    def test_error_handling_integration_workflow(self):
        """Test complete error handling workflow integration."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test 404 error handling workflow
            response = client.get("/nonexistent")
            assert response.status_code == 404

            data = response.get_json()
            assert data["error"] == "Not found"

            # Test invalid API request handling
            response = client.post("/transform", json={})
            assert response.status_code == 400

            data = response.get_json()
            assert "error" in data


@pytest.mark.integration
class TestTextTransformationWorkflow:
    """Integration tests for complete text transformation workflows."""

    @pytest.mark.integration
    def test_complete_transformation_workflow(self):
        """Test complete text transformation workflow from request to response."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test the complete workflow:
            # 1. HTTP request received
            # 2. Middleware logging starts
            # 3. Route handler processes request
            # 4. TextTransformer instantiated
            # 5. Transformation applied
            # 6. JSON response generated
            # 7. Middleware logging completes

            request_data = {"text": "Hello World", "transformation": "alternate_case"}
            response = client.post("/transform", json=request_data)

            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True
            assert data["original_text"] == "Hello World"
            assert data["transformed_text"] == "HeLLo WoRLd"
            assert data["transformation"] == "alternate_case"

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "text,transformation",
        [
            ("Hello", "alternate_case"),
            ("World", "backwards"),
            ("Test", "l33t_speak"),
            ("Message", "rot13"),
        ],
    )
    def test_multiple_transformation_types_workflow(self, text, transformation):
        """Test workflow with multiple transformation types."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.post(
                "/transform", json={"text": text, "transformation": transformation}
            )

            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True
            assert data["original_text"] == text
            assert data["transformation"] == transformation
            assert "transformed_text" in data

    @pytest.mark.integration
    def test_transformation_error_handling_workflow(self):
        """Test complete transformation error handling workflow."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test invalid transformation type
            response = client.post(
                "/transform",
                json={"text": "Hello", "transformation": "invalid_transform"},
            )

            assert response.status_code == 400

            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Unknown transformation: invalid_transform"

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "text,transformation",
        [
            ("", "alternate_case"),  # Empty string
            ("A", "backwards"),  # Single character
            ("   ", "l33t_speak"),  # Whitespace only
            ("123", "rot13"),  # Numbers only
            ("!@#$", "alternate_case"),  # Special characters only
        ],
    )
    def test_edge_case_transformations_workflow(self, text, transformation):
        """Test transformation workflow with edge cases."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.post(
                "/transform", json={"text": text, "transformation": transformation}
            )

            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True
            assert data["original_text"] == text

    @pytest.mark.integration
    def test_large_text_transformation_workflow(self):
        """Test transformation workflow with large text input."""
        app = create_app(TestConfig)

        # Test with moderately large text
        large_text = "This is a test sentence. " * 100  # 2500 characters

        with app.test_client() as client:
            response = client.post(
                "/transform",
                json={"text": large_text, "transformation": "alternate_case"},
            )

            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True
            assert len(data["transformed_text"]) == len(large_text)


@pytest.mark.integration
class TestRequestResponseWorkflow:
    """Integration tests for complete request/response workflows."""

    @pytest.mark.integration
    def test_request_logging_workflow(self):
        """Test complete request logging workflow."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test that requests are properly logged through the complete workflow
            start_time = time.time()

            response = client.get(
                "/health",
                headers={
                    "User-Agent": "Test-Agent/1.0",
                    "X-Forwarded-For": "192.168.1.1",
                },
            )

            end_time = time.time()

            assert response.status_code == 200
            assert end_time - start_time < 1.0  # Should be fast

            # Verify response structure
            data = response.get_json()
            assert data["status"] == "healthy"

    @pytest.mark.integration
    def test_concurrent_requests_workflow(self):
        """Test workflow with multiple concurrent requests."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Simulate multiple requests in quick succession
            responses = []

            for i in range(5):
                response = client.post(
                    "/transform",
                    json={"text": f"Test {i}", "transformation": "backwards"},
                )
                responses.append(response)

            # All requests should succeed
            for i, response in enumerate(responses):
                assert response.status_code == 200

                data = response.get_json()
                assert data["success"] is True
                assert data["original_text"] == f"Test {i}"

    @pytest.mark.integration
    def test_session_context_workflow(self):
        """Test workflow with Flask session context."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test multiple requests in the same session
            response1 = client.get("/health")
            response2 = client.get("/")
            response3 = client.post(
                "/transform",
                json={"text": "Session test", "transformation": "alternate_case"},
            )

            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response3.status_code == 200

            # Each request should be independent
            data = response3.get_json()
            assert data["original_text"] == "Session test"


@pytest.mark.integration
class TestConfigurationIntegrationWorkflow:
    """Integration tests for configuration workflows."""

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "config_class,expected_debug,expected_testing",
        [
            (DevelopmentConfig, True, False),  # debug=True, testing=False
            (TestConfig, False, True),  # debug=False, testing=True
        ],
    )
    def test_environment_based_configuration_workflow(
        self, config_class, expected_debug, expected_testing
    ):
        """Test configuration workflow based on environment."""
        app = create_app(config_class)

        assert app.config["DEBUG"] == expected_debug
        assert app.config["TESTING"] == expected_testing

        # Test that configuration affects behavior
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

    @pytest.mark.integration
    def test_logging_configuration_integration_workflow(self):
        """Test logging configuration integration workflow."""
        app = create_app(TestConfig)

        # Test that logging is properly configured and works
        with app.app_context():
            from app.logging_config import get_logger

            logger = get_logger("integration_test")

            # Should be able to log at all levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

            # Logger should have proper configuration
            assert logger.name.startswith("app.")

    @pytest.mark.integration
    def test_middleware_configuration_integration_workflow(self):
        """Test middleware configuration integration workflow."""
        app = create_app(TestConfig)

        # Test that middleware is properly configured
        assert len(app.before_request_funcs) > 0
        assert len(app.after_request_funcs) > 0

        # Test that error handlers are configured
        assert 404 in app.error_handler_spec[None]
        assert 500 in app.error_handler_spec[None]

        # Test middleware functionality
        with app.test_client() as client:
            # Test normal request
            response = client.get("/health")
            assert response.status_code == 200

            # Test error handling
            response = client.get("/nonexistent")
            assert response.status_code == 404


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests for complete application workflows."""

    @pytest.mark.integration
    def test_complete_application_lifecycle(self):
        """Test complete application lifecycle from startup to shutdown."""
        # Test application creation
        app = create_app(TestConfig)
        assert isinstance(app, Flask)

        # Test application can handle requests
        with app.test_client() as client:
            # Test static content
            response = client.get("/")
            assert response.status_code == 200

            # Test health monitoring
            response = client.get("/health")
            assert response.status_code == 200

            # Test core functionality
            response = client.post(
                "/transform",
                json={"text": "End-to-end test", "transformation": "alternate_case"},
            )
            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True

    @pytest.mark.integration
    def test_error_recovery_workflow(self):
        """Test application error recovery workflow."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Test that application recovers from errors

            # Generate an error
            response = client.post("/transform", json={"invalid": "data"})
            assert response.status_code == 400

            # Test that application still works after error
            response = client.get("/health")
            assert response.status_code == 200

            # Test that valid requests still work
            response = client.post(
                "/transform",
                json={"text": "Recovery test", "transformation": "backwards"},
            )
            assert response.status_code == 200

    @pytest.mark.integration
    def test_performance_under_load_workflow(self):
        """Test application performance under simulated load."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Simulate moderate load
            start_time = time.time()

            for i in range(10):
                response = client.post(
                    "/transform",
                    json={"text": f"Load test {i}", "transformation": "alternate_case"},
                )
                assert response.status_code == 200

            end_time = time.time()
            total_time = end_time - start_time

            # Should handle 10 requests reasonably quickly
            assert total_time < 5.0  # 5 seconds max for 10 requests
            average_time = total_time / 10
            assert average_time < 0.5  # 500ms average per request

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "text,transformation,expected_start",
        [
            ("Hello", "alternate_case", "HeLLo"),
            ("World", "backwards", "dlroW"),
            ("Python", "l33t_speak", "Py7h0n"),
        ],
    )
    def test_data_consistency_workflow(self, text, transformation, expected_start):
        """Test data consistency across multiple requests."""
        app = create_app(TestConfig)

        with app.test_client() as client:
            response = client.post(
                "/transform", json={"text": text, "transformation": transformation}
            )

            assert response.status_code == 200

            data = response.get_json()
            assert data["success"] is True
            assert data["original_text"] == text
            assert data["transformation"] == transformation

            # Verify transformation is consistent
            result = data["transformed_text"]
            if transformation == "alternate_case":
                assert result.startswith(expected_start)
            elif transformation == "backwards":
                assert result == expected_start
            elif transformation == "l33t_speak":
                assert "3" in result or "0" in result or "7" in result
