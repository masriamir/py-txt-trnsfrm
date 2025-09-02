# Local Security Scanning Guide

This guide provides instructions for running comprehensive security analysis locally using Trivy + Semgrep CI, following official Semgrep best practices.

## Quick Start

```bash
# 1. Install Semgrep and login for community rules access
pip install semgrep
semgrep login

# 2. Run the enhanced POC analysis script
./docs/security/poc_security_analysis.sh
```

## Prerequisites

### Install Semgrep
```bash
# Via pip (recommended)
pip install semgrep

# Via Homebrew (macOS)
brew install semgrep

# Via npm (alternative)
npm install -g @semgrep/semgrep
```

### Install Trivy
```bash
# Via package manager (Ubuntu/Debian)
sudo apt-get install trivy

# Via Homebrew (macOS)
brew install trivy

# Via GitHub releases
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

## Authentication Setup

### For Enhanced Community Rules Access

1. **Create Semgrep account**: Visit [semgrep.dev](https://semgrep.dev)
2. **Login locally**:
   ```bash
   semgrep login
   ```
3. **Verify authentication**:
   ```bash
   ls -la ~/.semgrep/settings.yml
   ```

### Environment Variables (Optional)

For CI/CD integration or advanced usage:

```bash
# Set API token (if not using semgrep login)
export SEMGREP_APP_TOKEN="your-token-here"

# Configure repository metadata
export SEMGREP_REPO_NAME="py-txt-trnsfrm"
export SEMGREP_BRANCH="main"
export SEMGREP_REPO_URL="https://github.com/masriamir/py-txt-trnsfrm"

# Enable diff-aware scanning (in git repositories)
export SEMGREP_BASELINE_REF="main"
```

## Running Scans

### Automated POC Script (Recommended)

```bash
# Run comprehensive analysis with 23 community rulesets
./docs/security/poc_security_analysis.sh
```

**Features:**
- ✅ Trivy filesystem and configuration scanning
- ✅ Semgrep with 23 community rulesets
- ✅ Automatic authentication detection
- ✅ Diff-aware scanning (when in git repository)
- ✅ SARIF output for GitHub Security integration
- ✅ Performance metrics and detailed reporting

### Manual Semgrep CI Usage

For direct `semgrep ci` usage:

```bash
# Basic scan with community rules (requires authentication)
semgrep ci --config=p/flask,p/python,p/bandit,p/security-audit

# Full ruleset (23 community rulesets)
semgrep ci --config=p/flask,p/nginx,p/xss,p/python,p/bandit,p/docker,p/secrets,p/comment,p/javascript,p/r2c-bug-scan,p/owasp-top-ten,p/github-actions,p/security-audit,p/docker-compose,p/semgrep-rule-ci,p/secure-defaults,p/security-headers,p/command-injection,p/insecure-transport,p/r2c-best-practices,p/r2c-security-audit,p/semgrep-rule-lints,p/semgrep-misconfigurations

# With custom output
semgrep ci --config=p/flask,p/python --json --output=custom_results.json
```

### Fallback Local Rules

If community rules are unavailable:

```bash
# Use local comprehensive ruleset
semgrep --config=docs/security/semgrep-rules.yaml --json --output=results.json .
```

## Output Formats

### JSON Output (for tooling integration)
```bash
semgrep ci --config=p/flask,p/python --json --output=results.json
```

### SARIF Output (for GitHub Security tab)
```bash
semgrep ci --config=p/flask,p/python --sarif --output=results.sarif
```

### Human-readable Output
```bash
semgrep ci --config=p/flask,p/python --text
```

## Diff-Aware Scanning

For scanning only changed files (requires git repository):

```bash
# Set baseline for comparison
export SEMGREP_BASELINE_REF="main"

