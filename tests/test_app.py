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
    response = client.get('/')
    assert response.status_code == 200
    assert b'Text Transformer' in response.data
    assert b'Transform your text' in response.data


@pytest.mark.api
def test_transform_text_success(client):
    """Test successful text transformation via API.

    Tests the /transform endpoint with valid input data to ensure
    successful text transformation and proper JSON response format.

    Args:
        client: Flask test client fixture.
    """
    data = {
        'text': 'Hello World',
        'transformation': 'alternate_case'
    }
    response = client.post('/transform',
                          data=json.dumps(data),
                          content_type='application/json')

    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'transformed_text' in result
    assert result['original_text'] == 'Hello World'


@pytest.mark.api
def test_transform_text_missing_data(client):
    """Test transformation API with missing required data.

    Verifies that the API properly handles requests with missing
    text or transformation parameters.

    Args:
        client: Flask test client fixture.
    """
    response = client.post('/transform',
                          data=json.dumps({}),
                          content_type='application/json')

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


@pytest.mark.api
def test_transform_text_invalid_transformation(client):
    """Test transformation API with invalid transformation type.

    Verifies that the API properly handles requests with unknown
    transformation types and returns appropriate error messages.

    Args:
        client: Flask test client fixture.
    """
    data = {
        'text': 'Hello World',
        'transformation': 'nonexistent_transform'
    }
    response = client.post('/transform',
                          data=json.dumps(data),
                          content_type='application/json')

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


@pytest.mark.api
def test_transform_text_empty_text(client):
    """Test transformation with empty text."""
    data = {
        'text': '',
        'transformation': 'alternate_case'
    }
    response = client.post('/transform',
                          data=json.dumps(data),
                          content_type='application/json')

    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['transformed_text'] == ''


@pytest.mark.integration
class TestStaticFiles:
    """Test static file serving."""

    def test_css_loads(self, client):
        """Test that CSS file is accessible."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert b'retro-text' in response.data

    def test_js_loads(self, client):
        """Test that JavaScript file is accessible."""
        response = client.get('/static/js/app.js')
        assert response.status_code == 200
        assert b'transformText' in response.data
