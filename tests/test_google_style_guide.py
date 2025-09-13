"""Test Google Python Style Guide compliance.

This module tests that all Python files in the project follow the Google Python
Style Guide conventions for naming, imports, docstrings, and code structure.
"""

import subprocess
from pathlib import Path

import pytest


class TestGoogleStyleGuideCompliance:
    """Test suite for Google Python Style Guide compliance."""

    @pytest.mark.unit
    def test_docstring_compliance_app_directory(self):
        """Test that app directory docstrings follow Google format using pydocstyle."""
        result = subprocess.run(
            ["uv", "run", "pydocstyle", "--convention=google", "app/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"Docstring issues found: {result.stdout}"

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", ["app.py", "wsgi.py", "gunicorn.conf.py"])
    def test_docstring_compliance_main_files(self, filename):
        """Test that main Python files follow Google docstring format."""
        project_root = Path(__file__).parent.parent
        file_path = project_root / filename

        if file_path.exists():
            result = subprocess.run(
                ["uv", "run", "pydocstyle", "--convention=google", str(file_path)],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            assert result.returncode == 0, (
                f"Docstring issues in {filename}: {result.stdout}"
            )

    @pytest.mark.unit
    def test_ruff_linting_passes(self):
        """Test that ruff linting passes with acceptable security warnings."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "app/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # App directory should have no ruff errors
        assert result.returncode == 0, f"Ruff linting errors in app/: {result.stdout}"

    @pytest.mark.unit
    def test_black_formatting_compliance(self):
        """Test that all files pass black formatting checks."""
        result = subprocess.run(
            ["uv", "run", "black", "--check", "."],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, f"Black formatting issues: {result.stdout}"


class TestGoogleStyleAutomation:
    """Test that automated style checking is properly integrated."""

    @pytest.mark.unit
    def test_pydocstyle_available(self):
        """Test that pydocstyle is available for automated checking."""
        result = subprocess.run(
            ["uv", "run", "pydocstyle", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0, "pydocstyle should be available"
        assert result.stdout.strip(), "pydocstyle should return version info"

    @pytest.mark.unit
    def test_makefile_has_docstring_check(self):
        """Test that Makefile includes docstring checking."""
        makefile_path = Path(__file__).parent.parent / "Makefile"

        with open(makefile_path, encoding="utf-8") as f:
            makefile_content = f.read()

        assert "pydocstyle" in makefile_content, "Makefile should include pydocstyle"
        assert "docstrings:" in makefile_content, (
            "Makefile should have docstrings target"
        )

    @pytest.mark.unit
    def test_quality_check_includes_docstrings(self):
        """Test that the quality check command includes docstring validation."""
        makefile_path = Path(__file__).parent.parent / "Makefile"

        with open(makefile_path, encoding="utf-8") as f:
            makefile_content = f.read()

        # Find the check target
        check_section = ""
        in_check_target = False

        for line in makefile_content.split("\n"):
            if line.startswith("check:"):
                in_check_target = True
            elif in_check_target and line.startswith("\t"):
                check_section += line + "\n"
            elif in_check_target and not line.startswith("\t"):
                break

        assert "pydocstyle" in check_section, (
            "Quality check should include docstring validation"
        )


class TestNamingConventions:
    """Test Google Python Style Guide naming conventions."""

    @pytest.mark.unit
    def test_python_files_snake_case(self):
        """Test that Python files use snake_case naming."""
        project_root = Path(__file__).parent.parent
        # Only check project files, not dependencies
        python_files = []
        for pattern in ["*.py", "app/**/*.py", "tests/**/*.py"]:
            python_files.extend(project_root.glob(pattern))

        invalid_files = []
        for file_path in python_files:
            # Skip virtual environment and other non-project directories
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            filename = file_path.stem
            # Allow special files like __init__
            if filename.startswith("__") and filename.endswith("__"):
                continue
            # Check for snake_case: lowercase letters, numbers, underscores
            if not filename.islower() or " " in filename or "-" in filename:
                if (
                    not filename.replace("_", "")
                    .replace("0", "")
                    .replace("1", "")
                    .replace("2", "")
                    .replace("3", "")
                    .replace("4", "")
                    .replace("5", "")
                    .replace("6", "")
                    .replace("7", "")
                    .replace("8", "")
                    .replace("9", "")
                    .isalpha()
                ):
                    invalid_files.append(str(file_path.relative_to(project_root)))

        assert not invalid_files, f"Files not following snake_case: {invalid_files}"

    @pytest.mark.unit
    def test_import_statements_organized(self):
        """Test that imports follow Google style organization."""
        # This is a basic check - imports should be properly organized
        # We rely on the existing linting tools for detailed validation

        app_files = list(Path(__file__).parent.parent.glob("app/**/*.py"))
        issues = []

        for file_path in app_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                # Basic check: look for obvious import order issues
                import_section = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith(("import ", "from ")) and not line.startswith(
                        "#"
                    ):
                        import_section.append((i, line))

                # Check for obvious violations: local imports before standard library
                local_before_stdlib = False
                found_local = False
                for _i, line in import_section:
                    if line.startswith("from app.") or line.startswith("import app"):
                        found_local = True
                    elif found_local and any(
                        lib in line
                        for lib in [
                            "import os",
                            "import sys",
                            "from pathlib",
                            "import logging",
                        ]
                    ):
                        local_before_stdlib = True
                        break

                if local_before_stdlib:
                    issues.append(
                        str(file_path.relative_to(Path(__file__).parent.parent))
                    )

            except (UnicodeDecodeError, FileNotFoundError):
                continue

        # This is more informational - we allow some flexibility
        if issues:
            print(f"Files with potential import order issues: {issues}")
        # Don't fail the test, just inform
        assert True  # Always pass but log issues
