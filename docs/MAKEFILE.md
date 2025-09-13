# Makefile Documentation

## Overview

The `Makefile` provides a comprehensive set of commands for streamlined development workflows, CI/CD operations, Docker management, and deployment automation for the py-txt-trnsfrm project. This file serves as a unified interface to all project development tasks.

## Quick Start

```bash
# See all available commands
make help

# Initial setup (installs uv and all dependencies)
make setup

# Run tests
make test

# Check code quality
make check

# Run local CI pipeline
make ci
```

## Command Categories

### Core Workflow Commands

These commands handle basic project setup and dependency management:

#### `make setup`
- **Purpose**: Complete initial setup for new development environment
- **Actions**: 
  - Installs uv if not present
  - Installs all dependency groups (dev, test, security)
  - Verifies application can be imported
- **Requirements**: Internet connection
- **Example**: `make setup`

#### `make install`
- **Purpose**: Install all development dependencies
- **Actions**: Runs `uv sync --group dev --group test --group security`
- **When to use**: After pulling changes that modify dependencies
- **Example**: `make install`

#### `make sync`
- **Purpose**: Sync dependencies according to uv.lock
- **Actions**: Runs `uv sync` (respects lock file)
- **When to use**: Regular dependency synchronization
- **Example**: `make sync`

#### `make clean`
- **Purpose**: Remove generated files and caches
- **Actions**: 
  - Removes pytest cache, mypy cache, ruff cache
  - Cleans __pycache__ directories
  - Removes coverage reports
  - Cleans build artifacts
- **Example**: `make clean`

#### `make fresh`
- **Purpose**: Complete environment reset
- **Actions**: Runs `clean` then `setup`
- **When to use**: When environment is corrupted or for fresh start
- **Example**: `make fresh`

### Code Quality Commands

These commands ensure code quality and consistency:

#### `make format`
- **Purpose**: Automatically fix code formatting
- **Actions**:
  - Runs `ruff format .` for Python formatting
- **Example**: `make format`

#### `make lint`
- **Purpose**: Check code for linting issues
- **Actions**: Runs `ruff check .`
- **Exit codes**: Non-zero if issues found
- **Example**: `make lint`

#### `make fix`
- **Purpose**: Automatically fix auto-fixable linting issues
- **Actions**: 
  - Runs `ruff check --fix .`
- **Example**: `make fix`

#### `make check`
- **Purpose**: Run comprehensive quality checks
- **Actions**:
  - Runs lint checks with ruff
  - Runs type checking with mypy
- **Note**: Type checking currently shows expected issues
- **Example**: `make check`

#### `make types`
- **Purpose**: Run type checking only
- **Actions**: Runs `mypy .`
- **Note**: Currently shows 99 expected errors due to missing type annotations
- **Example**: `make types`

### Testing Commands

Comprehensive testing support with various test categories:

#### `make test`
- **Purpose**: Run standard test suite
- **Actions**: Excludes performance tests and slow property-based tests
- **Default markers**: `"not slow and not test_transform_property_based"`
- **Parallel execution**: Uses xdist for faster execution
- **Example**: `make test`
- **Custom markers**: `make test MARKERS=unit`

#### `make test-unit`
- **Purpose**: Run only unit tests
- **Actions**: Runs tests marked with `@pytest.mark.unit`
- **Example**: `make test-unit`

#### `make test-api`
- **Purpose**: Run only API endpoint tests
- **Actions**: Runs tests marked with `@pytest.mark.api`
- **Example**: `make test-api`

#### `make test-all`
- **Purpose**: Run complete test suite including slow tests
- **Actions**: Runs all tests without exclusions
- **Note**: Includes property-based tests that may fail
- **Example**: `make test-all`

#### `make test-fast`
- **Purpose**: Run critical smoke tests only
- **Actions**: Runs tests marked with `@pytest.mark.smoke`
- **Example**: `make test-fast`

#### `make coverage`
- **Purpose**: Generate HTML coverage report
- **Actions**: 
  - Runs tests with coverage collection
  - Generates HTML report in `reports/coverage/html/`
  - Shows coverage summary in terminal
- **Requirement**: Minimum 80% coverage enforced
- **Example**: `make coverage`

#### `make test-perf`
- **Purpose**: Run performance benchmarks
- **Actions**: Runs performance tests with pytest-benchmark
- **Requirement**: Application must be running
- **Note**: Disables xdist parallel execution for benchmarks
- **Example**: `make test-perf`

### Application Commands

Commands for running and testing the application:

#### `make run`
- **Purpose**: Start development server
- **Actions**: Starts Flask development server
- **Default**: Runs on 127.0.0.1:5000
- **Environment**: Sets FLASK_ENV=development
- **Example**: `make run PORT=8000`

#### `make run-prod`
- **Purpose**: Start production server with gunicorn
- **Actions**: Delegates to `./deploy.sh start`
- **Requirement**: SECRET_KEY environment variable must be set
- **Example**: `SECRET_KEY=your-key make run-prod`

