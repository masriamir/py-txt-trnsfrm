FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_CONFIG=production \
    PYTHONIOENCODING=utf-8

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml ./
RUN uv pip install --system --no-cache-dir -e .

# Copy application code
COPY . .

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# Create non-root user
RUN addgroup --system --gid 1001 flask \
    && adduser --system --uid 1001 --ingroup flask flask

# Change ownership of the app directory (including logs)
RUN chown -R flask:flask /app
USER flask

# Create a volume mount point for logs
VOLUME ["/app/logs"]

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
