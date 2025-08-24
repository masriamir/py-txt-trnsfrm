# py-txt-trnsfrm Development Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

**py-txt-trnsfrm** is a Flask web application that provides creative text transformations inspired by early 90s internet culture. This is a Python 3.13+ project using modern tools and practices.

### Technology Stack and Dependencies
- **Python**: 3.13+ (specified in .python-version)
- **Backend Framework**: Flask 3.0+ with Gunicorn for production deployment
- **Frontend**: Bootstrap 5 with vanilla JavaScript, Jinja2 templates for server-side rendering
- **Package Management**: uv (modern, fast Python package management replacement for pip/pipenv)
- **Security**: Bandit for static analysis, Safety for dependency vulnerability scanning
- **Code Quality**: ruff (linting) + black (formatting) + mypy (type checking)
- **Testing**: pytest with comprehensive plugins (coverage, xdist for parallel execution, hypothesis for property-based testing, benchmark for performance testing)
- **Deployment**: Docker-ready with Heroku deployment support, Nginx configuration available

### Application Architecture
- **Main Flask App**: Located in `app/` package with blueprint-based routing in `app/main/`
- **Text Transformations**: Utility functions in `app/utils/` for various text effects
- **UI Components**: Five pastel color themes with accessibility-first design
- **API Endpoints**: RESTful API for text transformations with JSON responses
- **Health Monitoring**: Built-in health check endpoint for deployment monitoring

## Working Effectively

### Bootstrap and Dependencies
- **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH"`
- **Install all dependencies**: `uv sync --group dev --group test --group security` -- takes 3-4 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
- **Verify installation**: `uv run python -c "import app; print('✅ Application imports successfully')"`

### Dependency Management with Safety Registry
- **Adding new dependencies**: When adding dependencies to `pyproject.toml`, always sync with the safety registry to preserve URLs
- **Correct sync command**: `uv sync --default-index https://pkgs.safetycli.com/repository/akm-circuits-llc/pypi/simple/ --group dev --group test --group security`
- **CRITICAL**: The `uv.lock` file URLs must always use `pkgs.safetycli.com/` - never change them to `pypi.org` or `files.pythonhosted.org`
- **When uv.lock changes**: Only commit changes that add the specific new dependency and its direct dependencies - all other entries should preserve safety URLs
- **Verification**: After adding dependencies, confirm safety URLs with `grep "pkgs.safetycli.com" uv.lock | head -3`

### Code Quality Tools
- **Linting**: `uv run ruff check .` -- takes <1 second. Passes cleanly.
- **Formatting**: `uv run black --check .` -- takes <1 second. Currently fails on 7 files, run `uv run black .` to fix.
- **Type checking**: `uv run mypy .` -- takes 7-8 seconds. Currently has 99 errors, mostly missing type annotations.

### Testing
- **Run all tests (excluding performance)**: `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable` -- takes 1-2 seconds with parallel execution. Currently 47 passed, 1 failed (expected).
- **Run specific test categories (with parallel execution)**: 
  - `uv run pytest -m unit --benchmark-disable` -- Unit tests only
  - `uv run pytest -m integration --benchmark-disable` -- Integration tests
  - `uv run pytest -m api --benchmark-disable` -- API endpoint tests
  - `uv run pytest -m smoke --benchmark-disable` -- Critical functionality tests
- **Run with coverage**: Tests include coverage reporting to `reports/coverage/`
- **Performance tests**: `BASE_URL=http://localhost:5000 uv run pytest tests/performance/test_api_performance.py --benchmark-only -n 0` (requires running Flask app first)
- **NOTE**: Use `--benchmark-disable` for regular tests to maintain xdist parallel execution. Use `-n 0` flag **only** when running benchmark tests with `--benchmark-only` to disable xdist parallel execution which conflicts with pytest-benchmark.

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
  3. `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable` -- should have minimal failures (with parallel execution)
  4. Manual application test as described above

## Known Issues and Limitations

### Test Suite Issues
- **Performance tests**: Require `concurrent` and `load` markers in pytest.ini (already added)
- **Benchmark vs parallel execution**: pytest-benchmark conflicts with xdist parallel execution, so use `--benchmark-disable` for regular tests and `-n 0` only when running `--benchmark-only` performance tests
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
- **uv.lock**: Dependency lock file (always commit changes, URLs are prefixed with `pkgs.safetycli.com/` which is correct and should NOT be changed to `pypi.org` or `files.pythonhosted.org`)
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
uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable
FLASK_ENV=development uv run python app.py

# Security analysis
uv run bandit -r app/  # Individual tool - fast and reliable

# Testing transformations
curl -X POST http://localhost:5000/transform -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "transformation": "alternate_case"}'
```

## Maintaining These Instructions

### Keeping Instructions Current
- **ALWAYS update** `.github/copilot-instructions.md` when implementing new features, tools, or changing development workflows
- **Cross-reference changes** with existing information in this file to ensure consistency
- **Add new commands** with validated timings and proper `uv run` prefixes
- **Document new dependencies** in the Technology Stack and Dependencies section
- **Update known issues** when fixing problems or discovering new ones
- **Include any new test categories** or build processes

### Contributing Guidelines for Issues
When creating new issues, follow the structured format established in issues #7 and #8:
- **Use descriptive titles** following pattern: "Action description - brief context"
- **Include project metadata**: Epic, Story Points, Time Estimate, Risk Level
- **Provide clear description** and user story
- **Add technical analysis** section when relevant
- **Define acceptance criteria** as checkboxes
- **Document dependencies and blocking relationships**
- **Use appropriate labels**: P0/P1/P2 priority, story points (1-8), version tags
- **Assign to appropriate milestone** with sprint context