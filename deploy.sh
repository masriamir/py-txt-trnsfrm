#!/bin/bash
set -e

echo "🚀 Deploying py-txt-trnsfrm with Gunicorn 23.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GUNICORN_CONFIG="gunicorn.conf.py"
WSGI_MODULE="wsgi:application"
DEFAULT_PORT=5000
DEFAULT_WORKERS=4

# Environment variables with defaults
export PORT=${PORT:-$DEFAULT_PORT}
export WEB_CONCURRENCY=${WEB_CONCURRENCY:-$DEFAULT_WORKERS}
export FLASK_ENV=${FLASK_ENV:-production}

# Set LOG_LEVEL based on environment - debug for development, info for others
if [ "${FLASK_ENV}" = "development" ]; then
    export LOG_LEVEL=${LOG_LEVEL:-debug}
else
    export LOG_LEVEL=${LOG_LEVEL:-info}
fi

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Port: ${PORT}"
echo -e "  Workers: ${WEB_CONCURRENCY}"
echo -e "  Log Level: ${LOG_LEVEL}"
echo -e "  Flask Environment: ${FLASK_ENV}"
echo

# Function to check if port is available
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Warning: Port $PORT is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to start Gunicorn with monitoring
start_gunicorn() {
    echo -e "${GREEN}Starting Gunicorn 23.0.0 server...${NC}"

    # Install/update dependencies first
    echo -e "${BLUE}Installing dependencies...${NC}"
    uv sync

    # Run pre-deployment checks
    echo -e "${BLUE}Running pre-deployment checks...${NC}"
    uv run python -c "import app; print('✅ Application imports successfully')"

    # Check configuration file
    if [ ! -f "$GUNICORN_CONFIG" ]; then
        echo -e "${RED}Error: Gunicorn configuration file not found: $GUNICORN_CONFIG${NC}"
        exit 1
    fi

    # Start Gunicorn with the new configuration
    echo -e "${GREEN}Starting server on port $PORT with $WEB_CONCURRENCY workers...${NC}"
    exec uv run gunicorn \
        --config "$GUNICORN_CONFIG" \
        --bind "0.0.0.0:$PORT" \
        --workers "$WEB_CONCURRENCY" \
        --log-level "$LOG_LEVEL" \
        --access-logfile - \
        --error-logfile - \
        "$WSGI_MODULE"
}

# Function to run development server
start_development() {
    echo -e "${YELLOW}Starting development server...${NC}"
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    uv run flask --app app run --host=0.0.0.0 --port="$PORT" --debug
}

# Function to test deployment
test_deployment() {
    echo -e "${BLUE}Testing deployment...${NC}"

    # Start server in background
    start_gunicorn &
    SERVER_PID=$!

    # Wait for server to start
    sleep 5

    # Test health endpoint
    if curl -f "http://localhost:$PORT/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi

    # Test main endpoint
    if curl -f "http://localhost:$PORT/" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Main page accessible${NC}"
    else
        echo -e "${RED}❌ Main page not accessible${NC}"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi

    # Stop test server
    kill $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Deployment test passed${NC}"
}

# Function to show usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start production server (default)"
    echo "  dev       Start development server"
    echo "  test      Test deployment"
    echo "  docker    Build and run Docker container"
    echo
    echo "Environment Variables:"
    echo "  PORT              Server port (default: 5000)"
    echo "  WEB_CONCURRENCY   Number of workers (default: 4)"
    echo "  LOG_LEVEL         Log level (default: info)"
    echo "  FLASK_ENV         Flask environment (default: production)"
    echo "  GUNICORN_PIDFILE  PID file location (default: secure system directories)"
}

# Main script logic
case "${1:-start}" in
    "start")
        check_port || true
        start_gunicorn
        ;;
    "dev")
        check_port || true
        start_development
        ;;
    "test")
        test_deployment
        ;;
    "docker")
        echo -e "${BLUE}Building Docker image...${NC}"
        docker build -t py-txt-trnsfrm:latest .
        echo -e "${GREEN}Starting Docker container...${NC}"
        docker run --rm -p "$PORT:$PORT" py-txt-trnsfrm:latest
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        exit 1
        ;;
esac
