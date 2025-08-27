"""Tests for Docker Compose configuration functionality.

This module tests the Docker Compose configuration to ensure dynamic port
configuration works correctly with environment variable substitution.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml


class TestDockerComposePortConfiguration:
    """Test Docker Compose port configuration with environment variables."""

    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml file exists."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml should exist"

    def test_docker_compose_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Parse YAML to ensure it's valid
        config = yaml.safe_load(content)
        assert config is not None, "docker-compose.yml should be valid YAML"
        assert "services" in config, "docker-compose.yml should have services section"

    def test_web_service_port_mapping_uses_environment_variable(self):
        """Test that web service uses environment variable for port mapping."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Check for environment variable substitution in ports
        assert (
            "${PORT:-5000}:${PORT:-5000}" in content
        ), "Port mapping should use environment variable substitution"

    def test_web_service_healthcheck_uses_environment_variable(self):
        """Test that web service healthcheck uses environment variable for port."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Check for environment variable substitution in healthcheck
        assert (
            "http://localhost:${PORT:-5000}/health" in content
        ), "Healthcheck URL should use environment variable substitution"

    def test_web_service_environment_port_uses_substitution(self):
        """Test that web service environment PORT uses substitution syntax."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Check for environment variable substitution in environment
        assert (
            "PORT=${PORT:-5000}" in content
        ), "Environment PORT should use substitution syntax"

    def test_docker_compose_config_validation(self):
        """Test that docker-compose config validation passes."""
        repo_root = Path(__file__).parent.parent

        # Test with default PORT (not set)
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            env={**os.environ, "PORT": ""},  # Ensure PORT is not set
        )

        # docker-compose config should succeed (exit code 0)
        # If docker-compose is not available, skip this test
        if result.returncode == 127:  # Command not found
            pytest.skip("docker-compose not available in test environment")

        assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"

        # Parse the output to verify default port is used
        config_output = result.stdout
        assert (
            "5000:5000" in config_output
        ), "Default port 5000 should be used when PORT not set"

    def test_docker_compose_config_with_custom_port(self):
        """Test that docker-compose config works with custom PORT."""
        repo_root = Path(__file__).parent.parent

        # Test with custom PORT
        custom_port = "8080"
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            env={**os.environ, "PORT": custom_port},
        )

        # If docker-compose is not available, skip this test
        if result.returncode == 127:  # Command not found
            pytest.skip("docker-compose not available in test environment")

        assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"

        # Parse the output to verify custom port is used
        config_output = result.stdout
        assert (
            f"{custom_port}:{custom_port}" in config_output
        ), f"Custom port {custom_port} should be used when PORT is set"
        assert (
            f"http://localhost:{custom_port}/health" in config_output
        ), f"Healthcheck should use custom port {custom_port}"

    def test_docker_compose_environment_variable_format(self):
        """Test that environment variable substitution uses correct format."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Check for proper substitution syntax with default value
        # Pattern: ${VARIABLE:-default}
        port_pattern = r"\$\{PORT:-5000\}"
        matches = re.findall(port_pattern, content)

        # Should find at least 3 occurrences: ports mapping (2) + healthcheck (1) + environment (1)
        assert (
            len(matches) >= 3
        ), f"Should find at least 3 occurrences of ${{PORT:-5000}}, found {len(matches)}"

    def test_docker_compose_backward_compatibility(self):
        """Test that configuration maintains backward compatibility."""
        repo_root = Path(__file__).parent.parent
        compose_file = repo_root / "docker-compose.yml"

        with open(compose_file) as f:
            content = f.read()

        # Ensure default port is 5000 for backward compatibility
        assert (
            "5000" in content
        ), "Default port should be 5000 for backward compatibility"

        # Ensure no hardcoded ports remain
        assert '"5000:5000"' not in content, "Should not contain hardcoded port mapping"
        assert (
            '"http://localhost:5000/health"' not in content
        ), "Should not contain hardcoded healthcheck URL"

    @pytest.mark.integration
    def test_docker_compose_integration_with_different_ports(self):
        """Integration test for docker-compose with different port values."""
        repo_root = Path(__file__).parent.parent

        test_ports = ["3000", "8000", "9999"]

        for port in test_ports:
            # Test docker-compose config with different ports
            result = subprocess.run(
                ["docker-compose", "config"],
                capture_output=True,
                text=True,
                cwd=repo_root,
                env={**os.environ, "PORT": port},
            )

            # If docker-compose is not available, skip this test
            if result.returncode == 127:  # Command not found
                pytest.skip("docker-compose not available in test environment")

            assert (
                result.returncode == 0
            ), f"docker-compose config failed for port {port}: {result.stderr}"

            config_output = result.stdout

            # Verify port mapping
            assert (
                f"{port}:{port}" in config_output
            ), f"Port mapping should use port {port}"

            # Verify healthcheck URL
            assert (
                f"http://localhost:{port}/health" in config_output
            ), f"Healthcheck should use port {port}"

            # Verify environment variable
            assert (
                f"PORT={port}" in config_output
            ), f"Environment should set PORT={port}"


if __name__ == "__main__":
    # Run basic tests when executed directly
    test_class = TestDockerComposePortConfiguration()

    test_class.test_docker_compose_file_exists()
    test_class.test_docker_compose_valid_yaml()
    test_class.test_web_service_port_mapping_uses_environment_variable()
    test_class.test_web_service_healthcheck_uses_environment_variable()
    test_class.test_web_service_environment_port_uses_substitution()
    test_class.test_docker_compose_environment_variable_format()
    test_class.test_docker_compose_backward_compatibility()

    print("✅ All Docker Compose configuration tests passed!")
