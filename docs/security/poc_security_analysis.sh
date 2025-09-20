#!/bin/bash
#
# POC Security Analysis Script using Trivy + Semgrep
#
# This script demonstrates the proposed replacement for Snyk with open-source tools.
# Uses semgrep ci for proper CI/CD integration and community ruleset access.
#
# Usage: ./poc_security_analysis.sh
#
# Environment Variables:
#   SEMGREP_APP_TOKEN - Authentication token for Semgrep community rules
#   TRIVY_PATH        - Path to trivy binary (default: trivy)
#   SEMGREP_PATH      - Path to semgrep binary (default: semgrep)
#
# Copyright 2024 py-txt-trnsfrm
# Licensed under the MIT License

set -euo pipefail

# Global constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
declare -r SCRIPT_DIR
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
declare -r PROJECT_ROOT
declare -r SEMGREP_CONFIG="${SCRIPT_DIR}/semgrep-rules.yaml"
declare -r POC_REPORTS_DIR="${PROJECT_ROOT}/reports/security/poc"

# Community rulesets to use (from https://semgrep.dev/r)
declare -ra SEMGREP_COMMUNITY_RULESETS=(
  "p/flask"
  "p/nginx"
  "p/xss"
  "p/python"
  "p/bandit"
  "p/docker"
  "p/secrets"
  "p/comment"
  "p/javascript"
  "p/r2c-bug-scan"
  "p/owasp-top-ten"
  "p/github-actions"
  "p/security-audit"
  "p/docker-compose"
  "p/semgrep-rule-ci"
  "p/secure-defaults"
  "p/security-headers"
  "p/command-injection"
  "p/insecure-transport"
  "p/r2c-best-practices"
  "p/r2c-security-audit"
  "p/semgrep-rule-lints"
  "p/semgrep-misconfigurations"
)

# Global variables
trivy_path="${TRIVY_PATH:-trivy}"
semgrep_path="${SEMGREP_PATH:-semgrep}"
start_time=""
trivy_duration=""
semgrep_duration=""
semgrep_logged_in=false
semgrep_ci_success=false
diff_aware_available=false

#######################################
# Print error message and exit
# Globals:
#   None
# Arguments:
#   Error message
# Outputs:
#   Error message to stderr
#######################################
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
  exit 1
}

#######################################
# Initialize environment and validate prerequisites
# Globals:
#   PROJECT_ROOT, SEMGREP_CONFIG, POC_REPORTS_DIR, diff_aware_available
# Arguments:
#   None
# Outputs:
#   Status messages
#######################################
initialize_environment() {
  echo "🔒 Running POC security analysis with Trivy + Semgrep..."
  echo "📁 Project root: ${PROJECT_ROOT}"

  # Create reports directory structure from project root
  mkdir -p "${POC_REPORTS_DIR}"

  # Validate Semgrep config file exists
  if [[ ! -f "${SEMGREP_CONFIG}" ]]; then
    err "Semgrep config file not found: ${SEMGREP_CONFIG}"
  fi

  # Setup environment variables for Semgrep CI
  # Note: These variables must be exported (not local) for semgrep to access them
  export SEMGREP_REPO_NAME="${SEMGREP_REPO_NAME:-py-txt-trnsfrm}"
  export SEMGREP_BRANCH="${SEMGREP_BRANCH:-main}"
  export SEMGREP_JOB_URL="${SEMGREP_JOB_URL:-local}"
  export SEMGREP_COMMIT="${SEMGREP_COMMIT:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
  export SEMGREP_REPO_URL="${SEMGREP_REPO_URL:-https://github.com/masriamir/py-txt-trnsfrm}"

  # Check if we're in a git repository for diff-aware scanning
  if git rev-parse --git-dir > /dev/null 2>&1; then
    # Note: SEMGREP_BASELINE_REF must be exported for diff-aware scanning
    export SEMGREP_BASELINE_REF="${SEMGREP_BASELINE_REF:-main}"
    diff_aware_available=true
  else
    diff_aware_available=false
  fi

  # Change to project root for scans
  cd "${PROJECT_ROOT}" || err "Failed to change to project root: ${PROJECT_ROOT}"

  # Start timing
  start_time=$(date +%s)
}

