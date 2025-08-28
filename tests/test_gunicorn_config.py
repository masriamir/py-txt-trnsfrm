"""Tests for Gunicorn configuration security and functionality."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


def exec_gunicorn_config(env_vars=None):
    """Execute gunicorn.conf.py with optional environment variables and return namespace."""
    if env_vars is None:
        env_vars = {}

    # Create a clean namespace for execution
    namespace = {}

    # Add necessary imports to namespace
    namespace.update(
        {
            "os": os,
            "Path": Path,
            "multiprocessing": __import__("multiprocessing"),
            "traceback": __import__("traceback"),
        }
    )

    # Set environment variables temporarily
    old_env = {}
    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Read and execute the gunicorn config file
        config_path = Path(__file__).parent.parent / "gunicorn.conf.py"
        with open(config_path) as f:
            config_code = f.read()

        exec(config_code, namespace)  # noqa: S102
        return namespace
    finally:
        # Restore original environment
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


class TestGunicornPidfileConfiguration:
    """Test PID file configuration security and functionality."""

    def test_pidfile_respects_environment_variable(self):
        """Test that GUNICORN_PIDFILE environment variable is respected."""
        custom_pidfile = "/custom/path/test.pid"

        namespace = exec_gunicorn_config({"GUNICORN_PIDFILE": custom_pidfile})

        assert namespace["pidfile"] == custom_pidfile

    def test_pidfile_defaults_to_secure_location(self):
        """Test that PID file defaults to secure system locations."""
        # Mock os.access to simulate /var/run being writable
        with patch("os.access") as mock_access:
            # Mock /var/run as writable
            mock_access.side_effect = lambda path, mode: str(path).startswith(
                "/var/run"
            )

            namespace = exec_gunicorn_config()

            assert namespace["pidfile"] == "/var/run/gunicorn.pid"

    def test_pidfile_fallback_to_current_directory(self):
        """Test PID file falls back to current directory when secure paths unavailable."""
        # Mock all secure directories as non-writable
        with patch("os.access", return_value=False):
            namespace = exec_gunicorn_config()

            assert namespace["pidfile"] == "./gunicorn.pid"

    def test_pidfile_handles_permission_errors(self):
        """Test PID file configuration handles permission errors gracefully."""
        # Mock os.access to raise PermissionError
        with patch("os.access", side_effect=PermissionError("Permission denied")):
            namespace = exec_gunicorn_config()

            # Should fall back to current directory
            assert namespace["pidfile"] == "./gunicorn.pid"

    def test_pidfile_no_tmp_directory_usage(self):
        """Test that PID file configuration doesn't use /tmp directory."""
        namespace = exec_gunicorn_config()

        # Ensure result doesn't contain /tmp
        assert (
            "/tmp" not in namespace["pidfile"]  # noqa: S108
        )  # noqa: S108  # Testing avoidance of /tmp

    def test_gunicorn_config_imports_successfully(self):
        """Test that gunicorn.conf.py imports without errors."""
        try:
            namespace = exec_gunicorn_config()
            # Verify the pidfile variable exists and is a string
            assert "pidfile" in namespace
            assert isinstance(namespace["pidfile"], str)
            assert len(namespace["pidfile"]) > 0
        except Exception as e:
            pytest.fail(f"Failed to execute gunicorn.conf.py: {e}")

    def test_pidfile_with_writable_temp_directory(self):
        """Test PID file configuration with a writable temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_pidfile = str(Path(temp_dir) / "test.pid")

            namespace = exec_gunicorn_config({"GUNICORN_PIDFILE": custom_pidfile})

            assert namespace["pidfile"] == custom_pidfile
            # Verify the directory is actually writable
            assert os.access(Path(custom_pidfile).parent, os.W_OK)

    def test_get_secure_pidfile_path_function_exists(self):
        """Test that get_secure_pidfile_path function is defined and callable."""
        namespace = exec_gunicorn_config()

        assert "get_secure_pidfile_path" in namespace
        assert callable(namespace["get_secure_pidfile_path"])

    def test_pidfile_with_run_directory(self):
        """Test PID file configuration with /run directory."""
        # Mock /run as writable but not /var/run
        with patch("os.access") as mock_access:
            mock_access.side_effect = lambda path, mode: str(path).startswith(
                "/run"
            ) and not str(path).startswith("/var/run")

            namespace = exec_gunicorn_config()

            assert namespace["pidfile"] == "/run/gunicorn.pid"

    @pytest.mark.integration
    def test_pidfile_security_improvement(self):
        """Integration test: verify PID file configuration improves security."""
        # Test that the current configuration doesn't trigger security warnings
        config_path = Path(__file__).parent.parent / "gunicorn.conf.py"

        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "ruff", "check", "--select=S108", str(config_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should not have S108 (insecure temp file usage) warnings
        assert (
            "S108" not in result.stdout
        ), f"Security warning S108 still present: {result.stdout}"
        assert result.returncode == 0, f"Ruff check failed: {result.stdout}"
