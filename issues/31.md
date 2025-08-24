# Secure PID file location configuration

## Description

Currently, the application uses `/tmp` for PID files which can be a security risk in shared environments. The temporary directory may have loose permissions that could allow other users to interfere with the PID file.

## Current Implementation
```python
# Current approach uses /tmp by default
pidfile = "/tmp/gunicorn.pid"
```

## Proposed Solution
Use a more secure location with proper file permissions or make it configurable via environment variable:

```python
pidfile = os.environ.get("GUNICORN_PIDFILE", "/var/run/gunicorn.pid")
```

## Benefits
- Enhanced security in shared environments
- Configurable PID file location
- Follows best practices for system service files

## References
- Originally identified in PR #29: https://github.com/masriamir/py-txt-trnsfrm/pull/29#discussion_r2286174149