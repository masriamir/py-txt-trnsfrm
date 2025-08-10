"""Enhanced API tests with mocking and HTTP service testing."""
import json
import pytest
import responses
from unittest.mock import patch, MagicMock
from faker import Faker
from hypothesis import given, strategies as st

from tests.data.test_data import sample_texts, expected_results, edge_cases


fake = Faker()


@pytest.mark.api
class TestTransformAPI:
    """Test suite for the transform API with comprehensive mocking."""

    @pytest.mark.smoke
    def test_transform_endpoint_basic(self, client):
        """Basic smoke test for transform endpoint."""
        response = client.get('/')
        assert response.status_code == 200

    @pytest.mark.api
    def test_transform_with_sample_data(self, client):
        """Test transformation using predefined sample data."""
        for text_key, text_value in sample_texts.items():
            if text_key == "empty":  # Skip empty for this test
                continue

            data = {
                'text': text_value,
                'transformation': 'alternate_case'
            }
            response = client.post('/transform',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert 'transformed_text' in result

    @pytest.mark.api
    @pytest.mark.slow
    def test_transform_performance_data(self, client):
        """Test transformation with large text data."""
        large_text = "Performance test text. " * 1000
        data = {
            'text': large_text,
            'transformation': 'alternate_case'
        }
        response = client.post('/transform',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    @pytest.mark.api
    def test_transform_edge_cases(self, client):
        """Test transformation with edge case data."""
        for case_name, case_text in edge_cases.items():
            data = {
                'text': case_text,
                'transformation': 'alternate_case'
            }
            response = client.post('/transform',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True

    @pytest.mark.api
    @patch('app.utils.text_transformers.TextTransformer.alternate_case')
    def test_transform_with_mocked_transformer(self, mock_transform, client):
        """Test API with mocked transformer to isolate API logic."""
        mock_transform.return_value = "MOCKED_RESULT"

        data = {
            'text': 'test text',
            'transformation': 'alternate_case'
        }
        response = client.post('/transform',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['transformed_text'] == "MOCKED_RESULT"
        mock_transform.assert_called_once_with('test text')

    @pytest.mark.api
    @responses.activate
    def test_external_service_mock(self, client):
        """Example of mocking external HTTP services."""
        # This would be used if your app made external HTTP calls
        responses.add(
            responses.GET,
            'https://api.example.com/validate',
            json={'valid': True},
            status=200
        )

        # Your test logic here - this is just an example
        # If your app had external dependencies, you'd test them here
        assert True  # Placeholder

    @pytest.mark.api
    @given(text=st.text(min_size=1, max_size=100))
    def test_transform_property_based(self, client, text):
        """Property-based testing with Hypothesis."""
        data = {
            'text': text,
            'transformation': 'alternate_case'
        }
        response = client.post('/transform',
                              data=json.dumps(data),
                              content_type='application/json')

        # Property: API should never crash with valid input
        assert response.status_code in [200, 400]  # Either success or client error

        if response.status_code == 200:
            result = json.loads(response.data)
            assert 'success' in result
            assert 'transformed_text' in result

    @pytest.mark.api
    def test_transform_with_faker_data(self, client):
        """Test transformation with dynamically generated fake data."""
        fake_text = fake.text(max_nb_chars=200)
        data = {
            'text': fake_text,
            'transformation': 'alternate_case'
        }
        response = client.post('/transform',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert result['original_text'] == fake_text


@pytest.mark.network
class TestNetworkMocking:
    """Tests for network-related functionality with mocking."""

    @pytest.mark.network
    @responses.activate
    def test_mock_external_api_call(self):
        """Example of how to mock external API calls."""
        responses.add(
            responses.POST,
            'https://httpbin.org/post',
            json={'success': True, 'data': 'mocked'},
            status=200
        )

        # If your app made external requests, test them here
        # import requests
        # response = requests.post('https://httpbin.org/post', json={'test': 'data'})
        # assert response.json()['success'] is True
        pass
