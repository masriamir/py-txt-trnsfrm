# py-txt-trnsfrm Development Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Quick Reference Card

**Every PR Must Have:**
- ✅ Zero ruff/black errors (`make fix`)
- ✅ All tests passing (`make test`)
- ✅ Closing keywords (Closes #XX)
- ✅ All issue metadata copied
- ✅ Safety URLs preserved in `uv.lock`

**Never Do:**
- ❌ Change pkgs.safetycli.com URLs
- ❌ Use basic logging setup
- ❌ Manually fix formatting
- ❌ Commit without running tests

## 1. Sprint Management and Issue Creation

When creating or managing issues for sprint planning:

#### Issue Creation Standards
- **Title Format**: "Action verb + description - context" (e.g., "Fix all ruff linting errors - code quality foundation")
- **Required Metadata**:
  - **Project**: Always assign to "Retro Text Transformer" project
  - **Epic**: Categorize appropriately (Code Quality Foundation, Logging Infrastructure, Developer Productivity, etc.)
  - **Story Points**: Use Fibonacci sequence (1, 2, 3, 5, 8)
  - **Time Estimate**: Provide realistic hours estimate
  - **Risk Level**: Low/Medium/High
  - **Priority Labels**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low), P4 (Enhancement)
  - **Version Tags**: v1.0, v1.1, etc.
  - **Sprint Assignment**: Maximum 8 points per one-week sprint

#### Sprint Capacity
- **Sprint Duration**: 1 week
- **Max Capacity**: 8 story points per sprint
- **Velocity Tracking**: Monitor completed points vs planned

#### Dependencies
- **Always document blocking relationships** between issues
- **Use checkboxes** for prerequisites and blocked work
- **Update issue status** when dependencies are resolved

## 2. Technology Stack and Dependencies

**py-txt-trnsfrm** is a Flask web application that provides creative text transformations inspired by early 90s internet culture. This is a Python 3.13+ project using modern tools and practices.
### Core Stack
- **Python**: 3.13+ (specified in .python-version)
- **Backend Framework**: Flask `3.1.1+` with Gunicorn for production deployment
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
- **Centralized Configuration**: Environment variable handling in `app/env_config.py` for consistent configuration across all entry points

### Available Text Transformations
- **Case Transformations**: alternate_case, spongebob_case
- **Visual Effects**: rainbow_html, wave_text, zalgo_text
- **Linguistic**: leet_speak, shizzle_speak, stutter
- **Encoding**: morse_code, binary, rot13
- **Directional**: backwards, upside_down

## 3. Development with Makefile

The project includes a comprehensive `Makefile` for streamlined workflows:

#### Quick Commands
- **Initial setup**: `make setup` (installs uv and all dependencies)
- **Run tests**: `make test` (standard suite) or `make test-unit`, `make test-api`, etc.
- **Code quality**: `make fix` (auto-fix issues), `make check` (verify quality)
- **Run server**: `make run` (development) or `make run-prod` (production)
- **Local CI**: `make ci` (mirrors GitHub Actions locally)
- **Docker**: `make docker-build`, `make docker-run`, `make docker-stop`

#### Configuration via .env
- Copy `.env.example` to `.env` for local configuration
- Variables: `PORT`, `HOST`, `MARKERS`, `DOCKER_IMAGE`, etc.
- Precedence: Command line > Environment > `.env` file > `Makefile` defaults
- Example: `make run PORT=8000` or set `PORT=8000` in `.env`

See `docs/MAKEFILE.md` for complete documentation.

## 4. Code Formatting Standards (MANDATORY)

**CRITICAL**: These formatting standards are enforced by CI and must be followed:

1. **Line Length**: Maximum 88 characters (`black`/`ruff` standard)
2. **Multi-line Formatting**: When breaking long lines:
   ```python
   # CORRECT - Parentheses on separate lines for multi-line
   assert (
       some_long_condition_here
   ), "Error message here"
   
   # INCORRECT - Don't put opening parenthesis on same line as closing
   assert (some_long_condition_here), "Error message"
   ```
