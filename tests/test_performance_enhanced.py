"""Enhanced performance tests for critical application workflows.

This module contains comprehensive performance tests that complement the existing
performance test infrastructure, focusing on transformation engine performance,
concurrent load testing, and memory efficiency validation.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from faker import Faker

from app import create_app
from app.config import TestConfig
from app.utils.text_transformers import TextTransformer

fake = Faker()


@pytest.mark.load
class TestTransformationEnginePerformance:
    """Performance tests for text transformation engine."""

    @pytest.fixture
    def transformer(self):
        """Fixture providing TextTransformer instance."""
        return TextTransformer()

    @pytest.mark.load
    @pytest.mark.parametrize(
        "transformation", ["alternate_case", "backwards", "l33t_speak", "rot13"]
    )
    def test_single_transformation_performance(self, transformer, transformation):
        """Test performance of individual transformation operations."""
        text = "Performance test text for individual transformation speed testing."

        start_time = time.perf_counter()

        result = transformer.transform(text, transformation)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Each transformation should complete quickly
        assert duration < 0.01, f"{transformation} took {duration:.4f}s (too slow)"
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.load
    def test_batch_transformation_performance(self, transformer):
        """Test performance of batch transformation operations."""
        texts = [fake.sentence() for _ in range(100)]
        transformation = "alternate_case"

        start_time = time.perf_counter()

        results = []
        for text in texts:
            result = transformer.transform(text, transformation)
            results.append(result)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # 100 transformations should complete within reasonable time
        assert duration < 1.0, f"Batch transformations took {duration:.4f}s (too slow)"
        assert len(results) == 100

        # Average time per transformation
        avg_time = duration / 100
        assert avg_time < 0.01, f"Average transformation time {avg_time:.4f}s too slow"

    @pytest.mark.load
    @pytest.mark.parametrize("size", [1000, 5000, 10000])
    def test_large_text_transformation_performance(self, transformer, size):
        """Test performance with large text inputs."""
        large_text = "A" * size

        start_time = time.perf_counter()

        result = transformer.transform(large_text, "alternate_case")

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Performance should scale reasonably with text size
        expected_max_time = size / 10000  # 1s per 10k characters
        assert (
            duration < expected_max_time
        ), f"Large text ({size} chars) took {duration:.4f}s"
        assert len(result) == size

    @pytest.mark.load
    def test_transformation_memory_efficiency(self, transformer):
        """Test memory efficiency of transformations."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Get baseline memory
        gc.collect()
        memory_before = process.memory_info().rss

        # Perform many transformations
        for i in range(1000):
            text = f"Memory test iteration {i} with some additional content."
            transformer.transform(text, "alternate_case")

        # Force garbage collection and measure memory
        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable (less than 10MB for 1000 operations)
        assert (
            memory_increase < 10 * 1024 * 1024
        ), f"Memory increased by {memory_increase} bytes"

    @pytest.mark.load
    def test_all_transformations_performance(self, transformer):
        """Test performance of transformations categorized by complexity."""
        text = "Performance testing all transformation types for speed comparison."
        transformations = transformer.get_available_transformations()

        # Categorize transformations by algorithmic complexity
        complexity_categories = {
            "simple": [
                "backwards",  # text[::-1] - single operation
                "alternate_case",  # simple character iteration
                "rot13",  # character substitution with math
            ],
            "medium": [
                "l33t_speak",  # dictionary-based replacement
                "morse_code",  # dictionary lookup per character
                "binary",  # character to binary conversion
                "upside_down",  # dictionary mapping + reversal
                "stutter",  # character duplication logic
                "spongebob_case",  # random case alternation
                "wave_text",  # positioning with sine calculations
                "reverse_words",  # word-level operations
                "zalgo",  # light diacritical mark addition
            ],
            "complex": [
                "shizzle",  # ~120 lines: regex, plural detection, vowel analysis
                "rainbow_html",  # HTML generation with color calculations
            ],
        }

        performance_results = {}
        category_results = {category: {} for category in complexity_categories}

        # Test all transformations and categorize results
        for transformation in transformations:
            start_time = time.perf_counter()

            try:
                result = transformer.transform(text, transformation)
                end_time = time.perf_counter()
                duration = end_time - start_time

                performance_results[transformation] = duration

                # Each transformation should complete quickly
                assert duration < 0.1, f"{transformation} took {duration:.4f}s"
                assert isinstance(result, str)

                # Categorize the result
                for category, transforms in complexity_categories.items():
                    if transformation in transforms:
                        category_results[category][transformation] = duration
                        break

            except Exception as e:
                pytest.fail(f"Transformation {transformation} failed: {e}")

        # Test performance within each complexity category
        for category, results in category_results.items():
            if not results:  # Skip empty categories
                continue

            max_time = max(results.values())
            min_time = min(results.values())

            # Within each category, performance should be reasonably similar
            # Simple transformations: 5x ratio (should be very similar)
            # Medium transformations: 10x ratio (some variation expected)
            # Complex transformations: 20x ratio (algorithmic differences)
            max_ratios = {"simple": 5, "medium": 10, "complex": 20}
            max_ratio = max_ratios[category]

            actual_ratio = max_time / min_time if min_time > 0 else 1
            assert actual_ratio < max_ratio, (
                f"{category.title()} transformation performance varies too much: "
                f"{actual_ratio:.1f}x ratio exceeds {max_ratio}x limit. "
                f"Results: {results}"
            )


