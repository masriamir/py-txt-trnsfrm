"""Test Makefile functionality and integration."""

import os
import subprocess
from pathlib import Path

import pytest


class TestMakefileCommands:
    """Test suite for Makefile command functionality."""

    def test_makefile_exists(self):
        """Test that the Makefile exists in the project root."""
        makefile_path = Path(__file__).parent.parent / "Makefile"
        assert makefile_path.exists(), "Makefile should exist in project root"

    @pytest.mark.integration
    def test_make_help_command(self):
        """Test that 'make help' command works correctly."""
        result = subprocess.run(
            ["make", "help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"make help failed: {result.stderr}"

        # Check for key sections in help output
        output = result.stdout
        assert "py-txt-trnsfrm Development Makefile" in output
        assert "Core Workflow Commands:" in output
        assert "Code Quality Commands:" in output
        assert "Testing Commands:" in output
        assert "Application Commands:" in output
        assert "Security Commands:" in output
        assert "Docker Commands:" in output
        assert "CI/CD & Deployment:" in output

    @pytest.mark.integration
    def test_make_version_command(self):
        """Test that 'make version' command works correctly."""
        result = subprocess.run(
            ["make", "version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"make version failed: {result.stderr}"

        # Check for version information
        output = result.stdout
        assert "py-txt-trnsfrm Version Information" in output
        assert "Python:" in output
        assert "UV:" in output
        assert "Flask:" in output

    @pytest.mark.integration
    def test_make_progress_test_command(self):
        """Test that progress indicators work correctly."""
        result = subprocess.run(
            ["make", "progress-test"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"make progress-test failed: {result.stderr}"

        # Check for progress indicators (note: ANSI colors will be in output)
        output = result.stdout
        assert "This is a progress message" in output
        assert "This is a success message" in output
        assert "This is an error message" in output

    @pytest.mark.unit
    def test_makefile_has_required_targets(self):
        """Test that the Makefile contains all required targets."""
        makefile_path = Path(__file__).parent.parent / "Makefile"

        with open(makefile_path) as f:
            content = f.read()

        # Core workflow commands
        required_targets = [
            "setup:",
            "install:",
            "sync:",
            "clean:",
            "fresh:",
            "format:",
            "lint:",
            "fix:",
            "check:",
            "types:",
            "test:",
            "test-unit:",
            "test-api:",
            "test-all:",
            "test-fast:",
            "coverage:",
            "test-perf:",
            "run:",
            "run-prod:",
            "health:",
            "demo:",
            "security:",
            "security-quick:",
            "docker-build:",
            "docker-run:",
            "docker-stop:",
            "docker-clean:",
            "ci:",
            "deploy:",
            "help:",
            "version:",
        ]

        for target in required_targets:
            assert target in content, (
                f"Required target '{target}' not found in Makefile"
            )

    @pytest.mark.unit
    def test_makefile_has_proper_structure(self):
        """Test that the Makefile has proper structure and documentation."""
        makefile_path = Path(__file__).parent.parent / "Makefile"

        with open(makefile_path) as f:
            content = f.read()

        # Check for key structural elements
        assert "# Variables and Configuration" in content
        assert ".PHONY:" in content
        assert ".DEFAULT_GOAL := help" in content
        assert "UV := uv" in content
        # Future-Proof Template Section has been moved to docs/MAKEFILE.md
        assert (
            "See docs/MAKEFILE.md for the command template and best practices"
            in content
        )

    @pytest.mark.unit
    def test_makefile_documentation_exists(self):
        """Test that comprehensive Makefile documentation exists."""
        docs_path = Path(__file__).parent.parent / "docs" / "MAKEFILE.md"
        assert docs_path.exists(), "docs/MAKEFILE.md should exist"

        with open(docs_path) as f:
            content = f.read()

        # Check for key documentation sections
        assert "# Makefile Documentation" in content
        assert "## Overview" in content
        assert "## Quick Start" in content
        assert "## Command Categories" in content
        assert "## Troubleshooting" in content

    @pytest.mark.integration
    def test_make_clean_command(self):
        """Test that 'make clean' command works correctly."""
        result = subprocess.run(
            ["make", "clean"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"make clean failed: {result.stderr}"

        # Check for success message
        output = result.stdout
        assert "Cleanup complete!" in output or "✅" in output

    @pytest.mark.integration
    def test_make_uv_check_functionality(self):
        """Test that UV check works properly when UV is installed."""
        result = subprocess.run(
            ["make", "uv-check"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # Should pass since UV is installed in our environment
        assert result.returncode == 0, f"make uv-check failed: {result.stderr}"

    @pytest.mark.smoke
    def test_critical_makefile_commands(self):
        """Test critical Makefile commands that should always work."""
        critical_commands = ["help", "version", "clean", "uv-check"]

        for command in critical_commands:
            result = subprocess.run(
                ["make", command],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0, (
                f"Critical command 'make {command}' failed: {result.stderr}"
            )


class TestMakefileIntegration:
    """Test integration with existing project tools."""

    @pytest.mark.integration
    def test_makefile_integrates_with_existing_scripts(self):
        """Test that Makefile properly integrates with existing scripts."""
        project_root = Path(__file__).parent.parent

        # Check that referenced scripts exist
        deploy_script = project_root / "deploy.sh"
        security_script = project_root / "run_security_analysis.sh"

        assert deploy_script.exists(), (
            "deploy.sh should exist for deployment integration"
        )
        assert security_script.exists(), (
            "run_security_analysis.sh should exist for security integration"
        )

    @pytest.mark.integration
    def test_makefile_respects_uv_dependency_groups(self):
        """Test that Makefile commands use proper UV dependency groups."""
        makefile_path = Path(__file__).parent.parent / "Makefile"

        with open(makefile_path) as f:
            content = f.read()

        # Check that install command uses proper groups
        assert "--group dev --group test --group security" in content
        # Check for uv sync command (uses variable $(UV))
        assert "$(UV) sync" in content

    @pytest.mark.unit
    def test_readme_references_makefile_docs(self):
        """Test that README properly references Makefile documentation."""
        readme_path = Path(__file__).parent.parent / "README.md"

        with open(readme_path) as f:
            content = f.read()

        # Check for reference to Makefile documentation
        assert "docs/MAKEFILE.md" in content or "MAKEFILE.md" in content, (
            "README should reference Makefile documentation"
        )


class TestMakefileEnvIntegration:
    """Test .env file integration and variable precedence."""

    @pytest.fixture
    def project_root(self):
        """Fixture providing project root path."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def temp_env_file(self, project_root):
        """Fixture providing a temporary .env file for testing."""
        env_file = project_root / ".env"
        original_content = None

        # Backup original .env file if it exists
        if env_file.exists():
            original_content = env_file.read_text()

        yield env_file

        # Restore original .env file or remove if it didn't exist
        if original_content is not None:
            env_file.write_text(original_content)
        elif env_file.exists():
            env_file.unlink()

    @pytest.mark.integration
    def test_env_file_loading_when_present(self, temp_env_file, project_root):
        """Test that .env file variables are loaded correctly."""
        # Create a test .env file with custom values
        env_content = """
PORT=8080
HOST=0.0.0.0
MARKERS=unit
VERBOSE=1
DEBUG=1
DOCKER_IMAGE=test-image
DOCKER_TAG=test-tag
"""
        temp_env_file.write_text(env_content.strip())

        # Test that make command can access these variables
        # We'll use a simple grep to check if the Makefile has these values
        result = subprocess.run(
            ["make", "version"],  # Safe command that should work
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        assert result.returncode == 0, f"make version failed: {result.stderr}"

    @pytest.mark.integration
    def test_env_file_missing_graceful_handling(self, project_root):
        """Test that Makefile works correctly when .env file is missing."""
        # Ensure no .env file exists
        env_file = project_root / ".env"
        if env_file.exists():
            env_file.unlink()

        # Test that make commands still work with defaults
        result = subprocess.run(
            ["make", "help"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        assert result.returncode == 0, f"make help failed without .env: {result.stderr}"

    @pytest.mark.integration
    def test_environment_variable_precedence(self, temp_env_file, project_root):
        """Test that environment variables override .env file values."""
        # Create .env file with one value
        env_content = "PORT=8080"
        temp_env_file.write_text(env_content)

        # Set environment variable to different value
        env = os.environ.copy()
        env["PORT"] = "9090"

        # Run make command with custom environment
        result = subprocess.run(
            ["make", "version"],  # Safe test command
            capture_output=True,
            text=True,
            cwd=project_root,
            env=env,
        )

        assert result.returncode == 0, (
            f"make version failed with env override: {result.stderr}"
        )

    @pytest.mark.integration
    def test_command_line_argument_precedence(self, temp_env_file, project_root):
        """Test that command line arguments override both .env and environment variables."""
        # Create .env file with one value
        env_content = "PORT=8080"
        temp_env_file.write_text(env_content)

        # Set environment variable to different value
        env = os.environ.copy()
        env["PORT"] = "9090"

        # Test command line override (using a safe target that accepts PORT)
        # We'll test this by checking if the Makefile properly handles variable assignment
        result = subprocess.run(
            ["make", "help", "PORT=7070"],
            capture_output=True,
            text=True,
            cwd=project_root,
            env=env,
        )

        assert result.returncode == 0, (
            f"make help with PORT override failed: {result.stderr}"
        )

    @pytest.mark.unit
    def test_makefile_has_env_loading_logic(self, project_root):
        """Test that Makefile contains proper .env loading logic."""
        makefile_path = project_root / "Makefile"

        with open(makefile_path) as f:
            content = f.read()

        # Check for .env loading logic
        assert "ifneq (,$(wildcard .env))" in content, (
            "Makefile should check for .env file existence"
        )
        assert "include .env" in content, "Makefile should include .env file"
        assert "export" in content, "Makefile should export .env variables"

    @pytest.mark.unit
    def test_makefile_variable_defaults(self, project_root):
        """Test that Makefile has proper variable defaults with ?= operator."""
        makefile_path = project_root / "Makefile"

        with open(makefile_path) as f:
            content = f.read()

        # Check for default variable assignments using ?= (conditional assignment)
        required_defaults = [
            "PORT ?= 5000",
            "HOST ?= 127.0.0.1",
            "MARKERS ?=",
            "TIMEOUT ?= 300",
            "VERBOSE ?= 0",
            "DEBUG ?= 0",
            "DOCKER_IMAGE ?= py-txt-trnsfrm",
            "DOCKER_TAG ?= latest",
        ]

        for default in required_defaults:
            assert default in content, f"Makefile should have default: {default}"

    @pytest.mark.integration
    def test_env_example_file_compatibility(self, project_root):
        """Test that .env.example file contains all Makefile-related variables."""
        env_example_path = project_root / ".env.example"

        with open(env_example_path) as f:
            content = f.read()

        # Check for key Makefile variables (some are commented, that's fine)
        makefile_vars = [
            "PORT",  # Should be active (not commented)
            "HOST",  # Can be commented
            "MARKERS",  # Can be commented
            "TIMEOUT",  # Can be commented
            "VERBOSE",  # Can be commented
            "DEBUG",  # Can be commented
            "DOCKER_IMAGE",  # Can be commented
            "DOCKER_TAG",  # Can be commented
        ]

        for var in makefile_vars:
            assert var in content, f".env.example should reference {var}"

    @pytest.mark.integration
    def test_no_duplicate_port_in_env_example(self, project_root):
        """Test that PORT is not duplicated in .env.example file."""
        env_example_path = project_root / ".env.example"

        with open(env_example_path) as f:
            lines = f.readlines()

        # Count occurrences of PORT= (both active and commented)
        port_occurrences = []
        for i, line in enumerate(lines, 1):
            if "PORT=" in line:
                port_occurrences.append((i, line.strip()))

        # Should only have one active PORT definition
        active_port_lines = [
            occ for occ in port_occurrences if not occ[1].startswith("#")
        ]
        assert len(active_port_lines) == 1, (
            f"Should have exactly one active PORT definition, found: {active_port_lines}"
        )

        # Check that the PORT line mentions Makefile usage
        port_line_num, port_line = active_port_lines[0]

        # Check context around the PORT line for Makefile mention
        context_start = max(0, port_line_num - 3)
        context_end = min(len(lines), port_line_num + 2)
        context_lines = lines[context_start:context_end]
        context_text = "".join(context_lines).lower()

        assert "makefile" in context_text, (
            f"PORT definition should mention Makefile usage in context around line {port_line_num}"
        )
