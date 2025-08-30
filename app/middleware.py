"""Request logging middleware for capturing web request details.

This module provides comprehensive request and response logging middleware
for Flask applications. It captures detailed information about incoming
requests including timing, client information, headers, and response details.
"""

import time

from flask import g, request

from app.logging_config import get_logger

logger = get_logger(__name__)


def setup_request_logging(app):  # noqa: C901  # Complex middleware function
    """Set up comprehensive request logging middleware for the Flask application.

    Configures before_request and after_request handlers to log detailed
    information about all HTTP requests and responses. Includes timing
    information, client details, and error handling.

    Args:
        app: Flask application instance to configure with request logging.
    """

    @app.before_request
    def log_request_start():
        """Log the start of each request with detailed information.

        Captures and logs request initiation details including client IP,
        HTTP method, path, headers, and query parameters. Stores start
        time for duration calculation.
        """
        g.start_time = time.time()

        # Get client IP (handling proxies)
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()

        # Log basic request info
        logger.info(f"Request started: {request.method} {request.path}")
        logger.debug(f"Client IP: {client_ip}")
        logger.debug(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        logger.debug(f"Referrer: {request.headers.get('Referer', 'None')}")

        # Log query parameters if present
        if request.args:
            logger.debug(f"Query params: {dict(request.args)}")

        # Log request headers in debug mode (excluding sensitive ones)
        if app.debug:
            safe_headers = {
                k: v
                for k, v in request.headers
                if k.lower() not in ["authorization", "cookie", "x-api-key"]
            }
            logger.debug(f"Request headers: {dict(safe_headers)}")

    @app.after_request
    def log_request_end(response):
        """Log the completion of each request with response details.

        Captures and logs request completion information including response
        status code, duration, and response headers in debug mode.

        Args:
            response: Flask response object.

        Returns:
            Flask response object (unchanged).
        """
        duration = time.time() - g.get("start_time", time.time())

        # Get client IP again for consistency
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()

        # Determine log level based on status code
        if response.status_code < 400:
            log_level = logger.info
        elif response.status_code < 500:
            log_level = logger.warning
        else:
            log_level = logger.error

        # Log request completion
        log_level(
            f"Request completed: {request.method} {request.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"IP: {client_ip}"
        )

        # Log response details in debug mode
        if app.debug:
            logger.debug(f"Response headers: {dict(response.headers)}")
            if response.content_length:
                logger.debug(f"Response size: {response.content_length} bytes")

        return response

    @app.errorhandler(404)
    def log_not_found(error):
        """Log 404 Not Found errors with additional context.

        Captures and logs detailed information about 404 errors including
        client IP, user agent, and requested path for debugging purposes.

        Args:
            error: Flask error object for the 404 error.

        Returns:
            tuple: JSON error response and 404 status code.
        """
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()

        logger.warning(
            f"404 Not Found: {request.method} {request.path} - "
            f"IP: {client_ip} - "
            f"User Agent: {request.headers.get('User-Agent', 'Unknown')}"
        )
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def log_server_error(error):
        """Log 500 Internal Server errors with additional context.

        Captures and logs detailed information about server errors including
        client IP and error details for debugging and monitoring.

        Args:
            error: Flask error object for the 500 error.

        Returns:
            tuple: JSON error response and 500 status code.
        """
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()

        logger.error(
            f"500 Server Error: {request.method} {request.path} - "
            f"IP: {client_ip} - "
            f"Error: {str(error)}"
        )
        return {"error": "Internal server error"}, 500

    logger.info("Request logging middleware initialized")