#######################################
# Check Semgrep authentication status and setup token
# Globals:
#   semgrep_logged_in, SEMGREP_APP_TOKEN
# Arguments:
#   None
# Outputs:
#   Authentication status messages
#######################################
check_semgrep_authentication() {
  echo "🔐 Checking Semgrep authentication status..."
  semgrep_logged_in=false

  # Check for Semgrep settings file which indicates authentication
  if [[ -f "${HOME}/.semgrep/settings.yml" ]]; then
    # Verify the settings file contains authentication token
    if grep -q "api_token" "${HOME}/.semgrep/settings.yml" 2>/dev/null; then
      echo "✅ Semgrep authenticated - using community rulesets with semgrep ci"
      semgrep_logged_in=true
      # Export token from settings file for semgrep ci
      if [[ -z "${SEMGREP_APP_TOKEN:-}" ]]; then
        local token
        token=$(grep "api_token:" "${HOME}/.semgrep/settings.yml" | cut -d'"' -f2 2>/dev/null || true)
        if [[ -n "${token}" ]]; then
          # Note: SEMGREP_APP_TOKEN must be exported for semgrep authentication
          export SEMGREP_APP_TOKEN="${token}"
        fi
      fi
    fi
  fi

  if [[ "${semgrep_logged_in}" == false ]]; then
    echo "⚠️  Semgrep not logged in - some community rules may be limited"
    echo "💡 To login: semgrep login (for full access to community rules)"
    echo "💡 For CI/CD: Set SEMGREP_APP_TOKEN environment variable"
  fi
}

#######################################
# Build comma-separated community ruleset configuration
# Globals:
#   SEMGREP_COMMUNITY_RULESETS
# Arguments:
#   None
# Outputs:
#   Comma-separated ruleset string
#######################################
build_community_config() {
  local community_config=""
  local ruleset

  for ruleset in "${SEMGREP_COMMUNITY_RULESETS[@]}"; do
    if [[ -z "${community_config}" ]]; then
      community_config="${ruleset}"
    else
      community_config="${community_config},${ruleset}"
    fi
  done

  echo "${community_config}"
}

#######################################
# Run Trivy filesystem and configuration scans
# Globals:
#   POC_REPORTS_DIR, trivy_path, trivy_duration
# Arguments:
#   None
# Outputs:
#   Trivy scan results and status messages
#######################################
run_trivy_scans() {
  echo "📊 Running Trivy filesystem scan..."
  local trivy_start trivy_end
  trivy_start=$(date +%s)

  # Run filesystem scan first, fallback to config scan
  "${trivy_path}" fs --format json \
    --output "${POC_REPORTS_DIR}/trivy_fs.json" . 2>/dev/null || {
    echo "⚠️  Trivy filesystem scan failed - trying config scan only..."
    "${trivy_path}" config --format json \
      --output "${POC_REPORTS_DIR}/trivy_config.json" .
  }

  trivy_end=$(date +%s)
  trivy_duration=$((trivy_end - trivy_start))

  # Generate SARIF output for GitHub Security integration
  echo "📊 Generating Trivy SARIF output..."
  "${trivy_path}" config --format sarif \
    --output "${POC_REPORTS_DIR}/trivy.sarif" . 2>/dev/null || {
    echo "⚠️  Trivy SARIF generation failed"
  }
}

