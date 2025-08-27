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
- **Linting (Fix)**: `uv run ruff check --fix .` -- automatically fixes all auto-fixable issues
- **Linting (Verify)**: `uv run ruff check .` -- must pass with zero errors
- **Formatting (Fix)**: `uv run black .` -- fixes all formatting issues
- **Formatting (Verify)**: `uv run black --check .` -- must pass with zero changes needed
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

### GitHub Issue Management

When working on issues with Acceptance Criteria, follow this workflow to ensure comprehensive tracking and verification:

#### Before Starting Work
- **Review Acceptance Criteria**: Carefully read all Acceptance Criteria to understand requirements
- **Ask Questions**: If any criteria are unclear, ask for clarification in issue comments
- **Plan Implementation**: Break down work to address each Acceptance Criterion systematically
- **Estimate Effort**: Ensure your time estimate accounts for verifying all criteria

#### During Development
- **Reference Issue**: Include issue number in commit messages (e.g., `git commit -m "Fix transformation bug - addresses #123"`)
- **Update Progress**: Add comments to the issue about your progress and any implementation decisions
- **Check Off Completed Criteria**: As you complete each Acceptance Criterion, check it off in the issue:
  - Navigate to the issue on GitHub
  - Edit the issue description or add a comment
  - Check off completed items in the Acceptance Criteria checklist
- **Document Evidence**: For complex criteria, add comments with evidence of completion (test results, screenshots, etc.)
- **Test Each Criterion**: Create or run tests that specifically validate each Acceptance Criterion
- **Manual Verification**: Manually test functionality to ensure criteria are met in real usage

#### Before Submitting Pull Request
- **Final Verification**: Ensure all Acceptance Criteria are implemented and tested
- **Complete Checklist**: Verify all criteria are checked off in the issue
- **Cross-reference**: Ensure all acceptance criteria are addressed before considering work complete
- **Link to Issue**: Reference the issue in your pull request description
- **Evidence Summary**: Summarize how each major criterion was verified

#### Pull Request Review and Completion
- **Criteria Reference**: Reviewers should verify that all Acceptance Criteria are addressed
- **Testing Evidence**: Confirm that verification evidence is documented
- **Issue Closure**: Issues should only be closed when all criteria are completed and verified
- **Final Status Update**: Add a final comment summarizing completion and verification

This workflow ensures thorough requirement verification, maintains project quality, and provides clear tracking of development progress.

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

### Acceptance Criteria Verification
- **When working on issues with Acceptance Criteria, ALWAYS verify each criterion before considering work complete**:
  1. **Review Original Issue**: Confirm you understand all Acceptance Criteria
  2. **Test Each Criterion**: Create specific tests or perform manual verification for each criterion
  3. **Check Off Completed Items**: Mark each verified criterion as complete in the GitHub issue
  4. **Document Verification**: Add comments or evidence showing how each criterion was verified
  5. **Final Validation**: Ensure all criteria are checked off before submitting PR

### Manual Testing Requirements
- **ALWAYS** test the application after making changes:
  1. Run `uv run python -c "import app; print('✅ Import test passed')"`
  2. Start the development server: `FLASK_ENV=development uv run python app.py`
  3. Test health endpoint: `curl http://localhost:5000/health`
  4. Test at least one transformation: `curl -X POST http://localhost:5000/transform -H "Content-Type: application/json" -d '{"text": "test", "transformation": "alternate_case"}'`
  5. Stop the server with Ctrl+C

### Pre-commit Validation
- **ALWAYS run before committing** (MANDATORY):
  1. **Fix all linting issues**: `uv run ruff check --fix .`
  2. **Verify linting passes**: `uv run ruff check .` -- must pass cleanly
  3. **Fix all formatting issues**: `uv run black .`
  4. **Verify formatting passes**: `uv run black --check .` -- must pass cleanly
  5. `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable` -- should have minimal failures (with parallel execution)
  6. Manual application test as described above
  7. **Acceptance Criteria Verification** (when working on issues):
     - Verify all completed Acceptance Criteria are checked off in the GitHub issue
     - Ensure any evidence or verification steps are documented in issue comments
     - Confirm the pull request references the issue for proper tracking

## Mandatory Pre-Pull Request Requirements

**CRITICAL**: The following steps are **mandatory** for all pull request submissions. PRs that fail these requirements will be rejected.

### Code Quality Requirements (MANDATORY)
1. **All linting issues MUST be fixed** (not just identified):
   - Run: `uv run ruff check --fix .` to automatically fix issues
   - Verify: `uv run ruff check .` must pass with zero errors
2. **All formatting issues MUST be fixed** (not just identified):
   - Run: `uv run black .` to fix all formatting issues  
   - Verify: `uv run black --check .` must pass with zero changes needed
3. **Verification commands MUST pass** before PR submission
4. **This is a mandatory requirement**, not a suggestion

### Mandatory Workflow
The required workflow is: **fix → verify → commit**
- **Step 1**: Fix all issues using the fix commands
- **Step 2**: Verify fixes using the verification commands  
- **Step 3**: Only then proceed with commit and PR submission

**Note**: PRs with linting or formatting failures will be automatically rejected.

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

# Mandatory pre-commit workflow (fix → verify → commit)
# Step 1: Fix all issues
uv run ruff check --fix .       # Fix linting issues
uv run black .                  # Fix formatting issues

# Step 2: Verify all issues are resolved
uv run ruff check .             # Must pass with zero errors
uv run black --check .          # Must pass with zero changes needed

# Step 3: Run tests and commit (only after verification passes)
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

For detailed workflow on working with issues that have Acceptance Criteria, see the **GitHub Issue Management** section under "Working Effectively".