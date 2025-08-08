import json


def test_index_page(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Text Transformer' in response.data
    assert b'Transform your text' in response.data


def test_transform_text_success(client):
    """Test successful text transformation."""
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


def test_transform_text_missing_data(client):
    """Test transformation with missing data."""
    response = client.post('/transform',
                          data=json.dumps({}),
                          content_type='application/json')

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result


def test_transform_text_invalid_transformation(client):
    """Test transformation with invalid transformation type."""
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