@pytest.mark.load
class TestAPIEndpointPerformance:
    """Performance tests for API endpoint response times."""

    @pytest.fixture
    def app(self):
        """Fixture providing Flask application."""
        return create_app(TestConfig)

    @pytest.mark.load
    def test_health_endpoint_performance(self, app):
        """Test health endpoint response time."""
        with app.test_client() as client:
            # Warm up
            client.get("/health")

            # Measure performance
            start_time = time.perf_counter()

            response = client.get("/health")

            end_time = time.perf_counter()
            duration = end_time - start_time

            assert response.status_code == 200
            assert duration < 0.1, f"Health endpoint took {duration:.4f}s"

    @pytest.mark.load
    def test_transform_endpoint_performance(self, app):
        """Test transform endpoint response time."""
        with app.test_client() as client:
            request_data = {
                "text": "Performance test",
                "transformation": "alternate_case",
            }

            # Warm up
            client.post("/transform", json=request_data)

            # Measure performance
            start_time = time.perf_counter()

            response = client.post("/transform", json=request_data)

            end_time = time.perf_counter()
            duration = end_time - start_time

            assert response.status_code == 200
            assert duration < 0.1, f"Transform endpoint took {duration:.4f}s"

    @pytest.mark.load
    def test_index_endpoint_performance(self, app):
        """Test index endpoint response time."""
        with app.test_client() as client:
            # Warm up
            client.get("/")

            # Measure performance
            start_time = time.perf_counter()

            response = client.get("/")

            end_time = time.perf_counter()
            duration = end_time - start_time

            assert response.status_code == 200
            assert duration < 0.1, f"Index endpoint took {duration:.4f}s"

    @pytest.mark.load
    def test_sequential_requests_performance(self, app):
        """Test performance of sequential API requests."""
        with app.test_client() as client:
            num_requests = 50

            start_time = time.perf_counter()

            for i in range(num_requests):
                request_data = {"text": f"Request {i}", "transformation": "backwards"}
                response = client.post("/transform", json=request_data)
                assert response.status_code == 200

            end_time = time.perf_counter()
            total_duration = end_time - start_time
            avg_duration = total_duration / num_requests

            # Total time should be reasonable
            assert total_duration < 5.0, f"50 requests took {total_duration:.4f}s"
            assert avg_duration < 0.1, f"Average request time {avg_duration:.4f}s"

    @pytest.mark.load
    def test_mixed_endpoint_performance(self, app):
        """Test performance of mixed endpoint requests."""
        with app.test_client() as client:
            start_time = time.perf_counter()

            # Mix of different endpoints
            for i in range(30):
                if i % 3 == 0:
                    response = client.get("/health")
                elif i % 3 == 1:
                    response = client.get("/")
                else:
                    response = client.post(
                        "/transform",
                        json={"text": f"Test {i}", "transformation": "rot13"},
                    )

                assert response.status_code == 200

            end_time = time.perf_counter()
            duration = end_time - start_time

            # Mixed requests should complete efficiently
            assert duration < 3.0, f"30 mixed requests took {duration:.4f}s"


