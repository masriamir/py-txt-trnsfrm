"""API Performance Tests

This module contains performance tests for the py-txt-trnsfrm API.
These tests can be run standalone or integrated into a GitHub Actions workflow.

Usage:
    # Run with pytest-benchmark
    pytest tests/performance/test_api_performance.py --benchmark-only

    # Run with custom target URL
    BASE_URL=https://your-app.herokuapp.com pytest tests/performance/test_api_performance.py

Requirements:
    - pytest-benchmark
    - requests
"""

import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import requests

# Configuration - can be overridden via environment variables
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
CONCURRENT_USERS = int(os.getenv("CONCURRENT_USERS", "5"))
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "10"))


class TestAPIPerformance:
    """API performance test suite"""

    def test_health_endpoint_response_time(self, benchmark):
        """Test health endpoint response time"""

        def health_check():
            response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
            return response

        result = benchmark(health_check)
        assert result.status_code == 200

    def test_home_page_response_time(self, benchmark):
        """Test home page response time"""

        def get_home_page():
            response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
            return response

        result = benchmark(get_home_page)
        assert result.status_code == 200

    def test_transformation_endpoint_performance(self, benchmark):
        """Test transformation endpoint performance"""

        def transform_text():
            data = {
                "text": "Hello World! This is a performance test.",
                "transformation": "alternate_case",
            }
            response = requests.post(
                f"{BASE_URL}/transform", data=data, timeout=TEST_TIMEOUT
            )
            return response

        result = benchmark(transform_text)
        assert result.status_code == 200

    @pytest.mark.concurrent
    def test_concurrent_requests(self):
        """Test concurrent request handling"""

        def make_request():
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
            end_time = time.time()
            return response.status_code, end_time - start_time

        # Test with multiple concurrent requests
        concurrent_users = min(CONCURRENT_USERS, 20)  # Limit for safety

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(make_request) for _ in range(concurrent_users * 2)
            ]
            results = [future.result() for future in as_completed(futures)]

        # Analyze results
        response_times = [result[1] for result in results]
        status_codes = [result[0] for result in results]

        # All requests should succeed
        assert all(code == 200 for code in status_codes), (
            f"Some requests failed: {status_codes}"
        )

        # Response times should be reasonable
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
        print(f"95th percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")

        # Performance assertions
        assert avg_response_time < 2.0, (
            f"Average response time too high: {avg_response_time:.3f}s"
        )
        assert max_response_time < 5.0, (
            f"Max response time too high: {max_response_time:.3f}s"
        )

    @pytest.mark.load
    def test_sustained_load(self):
        """Test sustained load over time"""
        duration_seconds = int(os.getenv("LOAD_TEST_DURATION", "30"))
        requests_per_second = int(os.getenv("REQUESTS_PER_SECOND", "2"))

        start_time = time.time()
        response_times = []
        errors = 0

        while time.time() - start_time < duration_seconds:
            try:
                request_start = time.time()
                response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
                request_end = time.time()

                if response.status_code == 200:
                    response_times.append(request_end - request_start)
                else:
                    errors += 1

            except requests.RequestException:
                errors += 1

            # Rate limiting
            time.sleep(1.0 / requests_per_second)

        total_requests = len(response_times) + errors
        error_rate = errors / total_requests if total_requests > 0 else 0

        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {len(response_times)}")
        print(f"Error rate: {error_rate:.2%}")

        if response_times:
            avg_response_time = statistics.mean(response_times)
            print(f"Average response time: {avg_response_time:.3f}s")

        # Performance assertions
        assert error_rate < 0.05, f"Error rate too high: {error_rate:.2%}"
        assert len(response_times) > 0, "No successful requests"


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    print("Running basic performance test...")
    print(f"Target URL: {BASE_URL}")

    try:
        # Quick health check
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")

    print(
        "Run 'pytest tests/performance/test_api_performance.py --benchmark-only' for full benchmarks"
    )
