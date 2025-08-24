"""Main blueprint module for the Flask application.

This module initializes the main blueprint for the Flask application,
which contains the primary routes for the text transformation functionality.
"""

from flask import Blueprint

from app.logging_config import get_logger

logger = get_logger(__name__)

bp = Blueprint("main", __name__)
logger.debug("Main blueprint created")

# Import routes to register them with the blueprint
from app.main import routes as routes  # noqa: F401,E402

logger.debug("Main blueprint routes loaded")