@pytest.mark.load
@pytest.mark.concurrent
class TestConcurrentLoadPerformance:
    """Performance tests for concurrent load scenarios."""

    @pytest.fixture
    def app(self):
        """Fixture providing Flask application."""
        return create_app(TestConfig)

    @pytest.mark.load
    @pytest.mark.concurrent
    def test_concurrent_transformation_requests(self, app):
        """Test concurrent transformation requests performance."""
        num_threads = 5
        requests_per_thread = 10

        def make_requests(thread_id):
            results = []
            with app.test_client() as client:
                for i in range(requests_per_thread):
                    request_data = {
                        "text": f"Thread {thread_id} Request {i}",
                        "transformation": "alternate_case",
                    }

                    start_time = time.perf_counter()
                    response = client.post("/transform", json=request_data)
                    end_time = time.perf_counter()

                    duration = end_time - start_time
                    results.append((response.status_code, duration))

            return results

        # Execute concurrent requests
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_requests, i) for i in range(num_threads)]
            all_results = []

            for future in as_completed(futures):
                thread_results = future.result()
                all_results.extend(thread_results)

        end_time = time.perf_counter()
        total_duration = end_time - start_time

        # Verify all requests succeeded
        for status_code, duration in all_results:
            assert status_code == 200
            assert duration < 1.0  # Individual request should be fast

        # Total concurrent execution should be efficient
        total_requests = num_threads * requests_per_thread
        expected_sequential_time = total_requests * 0.05  # 50ms per request

        # Concurrent execution should be faster than sequential
        assert (
            total_duration < expected_sequential_time
        ), f"Concurrent execution ({total_duration:.4f}s) not faster than expected sequential ({expected_sequential_time:.4f}s)"

    @pytest.mark.load
    @pytest.mark.concurrent
    def test_concurrent_mixed_requests(self, app):
        """Test concurrent mixed request types performance."""
        num_threads = 3

        def health_requests():
            results = []
            with app.test_client() as client:
                for _ in range(20):
                    start_time = time.perf_counter()
                    response = client.get("/health")
                    end_time = time.perf_counter()

                    results.append((response.status_code, end_time - start_time))
            return results

        def transform_requests():
            results = []
            with app.test_client() as client:
                for i in range(15):
                    request_data = {
                        "text": f"Concurrent test {i}",
                        "transformation": "backwards",
                    }

                    start_time = time.perf_counter()
                    response = client.post("/transform", json=request_data)
                    end_time = time.perf_counter()

                    results.append((response.status_code, end_time - start_time))
            return results

        def index_requests():
            results = []
            with app.test_client() as client:
                for _ in range(10):
                    start_time = time.perf_counter()
                    response = client.get("/")
                    end_time = time.perf_counter()

                    results.append((response.status_code, end_time - start_time))
            return results

        # Execute different types of requests concurrently
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            health_future = executor.submit(health_requests)
            transform_future = executor.submit(transform_requests)
            index_future = executor.submit(index_requests)

            health_results = health_future.result()
            transform_results = transform_future.result()
            index_results = index_future.result()

        end_time = time.perf_counter()
        total_duration = end_time - start_time

        # Verify all requests succeeded
        all_results = health_results + transform_results + index_results
        for status_code, duration in all_results:
            assert status_code == 200
            assert duration < 1.0

        # Mixed concurrent requests should complete efficiently
        total_requests = len(all_results)
        assert (
            total_duration < 5.0
        ), f"Mixed concurrent requests took {total_duration:.4f}s"

        avg_duration = total_duration / total_requests
        assert (
            avg_duration < 0.2
        ), f"Average concurrent request time {avg_duration:.4f}s"

    @pytest.mark.load
    @pytest.mark.concurrent
    def test_transformation_engine_thread_safety(self):
        """Test that transformation engine is thread-safe under load."""
        transformer = TextTransformer()
        num_threads = 10
        operations_per_thread = 50

        results = []
        errors = []

        def worker_thread(thread_id):
            thread_results = []
            try:
                for i in range(operations_per_thread):
                    text = f"Thread {thread_id} operation {i}"
                    result = transformer.transform(text, "alternate_case")
                    thread_results.append((text, result))
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

            return thread_results

        # Execute concurrent transformations
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]

            for future in as_completed(futures):
                thread_results = future.result()
                results.extend(thread_results)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Verify no errors occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify all operations completed
        expected_operations = num_threads * operations_per_thread
        assert len(results) == expected_operations

        # Verify results are correct
        for _text, result in results:
            assert isinstance(result, str)
            assert len(result) > 0

        # Performance should be reasonable
        operations_per_second = expected_operations / duration
        assert operations_per_second > 100, f"Only {operations_per_second:.1f} ops/sec"