3. **Import Organization**: Let `ruff` handle import sorting - never manually reorder
4. **String Quotes**: Use double quotes consistently (enforced by `black`)
5. **Trailing Commas**: Add trailing commas in multi-line structures

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

### Test Creation and Maintenance Guidelines

**MANDATORY**: All code changes must include proper test coverage with appropriate pytest markers. This section defines requirements and best practices for creating, maintaining, and categorizing tests.

#### Test Creation Requirements (MANDATORY)

**All new functionality MUST include tests:**
- **New functions/methods**: Unit tests with `@pytest.mark.unit` (mandatory)
- **New Flask endpoints**: API tests with `@pytest.mark.api` (mandatory)
- **New utilities/transformations**: Unit tests + integration tests for complex workflows
- **Security-related changes**: Security tests with `@pytest.mark.security`
- **Performance-critical code**: Performance tests with `@pytest.mark.load` or `@pytest.mark.concurrent`

**Coverage Requirements:**
- **Minimum 80%** overall coverage (enforced by pytest configuration)
- **New code must maintain or improve** coverage percentage
- **All new functions must have dedicated unit tests**
- **All new endpoints must have dedicated API tests**

#### Test Creation Guidelines

**When to Create Tests:**
1. **Before implementation** (TDD approach encouraged) - Plan tests alongside feature design
2. **During implementation** - Create tests as you build functionality
3. **For bug fixes** - Create regression tests to prevent issue recurrence
4. **For refactoring** - Ensure existing behavior is preserved

**Pytest Marker Assignment (MANDATORY):**
- `@pytest.mark.unit` - Isolated unit tests for individual functions/methods (mandatory for all functions)
- `@pytest.mark.integration` - Cross-component tests (required for complex workflows spanning multiple modules)  
- `@pytest.mark.api` - Flask endpoint tests (mandatory for all routes in `app/main/`)
- `@pytest.mark.smoke` - Critical functionality tests (for core features affecting user experience)
- `@pytest.mark.slow` - Tests taking >5 seconds (property-based, large data processing)
- `@pytest.mark.security` - Security validation tests (authentication, input sanitization, vulnerability checks)
- `@pytest.mark.concurrent` - Concurrency/threading tests (for parallel processing features)
- `@pytest.mark.load` - Performance/load tests (for performance optimization work)

**Test Data Management:**
- **Use centralized test data** from `tests/data/test_data.py` for consistency
- **Use faker** for dynamic test data generation: `from faker import Faker`
- **Use pytest-datadir** for file-based test data: `@pytest.mark.datadir`
- **Edge cases**: Include tests for empty strings, special characters, unicode, large inputs
- **Sample data**: Leverage existing `sample_texts`, `expected_results`, `edge_cases` dictionaries

**Test Structure Requirements:**
```python
import pytest
from faker import Faker
from app.utils.some_module import SomeClass

@pytest.mark.unit
class TestSomeClass:
    """Test suite for SomeClass functionality."""
    
    @pytest.fixture
    def instance(self):
        """Fixture providing test instance."""
        return SomeClass()
    
    @pytest.mark.unit
    def test_basic_functionality(self, instance):
        """Test basic functionality with clear assertion."""
        result = instance.some_method("test input")
        assert result == "expected output"
        assert isinstance(result, str)
    
    @pytest.mark.unit  
    def test_edge_cases(self, instance):
        """Test edge cases comprehensively."""
        # Test with edge_cases from test_data
        for case_name, case_input in edge_cases.items():
            result = instance.some_method(case_input)
            assert isinstance(result, str)  # Should handle all edge cases
```

#### Test Maintenance Guidelines

**Updating Existing Tests:**
- **When modifying functionality**: Update corresponding tests to match new behavior
- **When fixing bugs**: Add regression tests before implementing the fix
- **When refactoring**: Ensure tests still validate the same behavior contracts
- **When adding features**: Extend existing test classes rather than creating duplicate tests