#### `make health`
- **Purpose**: Check application health endpoint
- **Actions**: Calls GET /health endpoint
- **Requirement**: Application must be running
- **Example**: `make health`

#### `make demo`
- **Purpose**: Run demo text transformation
- **Actions**: Calls POST /transform with sample data
- **Requirement**: Application must be running
- **Example**: `make demo`

### Security Commands

Security analysis and vulnerability scanning:

#### `make security`
- **Purpose**: Run comprehensive security analysis
- **Actions**: Delegates to `./run_security_analysis.sh`
- **Includes**: 
  - Bandit static code analysis
  - Safety dependency vulnerability scanning
  - Report generation in multiple formats
- **Output**: Reports saved to `reports/security/`
- **Example**: `make security`

#### `make security-quick`
- **Purpose**: Run quick security scan
- **Actions**: Runs `bandit -r app/` only
- **Use case**: Fast security check during development
- **Example**: `make security-quick`

### Docker Commands

Container management and operations:

#### `make docker-build`
- **Purpose**: Build Docker image
- **Actions**: Runs `docker build -t py-txt-trnsfrm:latest .`
- **Requirement**: Docker must be installed and running
- **Customization**: `make docker-build DOCKER_TAG=v1.0`
- **Example**: `make docker-build`

#### `make docker-run`
- **Purpose**: Run containerized application
- **Actions**: Starts container with port mapping
- **Default**: Maps to port 5000
- **Example**: `make docker-run PORT=3000`

#### `make docker-stop`
- **Purpose**: Stop running containers
- **Actions**: Stops all containers based on py-txt-trnsfrm image
- **Example**: `make docker-stop`

#### `make docker-clean`
- **Purpose**: Clean up Docker resources
- **Actions**: 
  - Prunes stopped containers
  - Removes py-txt-trnsfrm images
- **Example**: `make docker-clean`

### CI/CD & Deployment

Continuous integration and deployment operations:

#### `make ci`
- **Purpose**: Run local CI pipeline that mirrors GitHub Actions
- **Actions**: 
  1. Code quality checks (`make check`)
  2. Test execution (`make test`)
  3. Security analysis (`make security-quick`)
  4. Coverage report generation (`make coverage`)
- **Use case**: Validate changes locally before pushing
- **Example**: `make ci`

#### `make deploy`
- **Purpose**: Deploy to Heroku
- **Actions**: Delegates to `./deploy.sh start`
- **Requirement**: SECRET_KEY environment variable must be set
- **Example**: `SECRET_KEY=your-key make deploy`

## Environment Variables

The Makefile supports several environment variables for customization and includes automatic integration with `.env` files for local development convenience.

### .env File Integration

The Makefile automatically loads environment variables from a `.env` file if it exists in the project root. This provides a convenient way to set default values for local development without modifying the Makefile or using command-line arguments repeatedly.

#### Setting up .env File

1. Copy the example file: `cp .env.example .env`
2. Edit `.env` with your preferred values
3. The Makefile will automatically load these values

#### Variable Precedence

Variables are resolved in the following order (highest to lowest priority):
1. **Command line arguments**: `make run PORT=8000`
2. **Environment variables**: `export PORT=8000; make run`
3. **.env file values**: Values set in your local `.env` file
4. **Makefile defaults**: Default values defined in the Makefile

#### Example .env Configuration

```bash
# Server configuration
PORT=8000
HOST=0.0.0.0

# Testing configuration
MARKERS=unit
VERBOSE=1
DEBUG=1
TIMEOUT=600

# Docker configuration
DOCKER_IMAGE=my-custom-image
DOCKER_TAG=dev
```

### Core Variables

- **`PORT`** (default: 5000): Server port for running applications
- **`HOST`** (default: 127.0.0.1): Server host binding
- **`MARKERS`** (default: "not slow and not test_transform_property_based"): Pytest markers for test filtering
- **`TIMEOUT`** (default: 300): Command timeout in seconds
- **`VERBOSE`** (default: 0): Enable verbose output (0/1)
- **`DEBUG`** (default: 0): Enable debug mode (0/1)

### Docker Variables

- **`DOCKER_IMAGE`** (default: py-txt-trnsfrm): Docker image name
- **`DOCKER_TAG`** (default: latest): Docker image tag

### Examples

```bash
# Run tests with specific markers
make test MARKERS=unit

# Start server on different port
make run PORT=8000

# Run Docker container on port 3000
make docker-run PORT=3000

# Enable verbose output
make test VERBOSE=1
```

## Advanced Features

### Colored Output

The Makefile provides colored progress indicators:
- 🔵 Blue: Progress messages
- 🟢 Green: Success messages  
- 🟡 Yellow: Warning messages
- 🔴 Red: Error messages

### Progress Indicators

Each command provides clear feedback:
```
▶ Running ruff linting...
✅ Linting complete!
```

### Error Handling