#######################################
# Run Semgrep analysis with community rulesets and fallback
# Globals:
#   POC_REPORTS_DIR, semgrep_path, semgrep_logged_in, semgrep_ci_success,
#   semgrep_duration, SEMGREP_CONFIG
# Arguments:
#   community_config - Comma-separated community ruleset string
# Outputs:
#   Semgrep scan results and status messages
#######################################
run_semgrep_analysis() {
  local community_config="${1}"

  echo "🔍 Running Semgrep code analysis..."
  echo "🔍 Using community rulesets: ${community_config}"
  echo "📋 Total rulesets: ${#SEMGREP_COMMUNITY_RULESETS[@]}"

  if [[ "${diff_aware_available}" == true ]]; then
    echo "📊 Git repository detected - diff-aware scanning available"
  else
    echo "📊 Full repository scan (no git repository detected)"
  fi

  local semgrep_start semgrep_end
  semgrep_start=$(date +%s)

  # Try semgrep ci first (recommended for CI/CD), fallback to regular semgrep
  if [[ "${semgrep_logged_in}" == true ]]; then
    echo "🚀 Running semgrep ci for enhanced integration..."

    if semgrep ci --config="${community_config}" --json \
        --output="${POC_REPORTS_DIR}/semgrep.json" \
        --disable-version-check 2>/dev/null; then
      echo "✅ Semgrep CI scan completed successfully"
      semgrep_ci_success=true
    else
      echo "⚠️  Semgrep CI failed, trying regular semgrep with community rules..."
      semgrep_ci_success=false
    fi
  else
    echo "⚠️  No authentication - using regular semgrep command"
    semgrep_ci_success=false
  fi

  # Fallback to regular semgrep if semgrep ci failed or no auth
  if [[ "${semgrep_ci_success}" != true ]]; then
    echo "🔄 Falling back to regular semgrep command..."
    "${semgrep_path}" --config="${community_config}" --json \
      --output="${POC_REPORTS_DIR}/semgrep.json" . \
      --disable-version-check 2>/dev/null || {
      echo "⚠️  Community rules failed, using local rules..."
      "${semgrep_path}" --config="${SEMGREP_CONFIG}" --json \
        --output="${POC_REPORTS_DIR}/semgrep.json" . \
        --disable-version-check
    }
  fi

  semgrep_end=$(date +%s)
  semgrep_duration=$((semgrep_end - semgrep_start))
}

#######################################
# Generate Semgrep SARIF output for GitHub Security integration
# Globals:
#   POC_REPORTS_DIR, semgrep_path, semgrep_logged_in, SEMGREP_CONFIG
# Arguments:
#   community_config - Comma-separated community ruleset string
# Outputs:
#   Semgrep SARIF results and status messages
#######################################
generate_semgrep_sarif() {
  local community_config="${1}"

  echo "🔍 Generating Semgrep SARIF output..."

  if [[ "${semgrep_logged_in}" == true ]]; then
    # Try semgrep ci for SARIF (automatically uploads if configured)
    if ! semgrep ci --config="${community_config}" --sarif \
        --output="${POC_REPORTS_DIR}/semgrep.sarif" \
        --disable-version-check 2>/dev/null; then
      echo "⚠️  Semgrep CI SARIF failed, trying regular semgrep..."
      "${semgrep_path}" --config="${community_config}" --sarif \
        --output="${POC_REPORTS_DIR}/semgrep.sarif" . \
        --disable-version-check 2>/dev/null || {
        echo "⚠️  Community rules SARIF failed, trying local rules..."
        "${semgrep_path}" --config="${SEMGREP_CONFIG}" --sarif \
          --output="${POC_REPORTS_DIR}/semgrep.sarif" . \
          --disable-version-check 2>/dev/null || {
          echo "⚠️  Semgrep SARIF generation failed"
        }
      }
    fi
  else
    # No authentication - use regular semgrep
    "${semgrep_path}" --config="${community_config}" --sarif \
      --output="${POC_REPORTS_DIR}/semgrep.sarif" . \
      --disable-version-check 2>/dev/null || {
      echo "⚠️  Community rules SARIF failed, trying local rules..."
      "${semgrep_path}" --config="${SEMGREP_CONFIG}" --sarif \
        --output="${POC_REPORTS_DIR}/semgrep.sarif" . \
        --disable-version-check 2>/dev/null || {
        echo "⚠️  Semgrep SARIF generation failed"
      }
    }
  fi
}