# Run diff-aware scan
semgrep ci --config=p/flask,p/python
```

## Community Rulesets Used

Our POC uses 23 comprehensive community rulesets:

**Core Security & Best Practices:**
- `p/flask` - Flask web framework security
- `p/python` - Python language security patterns
- `p/bandit` - Python security issues (mirrors Bandit tool)
- `p/security-audit` - General security audit rules
- `p/owasp-top-ten` - OWASP Top 10 vulnerabilities
- `p/r2c-security-audit` - R2C security analysis
- `p/r2c-best-practices` - Development best practices
- `p/secure-defaults` - Secure configuration defaults

**Vulnerability Detection:**
- `p/xss` - Cross-site scripting detection
- `p/secrets` - Hardcoded secrets detection
- `p/command-injection` - Command injection vulnerabilities
- `p/insecure-transport` - Insecure communication patterns
- `p/security-headers` - Missing security headers
- `p/r2c-bug-scan` - General bug detection

**Infrastructure & DevOps Security:**
- `p/docker` - Docker security best practices
- `p/docker-compose` - Docker Compose security
- `p/nginx` - Nginx configuration security
- `p/github-actions` - GitHub Actions security
- `p/semgrep-rule-ci` - CI/CD security patterns
- `p/semgrep-misconfigurations` - Infrastructure misconfigurations

**Code Quality & Language Support:**
- `p/javascript` - JavaScript security patterns
- `p/comment` - Comment-based security annotations
- `p/semgrep-rule-lints` - Rule quality enforcement

## Integration with GitHub Security

### Upload SARIF Results

```bash
# Generate SARIF
semgrep ci --config=p/flask,p/python --sarif --output=semgrep.sarif

# Upload to GitHub (requires gh CLI and appropriate permissions)
gh api repos/:owner/:repo/code-scanning/sarifs \
  --method POST \
  --field commit_sha=$(git rev-parse HEAD) \
  --field ref=refs/heads/$(git branch --show-current) \
  --field sarif=@semgrep.sarif
```

### View Results

- **GitHub Security Tab**: Navigate to your repository's Security tab
- **Pull Request Comments**: Automatic comments on PRs (when configured)
- **Security Alerts**: GitHub will create alerts for new findings

## Performance Optimization

### For Large Repositories

```bash
# Limit file types
semgrep ci --include="*.py" --include="*.js" --config=p/flask,p/python

# Exclude directories
semgrep ci --exclude="tests/" --exclude="node_modules/" --config=p/flask,p/python

# Use specific rules only
semgrep ci --config=p/flask --config=p/python
```

### For CI/CD Environments

```bash
# Disable version checks for faster execution
semgrep ci --disable-version-check --config=p/flask,p/python

# Quiet mode
semgrep ci --quiet --config=p/flask,p/python
```

## Troubleshooting

### Authentication Issues

```bash
# Check login status
semgrep --version
cat ~/.semgrep/settings.yml

# Re-login if needed
semgrep logout
semgrep login
```

### Community Rules Access

```bash
# Test community rules access
semgrep --config=p/flask --dry-run .

# Fallback to local rules
semgrep --config=docs/security/semgrep-rules.yaml .
```

### Network Issues

```bash
# Use local rules if network unavailable
export SEMGREP_FORCE_LOCAL_RULES=1
semgrep --config=docs/security/semgrep-rules.yaml .
```

## Best Practices

1. **Always authenticate** for full community rule access
2. **Use `semgrep ci`** instead of regular `semgrep` for CI/CD
3. **Enable diff-aware scanning** for faster PR checks
4. **Generate SARIF output** for GitHub Security integration
5. **Maintain local fallback rules** for reliability
6. **Monitor performance** and optimize for your repository size
7. **Regularly update** rulesets and Semgrep version

## Resources

- [Semgrep CLI Documentation](https://semgrep.dev/docs/getting-started/cli)
- [Semgrep CI Documentation](https://semgrep.dev/docs/semgrep-ci/)
- [Community Rules Registry](https://semgrep.dev/r)
- [GitHub Integration Guide](https://semgrep.dev/docs/semgrep-appsec-platform/github-pr-comments)
- [SARIF Upload Documentation](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github)