**Removing Tests:**
- **Remove tests only when** the associated functionality is completely removed
- **Update test markers** if test categorization changes (e.g., unit -> integration)
- **Consolidate redundant tests** to maintain test suite efficiency

**Performance Considerations:**
- **Use `--benchmark-disable`** for regular test runs to maintain xdist parallel execution
- **Run performance tests separately** with `-n 0 --benchmark-only` when measuring performance
- **Keep test execution time reasonable** - mark slow tests with `@pytest.mark.slow`

#### Coverage Verification and Quality Assurance

**Coverage Verification Steps:**
1. **Before making changes**: Run `uv run pytest --cov=app --cov-report=term-missing` to establish baseline
2. **After adding tests**: Verify coverage improvements with `uv run pytest --cov=app --cov-report=html:reports/coverage/html`
3. **Check coverage reports**: Review `reports/coverage/html/index.html` for detailed coverage analysis
4. **Ensure 80% minimum**: Tests will fail if coverage drops below 80% threshold

**Test Quality Assurance:**
- **Clear test names**: Use descriptive names that explain what is being tested
- **Comprehensive assertions**: Test both positive and negative cases
- **Test isolation**: Each test should be independent and not rely on other tests
- **Mock external dependencies**: Use `pytest-mock` for isolating units under test
- **Document complex tests**: Add docstrings explaining test rationale for complex scenarios

#### Integration with Development Workflow

**Before Starting Work:**
- **Review existing tests** related to the area you're modifying
- **Plan test requirements** alongside feature requirements in Acceptance Criteria
- **Identify test types needed**: Unit, integration, API, security, performance

**During Development:**
- **Create tests incrementally** as you implement functionality
- **Run relevant test subset** frequently: `uv run pytest -m unit` or `uv run pytest tests/test_specific_module.py`
- **Verify test markers** are applied correctly with `uv run pytest --collect-only`

**Before Committing:**
- **Run full test suite**: `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable`
- **Verify coverage**: Ensure coverage requirements are met
- **Check test categorization**: Confirm proper pytest markers are applied
- **Validate test quality**: Ensure tests have clear assertions and proper structure

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

### Pull Request Management

When opening a pull request to address a specific issue, proper metadata inheritance ensures consistent project tracking and maintains sprint management accuracy for the Retro Text Transformer project.

#### Metadata Inheritance Process
When creating a PR to address an issue, **all metadata from the originating issue must be copied to the PR**:

##### Step-by-Step Metadata Inheritance Instructions
1. **Copy Labels**: Inherit all labels from the originating issue
   - **Priority labels** (P0, P1, P2)
   - **Story point labels** (1, 2, 3, 5, 8, etc.)
   - **Version tags** (v1.0.0, etc.)
   - **Type labels** (bug, enhancement, documentation, etc.)
   - **Component labels** (frontend, backend, testing, etc.)

2. **Copy Milestones**: Assign the same milestone from the originating issue to maintain sprint tracking

3. **Copy Project Assignments**: Ensure the PR is assigned to the same project board(s) as the issue

4. **Copy Custom Field Values**: Inherit any custom field values from the project board:
   - Epic assignments
   - Sprint assignments  
   - Risk level indicators
   - Time estimates
   - Any other custom fields used in project management

##### Metadata Inheritance Workflow
- **Before Creating PR**: Review the originating issue and note all metadata
- **During PR Creation**: Apply all relevant metadata from the issue to the PR
- **Verification**: Double-check that all metadata has been properly inherited
- **Documentation**: Reference the issue number in the PR description

This ensures continuous tracking from issue creation through PR completion and maintains accuracy in sprint management, story point tracking, and milestone progress for the Retro Text Transformer project.

#### Closing Issues with Pull Requests (MANDATORY)

**All pull requests MUST use GitHub's closing keywords to automatically close their associated issues.** This ensures proper issue tracking and prevents issues from remaining open after work completion.