#######################################
# Count issues from JSON reports using jq
# Globals:
#   POC_REPORTS_DIR
# Arguments:
#   None
# Outputs:
#   Issue counts to summary files
#######################################
count_security_issues() {
  local trivy_issues=0
  local trivy_failures=0
  local semgrep_issues=0

  # Count Trivy issues
  if [[ -f "${POC_REPORTS_DIR}/trivy_fs.json" ]]; then
    trivy_issues=$(jq '.Results[]?.Vulnerabilities // [] | length' \
      "${POC_REPORTS_DIR}/trivy_fs.json" 2>/dev/null | \
      awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Issues Found: ${trivy_issues}" >> \
      "${POC_REPORTS_DIR}/poc_summary.txt"
  elif [[ -f "${POC_REPORTS_DIR}/trivy_config.json" ]]; then
    trivy_failures=$(jq '.Results[]?.MisconfSummary?.Failures // 0' \
      "${POC_REPORTS_DIR}/trivy_config.json" 2>/dev/null | \
      awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Config Issues: ${trivy_failures}" >> \
      "${POC_REPORTS_DIR}/poc_summary.txt"
  fi

  # Count Semgrep issues
  if [[ -f "${POC_REPORTS_DIR}/semgrep.json" ]]; then
    semgrep_issues=$(jq '.results | length' \
      "${POC_REPORTS_DIR}/semgrep.json" 2>/dev/null || echo "0")
    echo "🔍 Semgrep Issues Found: ${semgrep_issues}" >> \
      "${POC_REPORTS_DIR}/poc_summary.txt"
  fi

  # Add findings to GitHub summary
  {
    if [[ -f "${POC_REPORTS_DIR}/trivy_fs.json" ]] || [[ -f "${POC_REPORTS_DIR}/trivy_config.json" ]]; then
      local trivy_total=$((trivy_issues + trivy_failures))
      echo "- **Trivy findings:** ${trivy_total} vulnerabilities"
    fi
    if [[ -f "${POC_REPORTS_DIR}/semgrep.json" ]]; then
      echo "- **Semgrep findings:** ${semgrep_issues} code security issues"
    fi
    echo ""
    echo "### 🔧 Tool Information"
    echo "- **Trivy**: Vulnerability and misconfiguration scanner"
    echo "- **Semgrep**: Enhanced CI integration with ${#SEMGREP_COMMUNITY_RULESETS[@]} community rulesets"
    echo ""
    echo "📊 SARIF reports uploaded to GitHub Security tab for detailed analysis."
  } >> "${POC_REPORTS_DIR}/github_summary.md"
}

#######################################
# Generate comprehensive POC summary report
# Globals:
#   PROJECT_ROOT, POC_REPORTS_DIR, SEMGREP_CONFIG, SEMGREP_COMMUNITY_RULESETS,
#   semgrep_logged_in, diff_aware_available, semgrep_ci_success,
#   trivy_duration, semgrep_duration, start_time
# Arguments:
#   None
# Outputs:
#   Comprehensive summary report to poc_summary.txt
#######################################
generate_summary_report() {
  local end_time total_duration
  end_time=$(date +%s)
  total_duration=$((end_time - start_time))

  # Generate comprehensive summary report header
  {
    echo "📋 POC Security Analysis Summary:"
    echo "================================="
    echo "Generated on: $(date)"
    echo "Tools: Trivy + Semgrep CI"
    echo "Project root: ${PROJECT_ROOT}"
    echo "Semgrep config: ${SEMGREP_CONFIG}"
    echo "Community rulesets: ${#SEMGREP_COMMUNITY_RULESETS[@]} total"
    echo "Authentication: $(
      [[ "${semgrep_logged_in}" == true ]] &&
      echo "✅ Authenticated" || echo "⚠️ Not authenticated"
    )"
    echo "Scan type: $(
      [[ "${diff_aware_available}" == true ]] &&
      echo "📊 Diff-aware available" || echo "📊 Full repository scan"
    )"
    echo "Semgrep CI: $(
      [[ "${semgrep_ci_success}" == true ]] &&
      echo "✅ Used semgrep ci" || echo "⚠️ Fallback to regular semgrep"
    )"
    echo ""
  } > "${POC_REPORTS_DIR}/poc_summary.txt"

  # Generate GitHub-compatible summary for PR comments
  {
    echo "## 🔒 POC Security Scan Results"
    echo ""
    echo "- **Semgrep Authentication:** $(
      [[ "${semgrep_logged_in}" == true ]] &&
      echo "✅ Authenticated (enhanced community rules)" ||
      echo "⚠️ Not authenticated (local rules used)"
    )"
    echo "- **Scan Type:** $(
      [[ "${diff_aware_available}" == true ]] &&
      echo "📊 Diff-aware scanning available" || echo "📊 Full repository scan"
    )"
    echo ""
  } > "${POC_REPORTS_DIR}/github_summary.md"

  # Add community rulesets used
  {
    echo "🔍 Semgrep Community Rulesets Used:"
    local ruleset
    for ruleset in "${SEMGREP_COMMUNITY_RULESETS[@]}"; do
      echo "  - ${ruleset}"
    done
    echo ""
  } >> "${POC_REPORTS_DIR}/poc_summary.txt"

  # Add performance metrics
  {
    echo "⏱️  Performance Metrics:"
    echo "  Trivy scan time: ${trivy_duration}s"
    echo "  Semgrep scan time: ${semgrep_duration}s"
    echo "  Total scan time: ${total_duration}s"
    echo ""
  } >> "${POC_REPORTS_DIR}/poc_summary.txt"

  # Count and add security issues
  count_security_issues

  # Add report structure information
  {
    echo ""
    echo "📁 POC Report Structure:"
    echo "  reports/security/poc/trivy_*.json      - Trivy scan results (JSON)"
    echo "  reports/security/poc/trivy.sarif       - Trivy SARIF for GitHub Security"
    echo "  reports/security/poc/semgrep.json      - Semgrep scan results (JSON)"
    echo "  reports/security/poc/semgrep.sarif     - Semgrep SARIF for GitHub Security"
    echo "  reports/security/poc/github_summary.md - GitHub-compatible summary for PR comments"
    echo "  reports/security/poc/poc_summary.txt   - This comprehensive summary file"
  } >> "${POC_REPORTS_DIR}/poc_summary.txt"

  # Print final status
  echo ""
  echo "✅ POC security analysis completed!"
  echo "📊 Performance: Trivy ${trivy_duration}s + Semgrep ${semgrep_duration}s = Total ${total_duration}s"
  echo "🔧 Semgrep method: $(
    [[ "${semgrep_ci_success}" == true ]] &&
    echo "semgrep ci (enhanced)" || echo "regular semgrep (fallback)"
  )"
  echo "🔐 Authentication: $(
    [[ "${semgrep_logged_in}" == true ]] &&
    echo "authenticated" || echo "not authenticated"
  )"
  echo "📋 See reports/security/poc/poc_summary.txt for detailed results"
}

#######################################
# Main function to orchestrate the POC security analysis
# Globals:
#   All script globals
# Arguments:
#   None
# Outputs:
#   Complete security analysis results
#######################################
main() {
  # Initialize environment and validate prerequisites
  initialize_environment

  # Check authentication and setup tokens
  check_semgrep_authentication

  # Build community configuration string
  local community_config
  community_config=$(build_community_config)

  # Run security scans
  run_trivy_scans
  run_semgrep_analysis "${community_config}"
  generate_semgrep_sarif "${community_config}"

  # Generate comprehensive summary report
  generate_summary_report
}

# Script entry point
main "$@"