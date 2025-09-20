"""Test configuration and fixtures module.

This module provides pytest fixtures and configuration for testing the Flask
text transformation application. It includes fixtures for creating test
application instances, test clients, and test runners.
"""

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from app import create_app
from app.config import TestConfig

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner


@pytest.fixture
def app() -> Generator["Flask", None, None]:
    """Create and configure a new Flask app instance for each test.

    Creates a Flask application instance using TestConfig for isolated
    testing with proper test configuration settings.

    Yields:
        Flask: Configured Flask application instance for testing.
    """
    app = create_app(TestConfig)

    with app.app_context():
        yield app


@pytest.fixture
def client(app: "Flask") -> "FlaskClient":
    """Create a test client for the Flask app.

    Provides a test client that can make requests to the application
    without running a live server.

    Args:
        app: Flask application fixture.

    Returns:
        FlaskClient: Test client for making HTTP requests.
    """
    return app.test_client()


@pytest.fixture
def runner(app: "Flask") -> "FlaskCliRunner":
    """Create a test runner for the app's CLI commands.

    Provides a test runner for testing Flask CLI commands in isolation.

    Args:
        app: Flask application fixture.

    Returns:
        FlaskCliRunner: Test runner for CLI commands.
    """
    return app.test_cli_runner()
