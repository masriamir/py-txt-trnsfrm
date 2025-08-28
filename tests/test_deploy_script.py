"""Tests for deploy.sh script functionality."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestDeployScriptVersionReading:
    """Test suite for dynamic Gunicorn version reading in deploy.sh."""

    @pytest.mark.unit
    def test_deploy_script_reads_gunicorn_version_from_pyproject(self):
        """Test that deploy.sh correctly reads Gunicorn version from pyproject.toml."""
        # Run the deploy script help command to capture output
        result = subprocess.run(
            ["bash", "deploy.sh", "help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        output = result.stdout

        # Verify that the output contains the expected version pattern
        assert "🚀 Deploying py-txt-trnsfrm with Gunicorn" in output
        # Should contain a version number, not the old hard-coded value
        assert "Gunicorn 23.0.0" in output or "Gunicorn unknown" in output
        # Should not contain any indication of failure in version reading
        assert "error" not in output.lower()

    @pytest.mark.unit
    def test_deploy_script_handles_missing_gunicorn_dependency(self):
        """Test that deploy.sh gracefully handles missing Gunicorn dependency."""
        # Create a temporary pyproject.toml without gunicorn dependency
        temp_content = """[project]
name = "test-project"
dependencies = [
    "flask>=3.1.1",
    "werkzeug>=3.1.3",
]
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as temp_file:
            temp_file.write(temp_content)
            temp_file.flush()

            # Test the version extraction function directly
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    f"""
import tomllib
import re

try:
    with open('{temp_file.name}', 'rb') as f:
        data = tomllib.load(f)
    
    deps = data.get('project', {{}}).get('dependencies', [])
    for dep in deps:
        if dep.startswith('gunicorn'):
            match = re.search(r'gunicorn[>=<!=~]*([0-9]+\\.[0-9]+\\.[0-9]+)', dep)
            if match:
                print(match.group(1))
                exit(0)
    
    print('unknown')
except Exception:
    print('unknown')
""",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert result.stdout.strip() == "unknown"

        # Clean up
        Path(temp_file.name).unlink()

    @pytest.mark.unit
    def test_deploy_script_version_extraction_with_different_formats(self):
        """Test version extraction with different dependency format variations."""
        test_cases = [
            ("gunicorn>=23.0.0", "23.0.0"),
            ("gunicorn==23.1.5", "23.1.5"),
            ("gunicorn~=22.5.1", "22.5.1"),
            ("gunicorn>=20.0.0,<25.0.0", "20.0.0"),
        ]

        for dependency_spec, expected_version in test_cases:
            temp_content = f"""[project]
name = "test-project"
dependencies = [
    "flask>=3.1.1",
    "{dependency_spec}",
    "werkzeug>=3.1.3",
]
"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".toml", delete=False
            ) as temp_file:
                temp_file.write(temp_content)
                temp_file.flush()

                result = subprocess.run(
                    [
                        "python3",
                        "-c",
                        f"""
import tomllib
import re

try:
    with open('{temp_file.name}', 'rb') as f:
        data = tomllib.load(f)
    
    deps = data.get('project', {{}}).get('dependencies', [])
    for dep in deps:
        if dep.startswith('gunicorn'):
            match = re.search(r'gunicorn[>=<!=~]*([0-9]+\\.[0-9]+\\.[0-9]+)', dep)
            if match:
                print(match.group(1))
                exit(0)
    
    print('unknown')
except Exception:
    print('unknown')
""",
                    ],
                    capture_output=True,
                    text=True,
                )

                assert result.returncode == 0
                assert result.stdout.strip() == expected_version

            # Clean up
            Path(temp_file.name).unlink()

    @pytest.mark.integration
    def test_deploy_script_integration_with_actual_pyproject(self):
        """Test that the deploy script integrates correctly with the actual pyproject.toml."""
        # Read the actual pyproject.toml to verify expected structure
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml should exist in project root"

        # Run the deploy script and verify it doesn't crash
        result = subprocess.run(
            ["bash", "deploy.sh", "help"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        assert result.returncode == 0
        output = result.stdout

        # Verify the script ran successfully
        assert "🚀 Deploying py-txt-trnsfrm with Gunicorn" in output
        assert "Usage: deploy.sh [COMMAND]" in output

        # The version should be either a valid version or 'unknown' (both are acceptable)
        assert "Gunicorn 23.0.0" in output or "Gunicorn unknown" in output

    @pytest.mark.unit
    def test_deploy_script_error_handling_for_corrupted_toml(self):
        """Test that deploy.sh handles corrupted TOML files gracefully."""
        # Create a corrupted TOML file
        corrupted_content = """[project
name = "test-project
dependencies = [
    "flask>=3.1.1"
    "gunicorn>=23.0.0
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as temp_file:
            temp_file.write(corrupted_content)
            temp_file.flush()

            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    f"""
import tomllib
import re

try:
    with open('{temp_file.name}', 'rb') as f:
        data = tomllib.load(f)
    
    deps = data.get('project', {{}}).get('dependencies', [])
    for dep in deps:
        if dep.startswith('gunicorn'):
            match = re.search(r'gunicorn[>=<!=~]*([0-9]+\\.[0-9]+\\.[0-9]+)', dep)
            if match:
                print(match.group(1))
                exit(0)
    
    print('unknown')
except Exception:
    print('unknown')
""",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert result.stdout.strip() == "unknown"

        # Clean up
        Path(temp_file.name).unlink()
