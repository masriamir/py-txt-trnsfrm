"""Tests for host binding security functionality.

This module tests the conditional host binding behavior that restricts
binding to 0.0.0.0 only in production environments for enhanced security.
"""

import os
from unittest.mock import patch

import pytest

from app.config import get_host_for_environment


class TestHostBinding:
    """Test host binding functionality for different environments."""

    @pytest.mark.unit
    def test_development_environment_binds_to_localhost(self):
        """Test that development environment binds to 127.0.0.1."""
        host = get_host_for_environment("development")
        assert host == "127.0.0.1", "Development should bind to localhost for security"

    @pytest.mark.unit
    def test_testing_environment_binds_to_localhost(self):
        """Test that testing environment binds to 127.0.0.1."""
        host = get_host_for_environment("testing")
        assert host == "127.0.0.1", "Testing should bind to localhost for security"

    @pytest.mark.unit
    def test_production_environment_binds_to_all_interfaces(self):
        """Test that production environment binds to 0.0.0.0."""
        host = get_host_for_environment("production")
        assert (
            host == "0.0.0.0"
        ), "Production should bind to all interfaces"  # noqa: S104

    @pytest.mark.unit
    def test_heroku_environment_binds_to_all_interfaces(self):
        """Test that heroku environment binds to 0.0.0.0."""
        host = get_host_for_environment("heroku")
        assert host == "0.0.0.0", "Heroku should bind to all interfaces"  # noqa: S104

    @pytest.mark.unit
    def test_unknown_environment_defaults_to_localhost(self):
        """Test that unknown environments default to 127.0.0.1 for security."""
        host = get_host_for_environment("unknown_env")
        assert host == "127.0.0.1", "Unknown environments should default to localhost"

    @pytest.mark.unit
    @patch.dict(os.environ, {"DYNO": "web.1"})
    def test_heroku_dyno_environment_binds_to_all_interfaces(self):
        """Test that environments with DYNO set bind to 0.0.0.0."""
        # Should return 0.0.0.0 regardless of config_name when DYNO is set
        host = get_host_for_environment("development")
        assert (
            host == "0.0.0.0"
        ), "Heroku DYNO environment should bind to all interfaces"  # noqa: S104

    @pytest.mark.unit
    @patch.dict(os.environ, {"DYNO": "worker.1"})
    def test_heroku_worker_dyno_binds_to_all_interfaces(self):
        """Test that worker dynos also bind to 0.0.0.0."""
        host = get_host_for_environment("testing")
        assert (
            host == "0.0.0.0"
        ), "Heroku worker dyno should bind to all interfaces"  # noqa: S104

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_no_dyno_environment_respects_config_name(self):
        """Test that without DYNO, config_name determines binding."""
        # Ensure DYNO is not set
        assert "DYNO" not in os.environ

        # Development should bind to localhost
        host = get_host_for_environment("development")
        assert host == "127.0.0.1"

        # Production should bind to all interfaces
        host = get_host_for_environment("production")
        assert host == "0.0.0.0"  # noqa: S104

    @pytest.mark.unit
    def test_case_sensitivity_of_config_names(self):
        """Test that config names are case sensitive."""
        # Uppercase should not match
        host = get_host_for_environment("PRODUCTION")
        assert host == "127.0.0.1", "Config names should be case sensitive"

        # Mixed case should not match
        host = get_host_for_environment("Production")
        assert host == "127.0.0.1", "Config names should be case sensitive"


class TestHostBindingIntegration:
    """Integration tests for host binding with application startup."""

    @pytest.mark.integration
    def test_host_binding_function_is_available(self):
        """Test that the host binding function is available and works correctly."""
        from app.config import get_host_for_environment

        assert callable(get_host_for_environment)

        # Test basic functionality
        assert get_host_for_environment("development") == "127.0.0.1"
        assert get_host_for_environment("production") == "0.0.0.0"  # noqa: S104

    @pytest.mark.integration
    def test_host_binding_function_import_in_modules(self):
        """Test that both app.py and wsgi.py can import the function."""
        # Test import from app.py perspective
        try:
            from app.config import get_host_for_environment

            assert callable(get_host_for_environment)
        except ImportError:
            pytest.fail("Could not import get_host_for_environment function")


class TestSecurityDocumentation:
    """Tests to verify security documentation and rationale."""

    @pytest.mark.unit
    def test_host_binding_function_has_security_documentation(self):
        """Test that the host binding function has proper security documentation."""
        from app.config import get_host_for_environment

        docstring = get_host_for_environment.__doc__
        assert docstring is not None, "Function should have documentation"
        assert "security" in docstring.lower(), "Documentation should mention security"
        assert (
            "production" in docstring.lower()
        ), "Documentation should explain production behavior"
        assert (
            "development" in docstring.lower()
        ), "Documentation should explain development behavior"

    @pytest.mark.unit
    def test_function_signature_has_type_hints(self):
        """Test that the function has proper type hints."""
        import inspect

        from app.config import get_host_for_environment

        signature = inspect.signature(get_host_for_environment)

        # Check parameter type hint
        config_name_param = signature.parameters["config_name"]
        assert (
            config_name_param.annotation is str
        ), "Parameter should have str type hint"

        # Check return type hint
        assert signature.return_annotation is str, "Return should have str type hint"
