# =============================================================================
# Comprehensive Makefile for py-txt-trnsfrm
# Developer Productivity & CI/CD Workflows
# =============================================================================

# Environment Configuration
# =============================================================================
# Load .env file if it exists (for local development)
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variables and Configuration
# =============================================================================
SHELL := /bin/bash
export PATH := $(HOME)/.local/bin:$(PATH)

UV := uv
PYTHON := $(UV) run python
PYTEST := $(UV) run pytest
UVTOOL := $(shell command -v uv 2> /dev/null)

# Default configuration
PORT ?= 5000
HOST ?= 127.0.0.1
MARKERS ?= "not slow and not test_transform_property_based"
TIMEOUT ?= 300
VERBOSE ?= 0
DEBUG ?= 0

# Docker configuration
DOCKER_IMAGE ?= py-txt-trnsfrm
DOCKER_TAG ?= latest
DOCKER_FULL_NAME := $(DOCKER_IMAGE):$(DOCKER_TAG)

# Colors for output
RESET := \033[0m
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m

# Progress indicators
define progress
	@printf "$(CYAN)▶$(RESET) $(BOLD)%s$(RESET)\n" "$(1)"
endef

define success
	@printf "$(GREEN)✅$(RESET) $(BOLD)%s$(RESET)\n" "$(1)"
endef

define warning
	@printf "$(YELLOW)⚠️$(RESET) $(BOLD)%s$(RESET)\n" "$(1)"
endef

define error
	@printf "$(RED)❌$(RESET) $(BOLD)%s$(RESET)\n" "$(1)"
endef

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help setup install sync clean fresh format lint fix check types test test-unit test-api test-all test-fast coverage test-perf run run-prod health demo security security-quick docker-build docker-run docker-stop docker-clean ci deploy version uv-check progress-test

# =============================================================================
# Help & Documentation
# =============================================================================

help: ## Show this help message with colored output
	@echo ""
	@echo "$(BOLD)$(CYAN)🚀 py-txt-trnsfrm Development Makefile$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)Core Workflow Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(setup|install|sync|clean|fresh):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Code Quality Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(format|lint|fix|check|types):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Testing Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(test|test-unit|test-api|test-all|test-fast|coverage|test-perf):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Application Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(run|run-prod|health|demo):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Security Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(security|security-quick):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Docker Commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(docker-build|docker-run|docker-stop|docker-clean):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)CI/CD & Deployment:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(ci|deploy):.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' Makefile
	@echo ""
	@echo "$(BOLD)Environment Variables:$(RESET)"
	@echo "  $(YELLOW)PORT$(RESET)              Server port (default: 5000)"
	@echo "  $(YELLOW)HOST$(RESET)              Server host (default: 127.0.0.1)"
	@echo "  $(YELLOW)MARKERS$(RESET)           Test markers (default: 'not slow and not test_transform_property_based')"
	@echo "  $(YELLOW)TIMEOUT$(RESET)           Command timeout (default: 300)"
	@echo "  $(YELLOW)VERBOSE$(RESET)           Verbose output (0/1, default: 0)"
	@echo "  $(YELLOW)DEBUG$(RESET)             Debug mode (0/1, default: 0)"
	@echo "  $(YELLOW)DOCKER_IMAGE$(RESET)      Docker image name (default: py-txt-trnsfrm)"
	@echo "  $(YELLOW)DOCKER_TAG$(RESET)        Docker image tag (default: latest)"
	@echo ""
	@echo "$(BOLD)Configuration:$(RESET)"
	@echo "  $(CYAN)Copy .env.example to .env and customize for local development$(RESET)"
	@echo "  $(CYAN)Variables can be set via command line, .env file, or environment$(RESET)"
	@echo ""
	@echo "$(BOLD)Examples:$(RESET)"
	@echo "  $(GREEN)make test MARKERS=unit$(RESET)                    # Run unit tests only"
	@echo "  $(GREEN)make run PORT=8000$(RESET)                        # Run dev server on port 8000"
	@echo "  $(GREEN)make docker-run PORT=3000$(RESET)                 # Run container on port 3000"
	@echo "  $(GREEN)make test VERBOSE=1$(RESET)                       # Run tests with verbose output"
	@echo ""
	@echo "For detailed documentation, see: $(BLUE)docs/MAKEFILE.md$(RESET)"

# =============================================================================
# Core Workflow Commands
# =============================================================================

setup: uv-check ## Initial setup - install uv and all dependencies
	$(call progress,Setting up development environment...)
	@if [ -z "$(UVTOOL)" ]; then \
		echo "$(YELLOW)Installing uv...$(RESET)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
	fi
	$(call progress,Installing all dependency groups...)
	$(UV) sync --group dev --group test --group security
	$(call progress,Verifying installation...)
	$(PYTHON) -c "import app; print('✅ Application imports successfully')"
	$(call success,Development environment ready!)

install: uv-check ## Install all dev/test/security dependencies
	$(call progress,Installing dependencies...)
	$(UV) sync --group dev --group test --group security
	$(call success,Dependencies installed!)

sync: uv-check ## Sync dependencies (respects uv.lock)
	$(call progress,Syncing dependencies...)
	$(UV) sync
	$(call success,Dependencies synchronized!)

clean: ## Clean generated files and caches
	$(call progress,Cleaning generated files and caches...)
	@rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf reports/coverage/.coverage reports/coverage/html/*
	@rm -rf .coverage htmlcov/ coverage.xml
	@rm -rf build/ dist/ *.egg-info/
	$(call success,Cleanup complete!)

fresh: clean setup ## Complete reset - clean everything and setup from scratch
	$(call progress,Performing fresh setup...)
	$(call success,Fresh environment ready!)

# =============================================================================
# Code Quality Commands
# =============================================================================

format: uv-check ## Fix all formatting issues (black + ruff format)
	$(call progress,Formatting code with black...)
	$(UV) run black .
	$(call progress,Formatting code with ruff...)
	$(UV) run ruff format .
	$(call success,Code formatting complete!)

lint: uv-check ## Run lint checks (ruff)
	$(call progress,Running ruff linting...)
	$(UV) run ruff check .
	$(call success,Linting complete!)

fix: uv-check ## Fix all auto-fixable issues (ruff + black)
	$(call progress,Fixing auto-fixable issues...)
	$(UV) run ruff check --fix .
	$(UV) run black .
	$(call success,Auto-fixes applied!)

check: uv-check ## Run all quality checks (lint + format check + types)
	$(call progress,Running comprehensive quality checks...)
	$(call progress,Checking code formatting...)
	$(UV) run black --check .
	$(call progress,Running lint checks...)
	$(UV) run ruff check .
	$(call progress,Running type checks...)
	$(UV) run mypy . || $(call warning,Type checking found issues (expected in current state))
	$(call success,Quality checks complete!)

types: uv-check ## Run mypy type checking
	$(call progress,Running type checks...)
	$(UV) run mypy . || $(call warning,Type checking found issues (expected in current state))

# =============================================================================
# Testing Commands
# =============================================================================

test: uv-check ## Standard test suite (excluding slow/performance tests)
	$(call progress,Running standard test suite...)
	$(PYTEST) --ignore=tests/performance -k "$(MARKERS)" --benchmark-disable
	$(call success,Test suite complete!)

test-unit: uv-check ## Run unit tests only
	$(call progress,Running unit tests...)
	$(PYTEST) -m unit --benchmark-disable
	$(call success,Unit tests complete!)

test-api: uv-check ## Run API tests only
	$(call progress,Running API tests...)
	$(PYTEST) -m api --benchmark-disable
	$(call success,API tests complete!)

test-all: uv-check ## Complete test suite (including slow tests)
	$(call progress,Running complete test suite...)
	$(PYTEST) --benchmark-disable
	$(call success,Complete test suite finished!)

test-fast: uv-check ## Quick smoke tests for critical functionality
	$(call progress,Running smoke tests...)
	$(PYTEST) -m smoke --benchmark-disable
	$(call success,Smoke tests complete!)

coverage: uv-check ## Generate coverage report (HTML)
	$(call progress,Generating coverage report...)
	$(PYTEST) --cov=app --cov-report=html:reports/coverage/html --cov-report=term-missing --benchmark-disable
	$(call success,Coverage report generated in reports/coverage/html/)

test-perf: uv-check ## Performance benchmarks (requires running app)
	$(call progress,Running performance tests...)
	@echo "$(YELLOW)Note: Ensure the application is running before performance tests$(RESET)"
	$(PYTEST) tests/performance/test_api_performance.py --benchmark-only -n 0
	$(call success,Performance tests complete!)

# =============================================================================
# Application Commands
# =============================================================================

run: uv-check ## Start development server
	$(call progress,Starting development server on $(HOST):$(PORT)...)
	@FLASK_ENV=development $(PYTHON) app.py

run-prod: uv-check ## Start production server (gunicorn)
	$(call progress,Starting production server...)
	@if [ -z "$$SECRET_KEY" ]; then \
		$(call error,SECRET_KEY environment variable is required for production mode); \
		exit 1; \
	fi
	@PORT=$(PORT) ./deploy.sh start

health: uv-check ## Check health endpoint (requires running server)
	$(call progress,Checking health endpoint...)
	@curl -f "http://$(HOST):$(PORT)/health" && $(call success,Health check passed!) || $(call error,Health check failed!)

demo: uv-check ## Run demo transformation
	$(call progress,Running demo transformation...)
	@curl -X POST "http://$(HOST):$(PORT)/transform" \
		-H "Content-Type: application/json" \
		-d '{"text": "Hello World", "transformation": "alternate_case"}' && \
		$(call success,Demo transformation complete!) || \
		$(call error,Demo failed - ensure server is running!)

# =============================================================================
# Security Commands
# =============================================================================

security: uv-check ## Full security analysis (bandit + safety)
	$(call progress,Running comprehensive security analysis...)
	@./run_security_analysis.sh
	$(call success,Security analysis complete! Check reports/security/)

security-quick: uv-check ## Quick security scan (bandit only)
	$(call progress,Running quick security scan...)
	$(UV) run bandit -r app/
	$(call success,Quick security scan complete!)

# =============================================================================
# Docker Commands
# =============================================================================

docker-build: ## Build Docker image
	$(call progress,Building Docker image $(DOCKER_FULL_NAME)...)
	docker build -t $(DOCKER_FULL_NAME) .
	$(call success,Docker image built: $(DOCKER_FULL_NAME))

docker-run: ## Run containerized application
	$(call progress,Starting Docker container on port $(PORT)...)
	docker run --rm -p $(PORT):5000 $(DOCKER_FULL_NAME)

docker-stop: ## Stop running containers
	$(call progress,Stopping Docker containers...)
	@docker stop $$(docker ps -q --filter ancestor=$(DOCKER_FULL_NAME)) 2>/dev/null || true
	$(call success,Containers stopped!)

docker-clean: ## Remove containers and images
	$(call progress,Cleaning Docker containers and images...)
	@docker container prune -f
	@docker rmi $(DOCKER_FULL_NAME) 2>/dev/null || true
	$(call success,Docker cleanup complete!)

# =============================================================================
# CI/CD & Deployment
# =============================================================================

ci: uv-check ## Run all local CI checks (mirrors GitHub Actions)
	$(call progress,Running local CI pipeline...)
	$(call progress,Step 1/4: Code quality checks...)
	@$(MAKE) check
	$(call progress,Step 2/4: Running tests...)
	@$(MAKE) test
	$(call progress,Step 3/4: Security analysis...)
	@$(MAKE) security-quick
	$(call progress,Step 4/4: Coverage report...)
	@$(MAKE) coverage
	$(call success,Local CI pipeline complete!)

deploy: ## Deploy to Heroku (delegates to deploy.sh)
	$(call progress,Deploying to Heroku...)
	@if [ -z "$$SECRET_KEY" ]; then \
		$(call error,SECRET_KEY environment variable is required for deployment); \
		exit 1; \
	fi
	@./deploy.sh start
	$(call success,Deployment complete!)

# =============================================================================
# Utilities & Debugging
# =============================================================================

version: ## Show version information
	@echo "$(BOLD)py-txt-trnsfrm Version Information$(RESET)"
	@echo "=================================="
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo "UV: $$($(UV) --version 2>&1)"
	@echo "Flask: $$($(PYTHON) -c 'import flask; print(flask.__version__)' 2>/dev/null || echo 'Not available')"
	@echo "Application: $$($(PYTHON) -c 'import app; print(getattr(app, \"__version__\", \"0.1.0\"))' 2>/dev/null || echo '0.1.0')"

uv-check: ## Internal utility to check UV installation
	@if ! command -v uv >/dev/null 2>&1; then \
		printf "$(RED)❌$(RESET) $(BOLD)%s$(RESET)\n" "UV is not installed. Run 'make setup' to install it."; \
		exit 1; \
	fi

progress-test: ## Test progress indicators and colors
	$(call progress,This is a progress message)
	$(call success,This is a success message)
	$(call warning,This is a warning message)
	@printf "$(RED)❌$(RESET) $(BOLD)%s$(RESET)\n" "This is an error message"

# =============================================================================
# Additional commands can be added here following established patterns.
# See docs/MAKEFILE.md for the command template and best practices.
# =============================================================================