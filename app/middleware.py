"""
Request logging middleware for capturing web request details.
"""
import time
from flask import request, g
from app.logging_config import get_logger

logger = get_logger(__name__)


def setup_request_logging(app):
    """Set up request logging middleware for the Flask app."""

    @app.before_request
    def log_request_start():
        """Log the start of each request with details."""
        g.start_time = time.time()

        # Get client IP (handling proxies)
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

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
            safe_headers = {k: v for k, v in request.headers if k.lower() not in
                          ['authorization', 'cookie', 'x-api-key']}
            logger.debug(f"Request headers: {dict(safe_headers)}")

    @app.after_request
    def log_request_end(response):
        """Log the end of each request with response details."""
        duration = time.time() - g.get('start_time', time.time())

        # Get client IP again for consistency
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

        # Determine log level based on status code
        if response.status_code < 400:
            log_level = logger.info
        elif response.status_code < 500:
            log_level = logger.warning
        else:
            log_level = logger.error

        # Log request completion
        log_level(f"Request completed: {request.method} {request.path} - "
                 f"Status: {response.status_code} - "
                 f"Duration: {duration:.3f}s - "
                 f"IP: {client_ip}")

        # Log response details in debug mode
        if app.debug:
            logger.debug(f"Response headers: {dict(response.headers)}")
            if response.content_length:
                logger.debug(f"Response size: {response.content_length} bytes")

        return response

    @app.errorhandler(404)
    def log_not_found(error):
        """Log 404 errors with additional context."""
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

        logger.warning(f"404 Not Found: {request.method} {request.path} - "
                      f"IP: {client_ip} - "
                      f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def log_server_error(error):
        """Log 500 errors with additional context."""
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()

        logger.error(f"500 Server Error: {request.method} {request.path} - "
                    f"IP: {client_ip} - "
                    f"Error: {str(error)}")
        return {"error": "Internal server error"}, 500

    logger.info("Request logging middleware initialized")