- Commands exit with appropriate exit codes
- Clear error messages for common issues
- Automatic dependency checking

## Troubleshooting

### Common Issues

#### UV Not Found
**Error**: `UV is not installed. Run 'make setup' to install it.`
**Solution**: Run `make setup` to install uv automatically

#### Docker Commands Fail
**Error**: Docker-related commands fail
**Solution**: 
1. Ensure Docker is installed: `docker --version`
2. Ensure Docker daemon is running: `docker ps`
3. Check Docker permissions

#### Port Already in Use
**Error**: Port conflicts when running servers
**Solution**: 
1. Use different port: `make run PORT=8001`
2. Stop conflicting processes: `lsof -ti:5000 | xargs kill`

#### Security Scan Timeout
**Error**: Safety scan times out
**Solution**: 
- Expected behavior for safety scans
- Check `reports/security/` for available results
- Use `make security-quick` for faster scans

#### Test Failures
**Error**: Expected test failures
**Known Issues**:
- Property-based test fails (expected)
- Security test fails (by design - tests HTML sanitization)
- Docker compose test fails if docker-compose not installed

### Performance Considerations

#### Parallel Execution
- Tests use xdist for parallel execution by default
- Disable with `-n 0` for benchmark tests
- Coverage reports may be slower with parallel execution

#### Cache Management
- Regular `make clean` prevents cache bloat
- UV caches dependencies for faster installs
- pytest caches for faster test discovery

## Integration with Existing Tools

### CI/CD Pipeline
The Makefile mirrors the GitHub Actions workflow:
- Same commands used in CI and locally
- Consistent behavior across environments
- Local validation before pushing

### Existing Scripts
The Makefile integrates with existing scripts:
- `./deploy.sh` for deployment operations
- `./run_security_analysis.sh` for security scans
- No duplication of deployment logic

### UV Integration
All commands use UV for:
- Dependency management
- Python environment handling
- Consistent tool versions

## Future Extensibility

### Adding New Commands

The Makefile includes a structured approach for adding new commands. Use the following template and best practices:

#### Command Template

```makefile
new-command: uv-check ## Description of new command
	$(call progress,Starting new command...)
	# Add your command implementation here
	$(call success,New command complete!)
```

#### Best Practices for New Commands

When adding new commands to the Makefile, follow these guidelines:

1. **Add proper dependencies**: Most commands should depend on `uv-check` to ensure UV is available
2. **Use progress indicators**: Provide user feedback with `$(call progress,...)` and `$(call success,...)`
3. **Include meaningful help text**: Add descriptive help text after `##` for the help system
4. **Follow naming conventions**: Use lowercase with hyphens (kebab-case) for command names
5. **Add to help sections**: If creating a new category, update the help target to include it
6. **Handle errors gracefully**: Use proper error handling and meaningful error messages
7. **Use environment variables**: Make commands configurable through environment variables when appropriate

#### Command Categories

Organize new commands into these existing categories:
- **Core Workflow**: Setup, installation, dependency management
- **Code Quality**: Formatting, linting, type checking
- **Testing**: Various test execution modes and coverage
- **Application**: Running, health checks, demonstrations
- **Security**: Security analysis and vulnerability scanning
- **Docker**: Container operations and management
- **CI/CD**: Continuous integration and deployment

#### Examples of Well-Formed Commands

```makefile
# Simple command with basic structure
docs-build: uv-check ## Build documentation with Sphinx
	$(call progress,Building documentation...)
	$(UV) run sphinx-build -b html docs/ docs/_build/html/
	$(call success,Documentation built in docs/_build/html/)

# Command with environment variable support
serve-docs: uv-check ## Serve documentation locally
	$(call progress,Starting documentation server on port $(DOCS_PORT)...)
	$(UV) run python -m http.server $(DOCS_PORT) --directory docs/_build/html/

# Command with error handling
deploy-staging: uv-check ## Deploy to staging environment
	$(call progress,Deploying to staging...)
	@if [ -z "$$STAGING_URL" ]; then \
		$(call error,STAGING_URL environment variable is required); \
		exit 1; \
	fi
	# Deployment commands here
	$(call success,Deployed to staging: $$STAGING_URL)
```

### Best Practices for Extensions

1. **Use dependency checks**: Add `uv-check` dependency
2. **Provide feedback**: Use progress indicators
3. **Handle errors**: Provide meaningful error messages
4. **Document thoroughly**: Add comprehensive help text
5. **Follow conventions**: Use established naming patterns

### Planned Enhancements

Based on the issue requirements, future additions may include:
- `make docs` for documentation automation
- Additional Docker operations
- Enhanced CI/CD integrations
- More granular test categories

## Related Documentation

- [CI/CD Pipeline Documentation](CI_CD_PIPELINE.md)
- [UV Troubleshooting Guide](UV_TROUBLESHOOTING.md)
- [Main README](../README.md)

## Support

For issues or questions:
1. Check this documentation
2. Review existing GitHub issues
3. Create new issue with `makefile` label
