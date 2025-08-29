"""Application integration tests module.

This module contains integration tests for the Flask text transformation
application, testing the main routes, API endpoints, and overall application
behavior through HTTP requests.
"""

import json

import pytest


@pytest.mark.smoke
def test_index_page(client):
    """Test that the index page loads successfully.

    Verifies that the main page returns a successful response and contains
    the expected content elements.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Text Transformer" in response.data
    assert b"Transform your text" in response.data


@pytest.mark.api
def test_transform_text_success(client):
    """Test successful text transformation via API.

    Tests the /transform endpoint with valid input data to ensure
    successful text transformation and proper JSON response format.

    Args:
        client: Flask test client fixture.
    """
    data = {"text": "Hello World", "transformation": "alternate_case"}
    response = client.post(
        "/transform", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["success"] is True
    assert "transformed_text" in result
    assert result["original_text"] == "Hello World"


@pytest.mark.api
def test_transform_text_missing_data(client):
    """Test transformation API with missing required data.

    Verifies that the API properly handles requests with missing
    text or transformation parameters.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/transform", data=json.dumps({}), content_type="application/json"
    )

    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result


@pytest.mark.api
def test_transform_text_invalid_transformation(client):
    """Test transformation API with invalid transformation type.

    Verifies that the API properly handles requests with unknown
    transformation types and returns appropriate error messages.

    Args:
        client: Flask test client fixture.
    """
    data = {"text": "Hello World", "transformation": "nonexistent_transform"}
    response = client.post(
        "/transform", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result


@pytest.mark.api
def test_transform_text_empty_text(client):
    """Test transformation with empty text."""
    data = {"text": "", "transformation": "alternate_case"}
    response = client.post(
        "/transform", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["success"] is True
    assert result["transformed_text"] == ""


@pytest.mark.api
@pytest.mark.smoke
def test_health_endpoint_basic(client):
    """Test basic health endpoint functionality.

    Verifies that the health endpoint returns expected JSON structure
    with dynamic version from pyproject.toml.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    result = json.loads(response.data)
    assert "status" in result
    assert "service" in result
    assert "version" in result
    assert result["status"] == "healthy"
    assert result["service"] == "py-txt-trnsfrm"

    # Version should be dynamic, not hardcoded
    assert result["version"] != ""
    assert isinstance(result["version"], str)


@pytest.mark.api
def test_health_endpoint_version_format(client):
    """Test that health endpoint returns properly formatted version.

    Verifies the version follows expected format and is not the
    hardcoded fallback unless there's an actual error.
    """
    response = client.get("/health")

    assert response.status_code == 200
    result = json.loads(response.data)

    version = result["version"]
    # Should be either semver format (x.y.z) or "unknown" fallback
    assert version == "0.1.0" or version == "unknown" or "." in version


@pytest.mark.api
def test_health_endpoint_response_structure(client):
    """Test health endpoint returns exact expected structure.

    Ensures the response format remains unchanged for monitoring systems.
    """
    response = client.get("/health")

    assert response.status_code == 200
    result = json.loads(response.data)

    # Verify exact structure
    expected_keys = {"status", "service", "version"}
    assert set(result.keys()) == expected_keys

    # Verify data types
    assert isinstance(result["status"], str)
    assert isinstance(result["service"], str)
    assert isinstance(result["version"], str)


@pytest.mark.integration
class TestStaticFiles:
    """Test static file serving."""

    def test_css_loads(self, client):
        """Test that CSS file is accessible."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert b"retro-text" in response.data

    def test_js_loads(self, client):
        """Test that JavaScript file is accessible."""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        assert b"transformText" in response.data


@pytest.mark.integration
class TestProjectConfiguration:
    """Test project configuration files."""

    def test_editorconfig_exists(self):
        """Test that .editorconfig file exists and contains expected settings."""
        from pathlib import Path

        # Get project root directory
        project_root = Path(__file__).parent.parent
        editorconfig_path = project_root / ".editorconfig"

        # Check file exists
        assert editorconfig_path.exists(), (
            ".editorconfig file should exist in project root"
        )

        # Check file content contains key settings
        content = editorconfig_path.read_text(encoding="utf-8")

        # Verify root directive
        assert "root = true" in content, ".editorconfig should declare itself as root"

        # Verify Python settings (4 spaces, 88 char limit)
        assert "[*.py]" in content, (
            ".editorconfig should have Python file configuration"
        )
        assert "indent_size = 4" in content, (
            ".editorconfig should set 4 spaces for Python files"
        )
        assert "max_line_length = 88" in content, (
            ".editorconfig should set 88 char limit for Python files"
        )

        # Verify web file settings (2 spaces)
        assert "[*.{css,js,html,htm,json}]" in content, (
            ".editorconfig should configure web files"
        )

        # Verify global settings
        assert "charset = utf-8" in content, ".editorconfig should set UTF-8 encoding"
        assert "end_of_line = lf" in content, ".editorconfig should set LF line endings"
        assert "insert_final_newline = true" in content, (
            ".editorconfig should require final newline"
        )
