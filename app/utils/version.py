"""Version extraction utility module.

This module provides functionality to dynamically extract the application version
from pyproject.toml with caching for performance optimization.
"""

from pathlib import Path

from app.logging_config import get_logger

logger = get_logger(__name__)

# Cache for the application version to avoid repeated file parsing
_cached_version: str | None = None


def get_application_version() -> str:
    """Get the application version from pyproject.toml with caching.

    Reads and caches the version from pyproject.toml on first call.
    Subsequent calls return the cached version for performance.

    Returns:
        str: Application version string from pyproject.toml.
             Falls back to "unknown" if version cannot be determined.

    Example:
        >>> version = get_application_version()
        >>> print(f"App version: {version}")
        App version: 0.1.0
    """
    global _cached_version

    # Return cached version if available
    if _cached_version is not None:
        return _cached_version

    # Try to extract version from pyproject.toml
    try:
        _cached_version = _extract_version_from_pyproject()
        logger.info(f"Application version loaded: {_cached_version}")
        return _cached_version
    except Exception as e:
        logger.error(f"Failed to extract version from pyproject.toml: {e}")
        # Fallback to unknown version
        _cached_version = "unknown"
        return _cached_version


def _extract_version_from_pyproject() -> str:
    """Extract version from pyproject.toml file.

    Parses the pyproject.toml file to find the version field under [project].
    Uses a simple string parsing approach to avoid heavy dependencies.

    Returns:
        str: Version string found in pyproject.toml.

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found.
        ValueError: If version field cannot be parsed from the file.
    """
    # Find pyproject.toml relative to this module
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # Go up two levels to project root
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    # Read and parse the file for version
    with open(pyproject_path, encoding="utf-8") as f:
        content = f.read()

    # Simple parsing to find version line
    # Look for version = "x.y.z" pattern under [project] section
    lines = content.split("\n")
    in_project_section = False

    for line in lines:
        line = line.strip()

        # Check if we're entering the [project] section
        if line == "[project]":
            in_project_section = True
            continue

        # Check if we're leaving the [project] section
        if in_project_section and line.startswith("[") and line != "[project]":
            in_project_section = False
            continue

        # Look for version line in project section
        if in_project_section and line.startswith("version"):
            # Parse version = "x.y.z" format
            if "=" in line:
                _, version_part = line.split("=", 1)
                version_part = version_part.strip()
                # Remove quotes if present
                if version_part.startswith('"') and version_part.endswith('"'):
                    version = version_part[1:-1]
                elif version_part.startswith("'") and version_part.endswith("'"):
                    version = version_part[1:-1]
                else:
                    version = version_part

                if version:
                    return version

    raise ValueError("Version field not found in pyproject.toml [project] section")


def reset_version_cache() -> None:
    """Reset the cached version for testing purposes.

    This function is primarily intended for use in tests to ensure
    version reloading behavior can be verified.
    """
    global _cached_version
    _cached_version = None
    logger.debug("Version cache reset")
