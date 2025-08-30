#!/usr/bin/env python3
"""Gunicorn configuration file for production deployment.

Optimized for Gunicorn 23.0.0 with modern best practices.
"""

import multiprocessing
import os
import traceback
from pathlib import Path

# Server socket configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes configuration
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 120
graceful_timeout = 30
keepalive = 2

# Performance optimizations
preload_app = True
reuse_port = True

# Logging configuration
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Enhanced access log format with more details
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '
    "response_time=%(D)s request_id=%({X-Request-ID}i)s"
)

# Process naming
proc_name = "py-txt-trnsfrm"

# Server mechanics
daemon = False


# PID file configuration with secure defaults and fallback strategy
def get_secure_pidfile_path():
    """Get secure PID file path with environment variable support and fallback strategy.

    Returns:
        str: Secure path for PID file based on environment and permissions.
    """
    # Check for explicit environment variable
    env_pidfile = os.environ.get("GUNICORN_PIDFILE")
    if env_pidfile:
        return env_pidfile

    # Secure defaults with fallback strategy
    secure_paths = [
        "/var/run/gunicorn.pid",  # Standard system location
        "/run/gunicorn.pid",  # Modern systemd location
        "./gunicorn.pid",  # Current directory fallback
    ]

    for pidfile_path in secure_paths:
        try:
            # Test if directory is writable
            parent_dir = Path(pidfile_path).parent
            if parent_dir.exists() and os.access(parent_dir, os.W_OK):
                return pidfile_path
        except (OSError, PermissionError):
            continue

    # Final fallback to current directory (always writable)
    return "./gunicorn.pid"


pidfile = get_secure_pidfile_path()
user = None
group = None
tmp_upload_dir = None

# SSL configuration (if certificates are provided)
keyfile = os.environ.get("SSL_KEY_FILE")
certfile = os.environ.get("SSL_CERT_FILE")
ssl_version = 2  # Use TLS
ciphers = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"

# Security headers and settings
forwarded_allow_ips = "*"
secure_scheme_headers = {
    "X-FORWARDED-PROTOCOL": "ssl",
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}

# Modern Gunicorn 23.0.0 features
# Enable HTTP/2 support if available
enable_stdio_inheritance = True

# Resource limits
worker_memory_limit = int(
    os.environ.get("WORKER_MEMORY_LIMIT", 512 * 1024 * 1024)
)  # 512MB

# Monitoring and health checks
max_worker_restarts = 5
restart_timeout = 30


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn %s server", server.version)
    server.log.info("Listening at: %s", server.address)
    server.log.info("Using worker class: %s", server.worker_class_str)
    server.log.info("Number of workers: %d", server.cfg.workers)


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Gunicorn server")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")
    import sys
    import threading

    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for thread_id, frame in sys._current_frames().items():
        code.append(f"\n# Thread: {id2name.get(thread_id, '')}({thread_id})")
        for filename, lineno, name, line in traceback.extract_stack(frame):
            code.append(f'  File: "{filename}", line {lineno}, in {name}')
            if line:
                code.append(f"    {line.strip()}")
    worker.log.debug("\n".join(code))


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.debug("Worker spawned (pid: %s)", worker.pid)


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.debug("Worker spawned (pid: %s)", worker.pid)


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.debug("Worker initialized (pid: %s)", worker.pid)


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing")


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s", req.method, req.uri)


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass


def child_exit(server, worker):
    """Called just after a worker has been exited, in the master process."""
    server.log.info("Worker exited (pid: %s)", worker.pid)


def worker_exit(server, worker):
    """Called just after a worker has been exited, in the worker process."""
    worker.log.info("Worker exiting (pid: %s)", worker.pid)


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info("Number of workers changed from %s to %s", old_value, new_value)


def on_exit(server):
    """Called just before exiting."""
    server.log.info("Shutting down Gunicorn server")