##### Required Closing Keywords
Use one of these GitHub closing keywords in your PR description or commit messages:
- `Closes #123` - Standard closing syntax
- `Fixes #456` - For bug fixes 
- `Resolves #789` - For general issue resolution
- `Closes: #123` - Alternative syntax with colon

##### Examples for Single Issues
```
# In PR description:
This PR adds the new text transformation feature.

Closes #45

# In commit message:
git commit -m "Add zalgo text transformation - Fixes #67"
```

##### Examples for Multiple Issues
```
# In PR description:
This PR refactors the transformation engine and fixes several bugs.

Closes #23
Fixes #34  
Resolves #45

# Alternative syntax:
Closes #23, #34, #45
```

##### Placement Requirements
- **PR Description**: Include closing keywords in the PR description (recommended)
- **Commit Messages**: Alternative placement in commit messages
- **Issue References**: Always reference specific issue numbers with `#` prefix
- **Verification**: Ensure the referenced issues exist and are related to the PR content

**Note**: This is a mandatory requirement for all PRs. PRs without proper issue closing keywords will be rejected during review.

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

## 5. Centralized Environment Configuration

The application uses a centralized configuration system located in `app/env_config.py` that provides a single source of truth for environment variable handling across all entry points (`app.py`, `wsgi.py`, `app/__init__.py`).

#### Key Functions
- `get_logging_config()`: Returns validated logging configuration with `log_level` and `debug_mode`
- `get_flask_env()`: Gets Flask environment with development default
- `get_flask_env_for_wsgi()`: Gets Flask environment with production default for WSGI contexts
- `is_heroku_environment()`: Detects Heroku deployment via DYNO environment variable
- `get_port()`: Gets port number with integer conversion
- `get_host_for_environment()`: Returns appropriate host binding based on environment

#### Log Level Processing
- **ALWAYS use `.upper()`** on log level environment variables for consistency
- Compare against uppercase values: `log_level == "DEBUG"`
- Pass uppercase values to setup functions: `setup_logging(debug=debug_mode, log_level=log_level)`

#### Usage Examples
```python
from app.env_config import get_logging_config, is_heroku_environment

# Get logging configuration
config = get_logging_config()
setup_logging(debug=config.debug_mode, log_level=config.log_level)

# Check deployment environment
if is_heroku_environment():
    # Heroku-specific configuration
    pass
```

#### Benefits
- **Single source of truth**: All environment variable logic centralized
- **Consistent behavior**: Same configuration across all entry points
- **Validation**: Automatic validation and fallbacks for invalid values
- **Type safety**: Structured configuration with proper typing

## 6. Common Mistakes to Avoid

1. **URL Modifications in uv.lock**
   - ❌ NEVER change `pkgs.safetycli.com` URLs to `pypi.org` or `files.pythonhosted.org`
   - ✅ Always preserve safety registry URLs when running `uv sync`

2. **Logging Configuration**
   - ❌ Don't use basic logging setup: `logging.basicConfig(...)`
   - ✅ Use centralized logging: `from app.logging_config import get_logger, setup_logging`

3. **Code Formatting**
   - ❌ Don't manually fix formatting issues
   - ✅ Always use `uv run black .` and `uv run ruff check --fix .`

4. **Test Execution**
   - ❌ Don't use `-n 0` for regular tests (disables parallel execution)
   - ✅ Only use `-n 0` with `--benchmark-only` for performance tests

5. **Environment Variables**
   - ❌ Don't use `.lower()` then `.upper()` on the same variable
   - ✅ Call `.upper()` once when retrieving: `os.environ.get("LOG_LEVEL", "info").upper()`

## 7. Pull Request Standards

When creating pull requests:

1. **Title**: Clear, action-oriented description
2. **Description MUST include**:
   - Summary of changes
   - Testing performed (with specific commands)
   - Verification steps
   - Related issue references with closing keywords
3. **Metadata**: Copy ALL labels, milestones, and project assignments from related issues
4. **Closing Keywords**: ALWAYS use `Closes #XX`, `Fixes #XX`, or `Resolves #XX`

