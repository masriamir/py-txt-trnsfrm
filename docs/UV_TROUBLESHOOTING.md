# UV Dependency Management Troubleshooting Guide

## Overview
This guide helps diagnose and fix common `uv sync` dependency management issues in the py-txt-trnsfrm project.

## Quick Diagnosis

### 1. Verify UV Installation
```bash
# Check if uv is installed and working
uv --version

# If not installed, install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Test Basic UV Sync
```bash
# Test dry-run first (safe, shows what would happen)
uv sync --dry-run

# If dry-run looks good, run actual sync
uv sync
```

### 3. Verify Dependencies are Installed
```bash
# List installed packages
uv pip list

# Check for core dependencies
uv pip show flask gunicorn werkzeug
```

## Common Issues and Solutions

### Issue: "uv sync uninstalling all dependencies"

**Possible Causes:**
1. Corrupted uv.lock file
2. Incorrect pyproject.toml configuration
3. Environment conflicts
4. Using incompatible uv flags

**Solutions:**

#### Solution 1: Regenerate Lock File
```bash
# Backup current lock file
cp uv.lock uv.lock.backup

# Regenerate lock file
uv lock --upgrade

# Test sync
uv sync --dry-run
uv sync
```

#### Solution 2: Clean Environment
```bash
# Remove virtual environment and start fresh
rm -rf .venv
uv sync
```

#### Solution 3: Verify Configuration
```bash
# Check pyproject.toml syntax
uv check pyproject.toml

# Validate dependency groups
uv tree
```

### Issue: "Application fails to start after uv sync"

**Diagnosis:**
```bash
# Test application import
uv run python -c "import app; print('✅ App imports successfully')"

# Check if all required dependencies are present
uv pip list | grep -E "(flask|gunicorn|werkzeug)"
```

**Solutions:**

#### Install Missing Dependencies
```bash
# Install core dependencies only
uv sync

# Install all development dependencies
uv sync --group dev --group test --group security
```

#### Verify App Structure
```bash
# Ensure app directory structure is correct
ls -la app/
```

### Issue: "Docker deployment fails"

**Common Problem:** Using wrong uv flags in Dockerfile

**Solution:** Update Dockerfile to use correct flags:
```dockerfile
# Install Python dependencies (production only)
RUN uv sync --frozen --no-dev
```

**Verification:**
```bash
# Test Docker-style sync locally
uv sync --frozen --no-dev
uv pip list  # Should show only production dependencies
```

## Dependency Group Management

### Install Specific Groups
```bash
# Development tools only
uv sync --group dev

# Testing dependencies only
uv sync --group test

# Security tools only
uv sync --group security

# All groups for development
uv sync --group dev --group test --group security
```

### Verify Group Contents
```bash
# Show dependency tree
uv tree

# Check what would be installed for a group
uv sync --group test --dry-run
```

## Advanced Troubleshooting

### Lock File Issues
```bash
# Check lock file consistency
uv lock --check

# Force regenerate if corrupted
rm uv.lock
uv lock
```

### Environment Debugging
```bash
# Show environment info
uv python info

# List available Python versions
uv python list

# Check virtual environment location
uv venv --info
```

### Configuration Validation
```bash
# Validate pyproject.toml
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Check for syntax errors
uv check
```

## Prevention Best Practices

### 1. Always Use Dry-Run First
```bash
# Before making changes, always check what would happen
uv sync --dry-run
uv lock --dry-run
```

### 2. Commit Lock File
```bash
# Always commit uv.lock to version control
git add uv.lock
git commit -m "Update dependency lock file"
```

### 3. Use Specific Commands for Different Environments

**Development:**
```bash
uv sync --group dev --group test --group security
```

**Production (Docker):**
```bash
uv sync --frozen --no-dev
```

**CI/CD:**
```bash
uv sync --frozen
```

### 4. Regular Maintenance
```bash
# Periodically update dependencies
uv lock --upgrade

# Check for security vulnerabilities
uv run safety scan
```

## Testing Your Setup

Run the provided test script to verify everything works:
```bash
python tests/test_uv_sync.py
```

This script validates:
- Core dependencies are installed
- Dependency groups are configured correctly
- Application can import successfully
- Production deployment works

## Getting Help

If issues persist:

1. **Check UV Documentation:** https://docs.astral.sh/uv/
2. **Run Validation Test:** `python tests/test_uv_sync.py`
3. **Check Project Issues:** Look for similar issues in the GitHub repository
4. **Create New Issue:** Include output of `uv --version`, `uv pip list`, and error messages

## Recovery Commands

If everything breaks, use these commands to get back to a working state:

```bash
# Nuclear option: complete reset
rm -rf .venv uv.lock
uv lock
uv sync

# Verify it works
uv run python -c "import app; print('✅ Recovery successful')"
```