# GitHub Actions CI/CD Pipeline

## Overview
Production-ready GitHub Actions CI/CD pipeline for py-txt-trnsfrm Flask application with uv dependency management, optimized for single production environment deployment.

## Workflows

### 🚀 ci.yml - Primary CI Pipeline
- **Triggers:** Push to main/develop, PRs, manual dispatch
- **Jobs:** Code Quality → Testing Matrix + Security Analysis → Aggregate Results
- **Features:** Fast failure, parallel execution, uv caching, comprehensive testing

### 🔒 security-nightly.yml - Nightly Security Scan
- **Triggers:** Nightly at 2:00 AM UTC, manual dispatch
- **Features:** Deep security analysis, slow tests, automatic issue creation

### 📦 release.yml - Release Pipeline
- **Triggers:** Version tags, releases, manual dispatch
- **Features:** Version validation, full test suite, git-based Heroku deployment to production

## Key Features

### Optimization
- uv dependency caching with lock file hashing
- Parallel job execution with proper dependencies
- Path-based filtering for efficiency
- Uses latest GitHub Actions (checkout@v5, setup-uv@v6)

### Security
- Zero tolerance for critical security issues
- Comprehensive scanning (Bandit, Safety)
- Automatic issue creation on findings
- Nightly deep security analysis

### Testing
- Matrix strategy by test type (unit, integration, api, smoke)
- Excludes slow/security tests from main CI
- Individual coverage reports with Codecov integration
- Standalone performance test file (`tests/performance/test_api_performance.py`)

### Deployment
- Git-based Heroku deployment to production environment
- Comprehensive pre-deployment validation
- Single production environment focus
- Automated changelog generation and GitHub releases

## Environment Variables
- `CODECOV_TOKEN` - Required for coverage uploads
- `HEROKU_API_KEY`, `HEROKU_EMAIL` - Required for production deployment

## Performance Testing
A standalone performance test file is available at `tests/performance/test_api_performance.py` that can be used independently:

```bash
# Run benchmark tests
pytest tests/performance/test_api_performance.py --benchmark-only

# Run with custom configuration
BASE_URL=https://py-txt-trnsfrm.herokuapp.com pytest tests/performance/test_api_performance.py
```

This file provides comprehensive performance testing capabilities including benchmark testing, concurrent request handling validation, and sustained load testing, and can be integrated into a future GitHub Actions workflow.

## Workflow Details

### CI Pipeline (`ci.yml`)
1. **Code Quality**: Fast-fail linting (ruff, black, mypy)
2. **Testing Matrix**: Parallel test execution by type
3. **Security Analysis**: Integrated bandit/safety scanning
4. **Aggregate Results**: Final status determination

### Nightly Security (`security-nightly.yml`)
- Deep security analysis with timeout handling
- Comprehensive dependency vulnerability scanning
- Automatic GitHub issue creation on critical findings
- Organized security reports in `reports/security/`

### Release Pipeline (`release.yml`)
- Version validation and breaking change detection
- Full test suite execution including slow tests
- Git-based Heroku deployment to production
- Automatic changelog generation and GitHub releases

See full documentation for usage examples and troubleshooting.
