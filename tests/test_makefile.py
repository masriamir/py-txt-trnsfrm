"""Test Makefile functionality and integration."""

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
        
        with open(makefile_path, 'r') as f:
            content = f.read()

        # Core workflow commands
        required_targets = [
            "setup:", "install:", "sync:", "clean:", "fresh:",
            "format:", "lint:", "fix:", "check:", "types:",
            "test:", "test-unit:", "test-api:", "test-all:", "test-fast:",
            "coverage:", "test-perf:",
            "run:", "run-prod:", "health:", "demo:",
            "security:", "security-quick:",
            "docker-build:", "docker-run:", "docker-stop:", "docker-clean:",
            "ci:", "deploy:",
            "help:", "version:"
        ]

        for target in required_targets:
            assert target in content, f"Required target '{target}' not found in Makefile"

    @pytest.mark.unit
    def test_makefile_has_proper_structure(self):
        """Test that the Makefile has proper structure and documentation."""
        makefile_path = Path(__file__).parent.parent / "Makefile"
        
        with open(makefile_path, 'r') as f:
            content = f.read()

        # Check for key structural elements
        assert "# Variables and Configuration" in content
        assert ".PHONY:" in content
        assert ".DEFAULT_GOAL := help" in content
        assert "UV := uv" in content
        assert "Future-Proof Template Section" in content

    @pytest.mark.unit
    def test_makefile_documentation_exists(self):
        """Test that comprehensive Makefile documentation exists."""
        docs_path = Path(__file__).parent.parent / "docs" / "MAKEFILE.md"
        assert docs_path.exists(), "docs/MAKEFILE.md should exist"
        
        with open(docs_path, 'r') as f:
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
            
            assert result.returncode == 0, f"Critical command 'make {command}' failed: {result.stderr}"


class TestMakefileIntegration:
    """Test integration with existing project tools."""

    @pytest.mark.integration
    def test_makefile_integrates_with_existing_scripts(self):
        """Test that Makefile properly integrates with existing scripts."""
        project_root = Path(__file__).parent.parent
        
        # Check that referenced scripts exist
        deploy_script = project_root / "deploy.sh"
        security_script = project_root / "run_security_analysis.sh"
        
        assert deploy_script.exists(), "deploy.sh should exist for deployment integration"
        assert security_script.exists(), "run_security_analysis.sh should exist for security integration"

    @pytest.mark.integration
    def test_makefile_respects_uv_dependency_groups(self):
        """Test that Makefile commands use proper UV dependency groups."""
        makefile_path = Path(__file__).parent.parent / "Makefile"
        
        with open(makefile_path, 'r') as f:
            content = f.read()

        # Check that install command uses proper groups
        assert "--group dev --group test --group security" in content
        assert "uv sync" in content

    @pytest.mark.unit
    def test_readme_references_makefile_docs(self):
        """Test that README properly references Makefile documentation."""
        readme_path = Path(__file__).parent.parent / "README.md"
        
        with open(readme_path, 'r') as f:
            content = f.read()

        # Check for reference to Makefile documentation
        assert "docs/MAKEFILE.md" in content or "MAKEFILE.md" in content, \
            "README should reference Makefile documentation"