# Security Tooling Documentation

This directory contains documentation and proof-of-concept configurations for security tooling evaluation and migration.

## Files

- **[SECURITY_TOOLING_EVALUATION.md](SECURITY_TOOLING_EVALUATION.md)**: Comprehensive evaluation of Trivy + Semgrep as replacements for Snyk SAST
- **[poc_security_analysis.sh](poc_security_analysis.sh)**: Proof-of-concept script demonstrating Trivy + Semgrep integration
- **[../workflows/poc-security-workflow.yml](../../.github/workflows/poc-security-workflow.yml)**: GitHub Actions workflow for POC security scanning

## Quick Start

### Run POC Security Analysis Locally

```bash
# Install tools
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
pip install semgrep

# Run POC analysis
chmod +x docs/security/poc_security_analysis.sh
./docs/security/poc_security_analysis.sh
```

### Results Location

- Reports generated in: `reports/security/poc/`
- SARIF files for GitHub Security tab integration
- JSON files for programmatic analysis
- Performance metrics and summary

## Key Findings

✅ **Recommendation: Proceed with Trivy + Semgrep migration**

- Complete feature coverage vs current tools
- No usage limitations or quotas
- Enhanced GitHub Actions integration
- SARIF output for Security tab
- Acceptable performance impact (<10s total scan time)

See the full evaluation document for detailed analysis and migration strategy.