Example PR description:
```
This PR implements centralized logging configuration for `app.py` and fixes `wsgi.py` log level handling.

## Changes
- Updated `app.py` to use centralized logging from `app.logging_config`
- Fixed `wsgi.py` to properly handle `LOG_LEVEL` environment variable
- Optimized log level processing to avoid redundant string operations

## Testing
- ✅ `uv run ruff check .` - passes cleanly
- ✅ `uv run black --check .` - no formatting issues
- ✅ `uv run pytest` - all tests pass
- ✅ Manual testing with `FLASK_ENV=development uv run python app.py`

## Verification
- Confirmed logging outputs at correct levels
- Verified `LOG_LEVEL` environment variable is respected
- Tested both development and production configurations

Closes #11
```

## 8. Performance Expectations and Timeouts

**Set appropriate timeouts for long-running operations:**
- `uv sync`: 3-4 minutes → Set timeout to 10+ minutes
- `./run_security_analysis.sh`: 5+ minutes → Set timeout to 10+ minutes  
- `./deploy.sh test`: 2+ minutes → Set timeout to 5+ minutes
- `make ci`: 2-3 minutes → Set timeout to 5+ minutes

**When running commands programmatically:**
```python
# Set appropriate timeout
result = subprocess.run(["uv", "sync"], timeout=600)  # 10 minutes
```

## 9. Pre-Commit Checklist (MANDATORY)

- [ ] Ran `make fix` to fix all formatting/linting issues
- [ ] Ran `make test` and all tests pass
- [ ] Updated tests for any new functionality
- [ ] Verified uv.lock URLs still use pkgs.safetycli.com
- [ ] Checked PR includes closing keywords
- [ ] Copied all metadata from related issues

## 10. Copy-Paste Commands

```bash
# Before any commit
make fix && make test && make check

# Verify safety URLs
grep -c "pkgs.safetycli.com" uv.lock

# Check formatting without fixing
uv run black --check . && uv run ruff check .
```

