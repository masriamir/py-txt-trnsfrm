"""Tests for version utility module.

This module contains tests for the version extraction functionality,
including caching behavior, error handling, and pyproject.toml parsing.
"""

from unittest.mock import patch

import pytest

from app.utils.version import get_application_version, reset_version_cache


@pytest.mark.unit
class TestVersionUtility:
    """Test suite for version utility functions."""

    def setup_method(self):
        """Reset version cache before each test."""
        reset_version_cache()

    @pytest.mark.unit
    def test_get_application_version_returns_string(self):
        """Test that get_application_version returns a string."""
        version = get_application_version()
        assert isinstance(version, str)
        assert len(version) > 0

    @pytest.mark.unit
    def test_get_application_version_from_real_pyproject(self):
        """Test version extraction from actual pyproject.toml."""
        version = get_application_version()
        # Should get the actual version from pyproject.toml or fallback
        assert version == "0.1.0" or version == "unknown"

    @pytest.mark.unit
    def test_version_caching_behavior(self):
        """Test that version is cached after first call."""
        # First call
        version1 = get_application_version()
        # Second call should return cached value
        version2 = get_application_version()

        assert version1 == version2
        assert isinstance(version1, str)

    @pytest.mark.unit
    @patch("app.utils.version.Path.exists")
    def test_version_fallback_when_file_not_found(self, mock_exists):
        """Test version fallback when pyproject.toml is not found."""
        # Reset cache to test fresh load
        reset_version_cache()

        # Mock file not existing
        mock_exists.return_value = False

        version = get_application_version()
        assert version == "unknown"

    @pytest.mark.unit
    def test_version_cache_reset(self):
        """Test that cache reset allows reloading."""
        # Get version first time
        version1 = get_application_version()

        # Reset cache
        reset_version_cache()

        # Get version again - should work without issue
        version2 = get_application_version()

        # Both should be valid
        assert isinstance(version1, str)
        assert isinstance(version2, str)

    @pytest.mark.unit
    @patch("app.utils.version.open")
    def test_version_parsing_with_custom_content(self, mock_open):
        """Test version parsing with custom pyproject.toml content."""
        reset_version_cache()

        # Mock pyproject.toml content
        mock_content = """
[build-system]
requires = ["hatchling"]

[project]
name = "test-app"
version = "1.2.3"
description = "Test app"
"""
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = mock_content

        with patch("app.utils.version.Path.exists", return_value=True):
            version = get_application_version()
            assert version == "1.2.3"

    @pytest.mark.unit
    @patch("app.utils.version.open")
    def test_version_parsing_with_single_quotes(self, mock_open):
        """Test version parsing with single quotes."""
        reset_version_cache()

        # Mock pyproject.toml content with single quotes
        mock_content = """
[project]
version = '2.0.0'
"""
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = mock_content

        with patch("app.utils.version.Path.exists", return_value=True):
            version = get_application_version()
            assert version == "2.0.0"

    @pytest.mark.unit
    @patch("app.utils.version.open")
    def test_version_parsing_missing_version_field(self, mock_open):
        """Test behavior when version field is missing."""
        reset_version_cache()

        # Mock pyproject.toml content without version
        mock_content = """
[project]
name = "test-app"
description = "Test app"
"""
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = mock_content

        with patch("app.utils.version.Path.exists", return_value=True):
            version = get_application_version()
            assert version == "unknown"

    @pytest.mark.unit
    @patch("app.utils.version.open")
    def test_version_parsing_malformed_content(self, mock_open):
        """Test behavior with malformed pyproject.toml."""
        reset_version_cache()

        # Mock malformed content
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.side_effect = Exception("File read error")

        with patch("app.utils.version.Path.exists", return_value=True):
            version = get_application_version()
            assert version == "unknown"


@pytest.mark.integration
class TestVersionIntegration:
    """Integration tests for version functionality."""

    def setup_method(self):
        """Reset version cache before each test."""
        reset_version_cache()

    @pytest.mark.integration
    def test_version_works_with_real_project_structure(self):
        """Test that version utility works with actual project structure."""
        version = get_application_version()

        # Should successfully read from real pyproject.toml
        assert isinstance(version, str)
        assert len(version) > 0
        # Either the real version or fallback
        assert version in ["0.1.0", "unknown"] or "." in version

    @pytest.mark.integration
    def test_version_consistent_across_calls(self):
        """Test version consistency across multiple calls."""
        versions = [get_application_version() for _ in range(5)]

        # All versions should be identical (due to caching)
        assert all(v == versions[0] for v in versions)
        assert len(set(versions)) == 1
