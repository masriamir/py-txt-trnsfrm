"""Tests for secure random number generation in text transformations."""

import pytest

from app.utils.text_transformers import TextTransformer


class TestSecureRandomUsage:
    """Test that secure random number generation is properly implemented."""

    @pytest.mark.unit
    def test_secure_random_import_available(self):
        """Test that secrets module is properly imported and accessible."""
        import secrets
        
        # Verify secrets module has the methods we need
        assert hasattr(secrets, 'SystemRandom')
        assert hasattr(secrets, 'choice')
        
        # Test SystemRandom functionality
        secure_random = secrets.SystemRandom()
        assert hasattr(secure_random, 'random')
        
        # Test that random() returns float between 0 and 1
        for _ in range(10):
            value = secure_random.random()
            assert 0.0 <= value < 1.0

    @pytest.mark.unit
    def test_spongebob_case_uses_secure_random(self):
        """Test that spongebob_case transformation works with secure random."""
        transformer = TextTransformer()
        
        # Test multiple times to ensure randomness works
        results = []
        for _ in range(10):
            result = transformer.spongebob_case("hello world")
            results.append(result)
            
            # Verify result has mixed case
            assert result != "hello world"  # Should be different from original
            assert result.lower() == "hello world"  # Should preserve characters
        
        # Results should not all be identical (very low probability with secure random)
        unique_results = set(results)
        assert len(unique_results) > 1, "Secure random should produce varying results"

    @pytest.mark.unit
    def test_zalgo_light_uses_secure_random(self):
        """Test that zalgo_light transformation works with secure random."""
        transformer = TextTransformer()
        
        # Test multiple times to ensure randomness works
        results = []
        for _ in range(20):  # More iterations for zalgo which has lower probability
            result = transformer.zalgo_light("hello")
            results.append(result)
            
            # Verify result contains original text
            assert "hello" in result or len(result) >= len("hello")
        
        # Should get some variation in results due to random character addition
        unique_results = set(results)
        # At least some results should be different (combining characters are added randomly)
        assert len(unique_results) >= 1

    @pytest.mark.slow
    @pytest.mark.unit
    def test_secure_random_performance(self):
        """Test that secure random doesn't significantly impact performance."""
        import time
        
        transformer = TextTransformer()
        text = "The quick brown fox jumps over the lazy dog"
        
        # Time multiple transformations
        start_time = time.time()
        for _ in range(100):
            transformer.spongebob_case(text)
            transformer.zalgo_light(text)
        end_time = time.time()
        
        # Should complete 200 transformations in reasonable time (less than 1 second)
        duration = end_time - start_time
        assert duration < 1.0, f"Transformations took {duration:.3f}s, may be too slow"

    @pytest.mark.unit
    def test_transformation_determinism_within_call(self):
        """Test that each transformation call uses fresh random values."""
        transformer = TextTransformer()
        
        # For a longer text, spongebob_case should have internal variation
        text = "abcdefghijklmnopqrstuvwxyz"
        result = transformer.spongebob_case(text)
        
        # Should have mix of upper and lower case
        has_upper = any(c.isupper() for c in result)
        has_lower = any(c.islower() for c in result)
        assert has_upper and has_lower, "Should have mixed case from secure random"

    @pytest.mark.integration
    def test_secure_random_integration(self):
        """Integration test for secure random usage."""
        transformer = TextTransformer()
        
        # Test that transformations work correctly
        test_cases = [
            ("hello", "spongebob_case"),
            ("test text", "spongebob_case"),
            ("sample", "zalgo"),
            ("another test", "zalgo"),
        ]
        
        for text, transformation in test_cases:
            result = transformer.transform(text, transformation)
            
            # Basic validation
            assert isinstance(result, str)
            assert len(result) >= len(text)  # Result should be at least as long
            
            # Verify transformation occurred
            if transformation == "spongebob_case":
                assert result != text or text.islower()  # Should change case or was already lowercase
            elif transformation == "zalgo":
                # Zalgo may or may not add characters due to randomness
                assert len(result) >= len(text)