# GitHub Actions CI/CD Pipeline

## Overview
Comprehensive GitHub Actions CI/CD pipeline for py-txt-trnsfrm Flask application with uv dependency management.

## Workflows

### 🚀 ci.yml - Primary CI Pipeline
- **Triggers:** Push to main/develop, PRs, manual dispatch
- **Jobs:** Code Quality → Testing Matrix + Security Analysis → Build & Integration → Aggregate Results
- **Features:** Fast failure, parallel execution, uv caching, comprehensive testing

### 🔒 security-nightly.yml - Nightly Security Scan  
- **Triggers:** Nightly at 2:00 AM UTC, manual dispatch
- **Features:** Deep security analysis, slow tests, automatic issue creation

### 📦 release.yml - Release Pipeline
- **Triggers:** Version tags, releases, manual dispatch  
- **Features:** Version validation, full test suite, Docker builds, Heroku deployment

### ⚡ performance.yml - Performance Testing
- **Triggers:** Manual dispatch, weekly schedule, performance-affecting PRs
- **Features:** Load testing with Locust, benchmark tests, configurable environments

## Key Features

### Optimization
- uv dependency caching with lock file hashing
- Parallel job execution with proper dependencies
- Path-based filtering for efficiency
- Artifact management with appropriate retention

### Security
- Zero tolerance for critical security issues
- Comprehensive scanning (Bandit, Safety, container security)
- Automatic issue creation on findings
- SARIF upload support

### Testing
- Matrix strategy by test type (unit, integration, api, smoke)
- Excludes slow/security tests from main CI
- Individual coverage reports with Codecov integration
- Performance regression detection

### Deployment
- Multi-platform Docker builds
- Container registry integration (GHCR)
- Heroku deployment support
- Post-deployment validation

## Environment Variables
- `CODECOV_TOKEN` - Required for coverage uploads
- `HEROKU_API_KEY`, `HEROKU_EMAIL` - Optional for deployment

See full documentation for usage examples and troubleshooting.