@pytest.mark.load
class TestMemoryAndResourcePerformance:
    """Performance tests for memory usage and resource efficiency."""

    @pytest.mark.load
    def test_application_memory_usage(self):
        """Test application memory usage under normal load."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Get baseline memory
        gc.collect()
        memory_before = process.memory_info().rss

        # Create and use application
        app = create_app(TestConfig)

        with app.test_client() as client:
            # Perform various operations
            for i in range(100):
                client.get("/health")
                client.post(
                    "/transform",
                    json={"text": f"Memory test {i}", "transformation": "backwards"},
                )

        # Measure memory after operations
        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable
        assert (
            memory_increase < 50 * 1024 * 1024
        ), f"Memory increased by {memory_increase} bytes"

    @pytest.mark.load
    def test_transformation_cache_efficiency(self):
        """Test efficiency of transformation operations with repeated inputs."""
        transformer = TextTransformer()

        # Test with repeated transformations of the same text
        text = "Cache efficiency test text for performance evaluation."
        transformation = "alternate_case"

        # First run - baseline
        start_time = time.perf_counter()
        for _ in range(100):
            transformer.transform(text, transformation)
        baseline_duration = time.perf_counter() - start_time

        # Second run - should not be significantly slower (no memory leaks)
        start_time = time.perf_counter()
        for _ in range(100):
            transformer.transform(text, transformation)
        second_duration = time.perf_counter() - start_time

        # Performance should be consistent
        assert (
            second_duration < baseline_duration * 1.5
        ), f"Second run ({second_duration:.4f}s) much slower than first ({baseline_duration:.4f}s)"

    @pytest.mark.load
    def test_garbage_collection_efficiency(self):
        """Test that objects are properly garbage collected."""
        import gc
        import weakref

        # Track object lifecycle
        transformers = []
        weak_refs = []

        # Create many transformer instances
        for _i in range(100):
            transformer = TextTransformer()
            transformers.append(transformer)
            weak_refs.append(weakref.ref(transformer))

        # Use transformers
        for transformer in transformers:
            transformer.transform("GC test", "backwards")

        # Clear references
        transformers.clear()

        # Force garbage collection
        gc.collect()

        # Check that objects were garbage collected
        alive_objects = sum(1 for ref in weak_refs if ref() is not None)

        # Most objects should be garbage collected
        assert alive_objects < 10, f"{alive_objects} objects still alive after GC"
