# py-txt-trnsfrm Development Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Dependencies
- **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH"`
- **Install all dependencies**: `uv sync --group dev --group test --group security` -- takes 3-4 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
- **Verify installation**: `uv run python -c "import app; print('✅ Application imports successfully')"`

### Code Quality Tools
- **Linting**: `uv run ruff check .` -- takes <1 second. Passes cleanly.
- **Formatting**: `uv run black --check .` -- takes <1 second. Currently fails on 7 files, run `uv run black .` to fix.
- **Type checking**: `uv run mypy .` -- takes 7-8 seconds. Currently has 99 errors, mostly missing type annotations.

### Testing
- **Run all tests (excluding performance)**: `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" -n 0` -- takes 1-2 seconds. Currently 47 passed, 1 failed (expected).
- **Run specific test categories**: 
  - `uv run pytest -m unit -n 0` -- Unit tests only
  - `uv run pytest -m integration -n 0` -- Integration tests
  - `uv run pytest -m api -n 0` -- API endpoint tests
  - `uv run pytest -m smoke -n 0` -- Critical functionality tests
- **Run with coverage**: Tests include coverage reporting to `reports/coverage/`
- **Performance tests**: `BASE_URL=http://localhost:5000 uv run pytest tests/performance/test_api_performance.py --benchmark-only -n 0` (requires running Flask app first)
- **NOTE**: Must use `-n 0` to disable xdist parallel execution when pytest-benchmark is installed

### Security Analysis
- **Run comprehensive security scan**: `./run_security_analysis.sh` -- may take 5+ minutes or timeout on safety scan. NEVER CANCEL. Set timeout to 10+ minutes.
- **Individual security tools**:
  - `uv run bandit -r app/` -- Code security analysis (currently 4 low-severity issues) takes <1 second
  - `uv run safety scan` -- Dependency vulnerability scan (may timeout, that's expected)

### Running the Application

#### Development Mode
- **Start development server**: `FLASK_ENV=development uv run python app.py` -- starts on port 5000
- **Health check**: `curl http://localhost:5000/health` -- returns JSON health status
- **Test transformation**: `curl -X POST http://localhost:5000/transform -H "Content-Type: application/json" -d '{"text": "Hello World", "transformation": "alternate_case"}'`

#### Production Mode (with Gunicorn)
- **Production deployment requires SECRET_KEY environment variable**
- **Start with deploy script**: `SECRET_KEY=your-secret-key ./deploy.sh start` 
- **Test deployment**: `SECRET_KEY=your-secret-key ./deploy.sh test` -- takes 15-20 seconds. NEVER CANCEL. Set timeout to 2+ minutes.
- **Development deployment**: `FLASK_ENV=development ./deploy.sh dev` (has known gunicorn config issue)

## Validation

### Manual Testing Requirements
- **ALWAYS** test the application after making changes:
  1. Run `uv run python -c "import app; print('✅ Import test passed')"`
  2. Start the development server: `FLASK_ENV=development uv run python app.py`
  3. Test health endpoint: `curl http://localhost:5000/health`
  4. Test at least one transformation: `curl -X POST http://localhost:5000/transform -H "Content-Type: application/json" -d '{"text": "test", "transformation": "alternate_case"}'`
  5. Stop the server with Ctrl+C

### Pre-commit Validation
- **ALWAYS run before committing**:
  1. `uv run ruff check .` -- must pass
  2. `uv run black .` -- to fix formatting issues
  3. `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" -n 0` -- should have minimal failures
  4. Manual application test as described above

## Known Issues and Limitations

### Test Suite Issues
- **Performance tests**: Require `concurrent` and `load` markers in pytest.ini (already added)
- **Parallel execution conflict**: pytest-benchmark requires `-n 0` flag to disable xdist parallel execution
- **Property-based test**: `test_transform_property_based` fails due to Hypothesis function-scoped fixture health check
- **Security test**: `test_json_input_validation` fails because app doesn't sanitize HTML in transformations (by design)

### Code Quality Issues  
- **Type annotations**: 99 mypy errors due to missing type annotations in tests and some application files
- **Black formatting**: 7 files need reformatting
- **Security**: 4 low-severity Bandit warnings (all acceptable - test secrets and non-cryptographic random usage)

### Deployment Issues
- **Production mode**: Requires SECRET_KEY environment variable
- **Gunicorn config**: Has AttributeError in on_starting hook (server.version doesn't exist)
- **Docker**: Available but not tested in validation

### Timing Expectations
- **NEVER CANCEL** these operations:
  - `uv sync` -- 3-4 minutes 
  - `./run_security_analysis.sh` -- up to 5 minutes (safety scan may timeout)
  - `./deploy.sh test` -- 2+ minutes
- **Fast operations** (<10 seconds):
  - Linting with ruff
  - Running tests
  - Security scan with bandit
  - Application startup

## Repository Structure

### Key Projects
- **app/**: Main Flask application package
  - **main/**: Blueprint with routes and main endpoints  
  - **utils/**: Text transformation utilities
  - **static/**: CSS and JavaScript assets
  - **templates/**: Jinja2 HTML templates
- **tests/**: Comprehensive test suite with performance, security, and functional tests
- **.github/workflows/**: CI/CD pipelines (ci.yml, security-nightly.yml, release.yml)
- **docs/**: Documentation including CI/CD pipeline details and UV troubleshooting

### Important Files
- **pyproject.toml**: Project configuration and dependencies (uses uv for package management)
- **uv.lock**: Dependency lock file (always commit changes)
- **pytest.ini**: Test configuration with markers and coverage settings
- **gunicorn.conf.py**: Production server configuration
- **deploy.sh**: Deployment script with multiple modes
- **run_security_analysis.sh**: Security analysis automation

### Text Transformations Available
- alternate_case, rainbow_html, leet_speak, backwards, upside_down
- stutter, zalgo_text, morse_code, binary, rot13
- spongebob_case, wave_text, shizzle_speak

## Common Commands Reference

```bash
# Complete setup from fresh clone
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --group dev --group test --group security  # 3-4 minutes

# Development workflow
uv run ruff check .
uv run black .
uv run pytest --ignore=tests/performance -k "not test_transform_property_based" -n 0
FLASK_ENV=development uv run python app.py

# Security analysis
uv run bandit -r app/  # Individual tool - fast and reliable

# Testing transformations
curl -X POST http://localhost:5000/transform -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "transformation": "alternate_case"}'
```

## Dependencies and Environment
- **Python**: 3.13+ (specified in .python-version)
- **Package Manager**: uv (modern, fast Python package management)
- **Framework**: Flask 3.0+ with Gunicorn for production
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Testing**: pytest with comprehensive plugins (coverage, xdist, hypothesis, etc.)
- **Security**: Bandit for static analysis, Safety for dependency scanning
- **Linting**: ruff + black + mypy for code quality