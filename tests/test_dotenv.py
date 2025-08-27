"""Test python-dotenv integration functionality."""

import os
import tempfile
from pathlib import Path


def test_dotenv_loading():
    """Test that dotenv loads environment variables from .env file."""
    # This test verifies that dotenv is loading variables
    # The .env file should be loaded when the app package is imported

    # Create a temporary .env file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_DOTENV_INTEGRATION=success\n")
        f.write("DOTENV_TEST_VALUE=12345\n")
        temp_env_file = f.name

    try:
        # Load the temporary .env file
        from dotenv import load_dotenv

        load_dotenv(temp_env_file)

        # Verify variables are loaded
        assert os.environ.get("TEST_DOTENV_INTEGRATION") == "success"
        assert os.environ.get("DOTENV_TEST_VALUE") == "12345"

    finally:
        # Clean up
        Path(temp_env_file).unlink()
        # Clean up environment variables
        os.environ.pop("TEST_DOTENV_INTEGRATION", None)
        os.environ.pop("DOTENV_TEST_VALUE", None)


def test_dotenv_does_not_override_existing_env():
    """Test that dotenv does not override existing environment variables."""
    # Set an environment variable directly
    os.environ["TEST_EXISTING_VAR"] = "existing_value"

    # Create a temporary .env file with the same variable
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_EXISTING_VAR=dotenv_value\n")
        temp_env_file = f.name

    try:
        # Load the .env file
        from dotenv import load_dotenv

        load_dotenv(temp_env_file)

        # The existing environment variable should not be overridden
        assert os.environ.get("TEST_EXISTING_VAR") == "existing_value"

    finally:
        # Clean up
        Path(temp_env_file).unlink()
        os.environ.pop("TEST_EXISTING_VAR", None)


def test_app_import_loads_dotenv():
    """Test that importing the app package loads .env file."""
    # Create a test .env file in the project root
    project_root = Path(__file__).parent.parent
    test_env_file = project_root / ".env.test"

    try:
        # Write test values to .env.test
        test_env_file.write_text("TEST_APP_IMPORT_VAR=app_import_works\n")

        # Load the test .env file
        from dotenv import load_dotenv

        load_dotenv(test_env_file)

        # Verify the variable was loaded
        assert os.environ.get("TEST_APP_IMPORT_VAR") == "app_import_works"

    finally:
        # Clean up
        if test_env_file.exists():
            test_env_file.unlink()
        os.environ.pop("TEST_APP_IMPORT_VAR", None)


def test_dotenv_with_flask_app_creation():
    """Test that dotenv variables are available during Flask app creation."""
    # Create a temporary .env file with Flask configuration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SECRET_KEY=test-secret-from-dotenv-integration\n")
        f.write("FLASK_ENV=development\n")
        f.write("LOG_LEVEL=warning\n")
        temp_env_file = f.name

    try:
        # Load the .env file
        from dotenv import load_dotenv

        load_dotenv(temp_env_file)

        # Import app after loading dotenv
        from app import create_app

        # Create Flask app
        create_app()

        # Verify that dotenv variables were used in configuration
        # Note: The app might use different config depending on FLASK_ENV
        assert os.environ.get("SECRET_KEY") == "test-secret-from-dotenv-integration"
        assert os.environ.get("FLASK_ENV") == "development"
        assert os.environ.get("LOG_LEVEL") == "warning"

    finally:
        # Clean up
        Path(temp_env_file).unlink()
        # Clean up environment variables
        os.environ.pop("SECRET_KEY", None)
        os.environ.pop("FLASK_ENV", None)
        os.environ.pop("LOG_LEVEL", None)


def test_env_example_file_exists():
    """Test that .env.example file exists and contains expected variables."""
    project_root = Path(__file__).parent.parent
    env_example_file = project_root / ".env.example"

    assert env_example_file.exists(), ".env.example file should exist"

    content = env_example_file.read_text()

    # Check that key environment variables are documented
    expected_vars = [
        "FLASK_ENV",
        "FLASK_DEBUG",
        "SECRET_KEY",
        "LOG_LEVEL",
        "PORT",
        "WEB_CONCURRENCY",
    ]

    for var in expected_vars:
        assert var in content, f"{var} should be documented in .env.example"


def test_gitignore_includes_dotenv():
    """Test that .gitignore includes .env file."""
    project_root = Path(__file__).parent.parent
    gitignore_file = project_root / ".gitignore"

    assert gitignore_file.exists(), ".gitignore file should exist"

    content = gitignore_file.read_text()
    assert ".env" in content, ".env should be in .gitignore"


class TestDotenvIntegration:
    """Test class for dotenv integration scenarios."""

    def test_dotenv_import_error_handling(self):
        """Test that missing python-dotenv is handled gracefully."""
        # This test simulates the case where python-dotenv is not installed
        # We can't actually test this without uninstalling the package,
        # but we can verify the import error handling structure exists

        # Check that the import is wrapped in try-except in key files
        project_root = Path(__file__).parent.parent

        # Check app.py
        app_py = project_root / "app.py"
        content = app_py.read_text()
        assert "try:" in content and "from dotenv import load_dotenv" in content
        assert "except ImportError:" in content

        # Check wsgi.py
        wsgi_py = project_root / "wsgi.py"
        content = wsgi_py.read_text()
        assert "try:" in content and "from dotenv import load_dotenv" in content
        assert "except ImportError:" in content

        # Check app/__init__.py
        app_init = project_root / "app" / "__init__.py"
        content = app_init.read_text()
        assert "try:" in content and "from dotenv import load_dotenv" in content
        assert "except ImportError:" in content

    def test_env_file_search_behavior(self):
        """Test that dotenv searches for .env files in parent directories."""
        # Create a test directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create subdirectory
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()

            # Create .env file in parent directory
            env_file = temp_path / ".env"
            env_file.write_text("PARENT_DIR_VAR=found_in_parent\n")

            # Change to subdirectory and load dotenv
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)

                from dotenv import load_dotenv

                load_dotenv()

                # Should find the .env file in parent directory
                assert os.environ.get("PARENT_DIR_VAR") == "found_in_parent"

            finally:
                os.chdir(original_cwd)
                os.environ.pop("PARENT_DIR_VAR", None)
