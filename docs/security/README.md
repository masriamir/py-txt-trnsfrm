# Security Tooling Documentation

This directory contains documentation and proof-of-concept configurations for security tooling evaluation and migration.

## Files

- **[SECURITY_TOOLING_EVALUATION.md](SECURITY_TOOLING_EVALUATION.md)**: Comprehensive evaluation of Trivy + Semgrep as replacements for Snyk SAST
- **[poc_security_analysis.sh](poc_security_analysis.sh)**: Enhanced POC script with semgrep ci integration and 23 community rulesets
- **[semgrep-rules.yaml](semgrep-rules.yaml)**: Comprehensive local fallback rules (26 security patterns)
- **[LOCAL_SCANNING_GUIDE.md](LOCAL_SCANNING_GUIDE.md)**: Complete guide for local security scanning setup
- **[../workflows/poc-security-workflow.yml](../../.github/workflows/poc-security-workflow.yml)**: GitHub Actions workflow with diff-aware scanning and PR comments

## Quick Start

### Enhanced Local Security Analysis

```bash
# 1. Install tools
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
pip install semgrep

# 2. Login for community rules access (optional but recommended)
semgrep login

# 3. Run enhanced POC analysis
chmod +x docs/security/poc_security_analysis.sh
./docs/security/poc_security_analysis.sh
```

### Features

- ✅ **23 Community Rulesets**: Flask, Python, OWASP Top 10, Docker, JavaScript, etc.
- ✅ **Semgrep CI Integration**: Enhanced authentication and diff-aware scanning
- ✅ **Automatic Fallback**: Local rules when community access unavailable
- ✅ **GitHub Integration**: SARIF upload and PR comments
- ✅ **Authentication Detection**: Reliable login status checking

### Results Location

- Reports generated in: `reports/security/poc/`
- SARIF files for GitHub Security tab integration
- JSON files for programmatic analysis
- Performance metrics and authentication status
- Comprehensive summary with ruleset coverage

## Authentication Setup

### For Enhanced Community Rules

```bash
# Login to Semgrep (recommended)
semgrep login

# Verify authentication
ls -la ~/.semgrep/settings.yml
```

### For CI/CD (GitHub Actions)

Set the `SEMGREP_APP_TOKEN` secret in your repository:
1. Go to Settings → Secrets and variables → Actions
2. Add `SEMGREP_APP_TOKEN` with your Semgrep API token
3. The workflow will automatically use community rulesets when available

## Key Findings

✅ **Recommendation: Proceed with Trivy + Semgrep CI migration**

- **Enhanced Coverage**: 23 community rulesets vs 4 basic Bandit patterns
- **CI/CD Optimized**: semgrep ci command with diff-aware scanning
- **No Usage Limitations**: Open-source tools eliminate commercial quotas
- **GitHub Native Integration**: SARIF upload and PR comments
- **Reliable Authentication**: Proper token handling and fallback strategies
- **Performance**: ~27s for comprehensive 23-ruleset analysis

## Migration Benefits

| Feature | Current (Bandit + Safety) | Enhanced POC (Trivy + Semgrep CI) |
|---------|---------------------------|-----------------------------------|
| **Code Rules** | 4 basic patterns | 23 community rulesets (hundreds of rules) |
| **Authentication** | None required | Optional (enhanced when available) |
| **Diff-Aware Scanning** | No | Yes (PR optimization) |
| **GitHub Integration** | Basic | Native (SARIF + PR comments) |
| **Fallback Strategy** | None | Comprehensive local rules |
| **Performance** | ~1s | ~27s (acceptable for coverage) |

See the full evaluation document and local scanning guide for detailed analysis and setup instructions.