## Validation
### Acceptance Criteria Verification
- **When working on issues with Acceptance Criteria, ALWAYS verify each criterion before considering work complete**:
  1. **Review Original Issue**: Confirm you understand all Acceptance Criteria
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
  5. **Test Creation Verification** (MANDATORY for code changes):
     - Confirm new/updated tests exist for all functionality changes
     - Verify proper pytest markers are applied: `uv run pytest --collect-only | grep -E "@pytest.mark.(unit|api|integration)"`
     - Validate test coverage meets requirements: `uv run pytest --cov=app --cov-report=term-missing`
     - Ensure coverage is maintained or improved (80% minimum threshold)
  6. **Run full test suite**: `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable` -- should have minimal failures (with parallel execution)
  7. **Manual application test** as described above
  8. **Acceptance Criteria Verification** (when working on issues):
     - Verify all completed Acceptance Criteria are checked off in the GitHub issue
     - Ensure any evidence or verification steps are documented in issue comments
     - Confirm the pull request references the issue for proper tracking
     - Validate that tests exist for each Acceptance Criterion
  9. **Metadata Inheritance Verification** (when working on issues):
     - Verify the PR has inherited all relevant metadata from the originating issue
     - Confirm labels (priority, story points, version tags) are copied to the PR
     - Ensure milestone and project assignments match the originating issue
     - Validate any custom field values from the project board are inherited
  10. **Issue Closing Keywords Verification** (MANDATORY for all PRs):
     - Ensure PR description includes proper GitHub closing keywords (Closes #123, Fixes #456, Resolves #789)
     - Verify all referenced issue numbers exist and are related to the PR content
     - Confirm closing keywords use correct syntax with `#` prefix for issue numbers
     - Validate that multiple issues use proper syntax (separate lines or comma-separated)

## Mandatory Pre-Pull Request Requirements

**CRITICAL**: The following steps are **mandatory** for all pull request submissions. PRs that fail these requirements will be rejected.

### Code Quality Requirements (MANDATORY)
1. **All linting issues MUST be fixed** (not just identified):
   - Run: `uv run ruff check --fix .` to automatically fix issues
   - Verify: `uv run ruff check .` must pass with zero errors
2. **All formatting issues MUST be fixed** (not just identified):
   - Run: `uv run black .` to fix all formatting issues  
   - Verify: `uv run black --check .` must pass with zero changes needed
3. **Test Requirements MUST be met** (MANDATORY):
   - All new functionality must have corresponding tests with proper pytest markers
   - Coverage must meet or exceed 80% threshold: `uv run pytest --cov=app --cov-fail-under=80`
   - All tests must pass: `uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable`
   - New functions must have unit tests with `@pytest.mark.unit`
   - New endpoints must have API tests with `@pytest.mark.api`
   - Complex workflows must have integration tests with `@pytest.mark.integration`
4. **Verification commands MUST pass** before PR submission
5. **Issue closing keywords MUST be included** in PR description (MANDATORY):
   - Use proper GitHub closing syntax: `Closes #123`, `Fixes #456`, `Resolves #789`
   - Reference all related issues that the PR addresses
   - Ensure issue numbers exist and are related to the PR content
6. **This is a mandatory requirement**, not a suggestion

### Test Creation Requirements (MANDATORY)
- **Unit Tests**: Every new function/method must have dedicated unit tests
- **API Tests**: Every new Flask endpoint must have API tests  
- **Integration Tests**: Multi-component features must have integration tests
- **Security Tests**: Authentication/authorization features must have security tests
- **Performance Tests**: Performance-critical code must have performance tests
- **Regression Tests**: Bug fixes must include tests preventing regression
- **Proper Markers**: All tests must use appropriate pytest markers for categorization

### Mandatory Workflow
The required workflow is: **implement → test → fix → verify → close → commit**
- **Step 1**: Implement functionality with corresponding tests
- **Step 2**: Apply proper pytest markers and ensure coverage
- **Step 3**: Fix all linting and formatting issues using the fix commands
- **Step 4**: Verify all fixes and test requirements using the verification commands  
- **Step 5**: Add proper issue closing keywords to PR description (Closes #123, Fixes #456, Resolves #789)
- **Step 6**: Only then proceed with commit and PR submission

**Note**: PRs with linting, formatting, or test coverage failures will be automatically rejected.

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


## Common Commands Reference

```bash
# Complete setup from fresh clone
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --group dev --group test --group security  # 3-4 minutes

# Mandatory pre-commit workflow (implement → test → fix → verify → commit)
# Step 1: Implement functionality with tests
# Step 2: Apply proper pytest markers and ensure coverage
uv run pytest --cov=app --cov-report=term-missing    # Check coverage
uv run pytest --collect-only | grep "@pytest.mark"  # Verify markers

# Step 3: Fix all issues
uv run ruff check --fix .       # Fix linting issues
uv run black .                  # Fix formatting issues

# Step 4: Verify all issues are resolved
uv run ruff check .             # Must pass with zero errors
uv run black --check .          # Must pass with zero changes needed
uv run pytest --cov=app --cov-fail-under=80  # Must meet coverage threshold

# Step 5: Run tests and commit (only after verification passes)
uv run pytest --ignore=tests/performance -k "not test_transform_property_based" --benchmark-disable
FLASK_ENV=development uv run python app.py

# Test execution by category
uv run pytest -m unit --benchmark-disable           # Unit tests only
uv run pytest -m integration --benchmark-disable    # Integration tests
uv run pytest -m api --benchmark-disable           # API endpoint tests
uv run pytest -m smoke --benchmark-disable         # Critical functionality tests

# Test coverage and quality
uv run pytest --cov=app --cov-report=html:reports/coverage/html  # HTML coverage report
uv run pytest --cov=app --cov-report=term-missing               # Terminal coverage report
uv run pytest tests/specific_module.py -v                       # Run specific test module

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
- **Update test guidelines** when adding new pytest markers, test types, or coverage requirements
- **Maintain test command accuracy** when modifying test execution workflows or adding new test categories

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