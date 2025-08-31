#!/bin/bash
# POC Security analysis script using Trivy + Semgrep
# This script demonstrates the proposed replacement for Snyk with open-source tools
# Uses semgrep ci for proper CI/CD integration and community ruleset access

echo "🔒 Running POC security analysis with Trivy + Semgrep..."

# Determine project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Create reports directory structure from project root
mkdir -p "$PROJECT_ROOT/reports/security/poc"

# Semgrep configuration file path
SEMGREP_CONFIG="$SCRIPT_DIR/semgrep-rules.yaml"

# Community rulesets to use (from https://semgrep.dev/r)
SEMGREP_COMMUNITY_RULESETS=(
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

# Environment variables for Semgrep CI
export SEMGREP_REPO_NAME="${SEMGREP_REPO_NAME:-py-txt-trnsfrm}"
export SEMGREP_BRANCH="${SEMGREP_BRANCH:-main}"
export SEMGREP_JOB_URL="${SEMGREP_JOB_URL:-local}"
export SEMGREP_COMMIT="${SEMGREP_COMMIT:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
export SEMGREP_REPO_URL="${SEMGREP_REPO_URL:-https://github.com/masriamir/py-txt-trnsfrm}"

# Check if we're in a git repository for diff-aware scanning
if git rev-parse --git-dir > /dev/null 2>&1; then
    export SEMGREP_BASELINE_REF="${SEMGREP_BASELINE_REF:-main}"
    DIFF_AWARE_AVAILABLE=true
else
    DIFF_AWARE_AVAILABLE=false
fi

# Tool paths (adjust based on installation)
TRIVY_PATH="${TRIVY_PATH:-trivy}"
SEMGREP_PATH="${SEMGREP_PATH:-semgrep}"

# Start timing
start_time=$(date +%s)

# Change to project root for scans
cd "$PROJECT_ROOT" || exit 1

# Run Trivy filesystem scan for dependencies and config
echo "📊 Running Trivy filesystem scan..."
trivy_start=$(date +%s)
$TRIVY_PATH fs --format json --output "$PROJECT_ROOT/reports/security/poc/trivy_fs.json" . 2>/dev/null || {
    echo "⚠️  Trivy filesystem scan failed - trying config scan only..."
    $TRIVY_PATH config --format json --output "$PROJECT_ROOT/reports/security/poc/trivy_config.json" .
}
trivy_end=$(date +%s)
trivy_duration=$((trivy_end - trivy_start))

# Run Trivy SARIF output for GitHub Security integration
echo "📊 Generating Trivy SARIF output..."
$TRIVY_PATH config --format sarif --output "$PROJECT_ROOT/reports/security/poc/trivy.sarif" . 2>/dev/null || {
    echo "⚠️  Trivy SARIF generation failed"
}

# Run Semgrep code analysis
echo "🔍 Running Semgrep code analysis..."
semgrep_start=$(date +%s)

# Check if Semgrep config file exists
if [ ! -f "$SEMGREP_CONFIG" ]; then
    echo "❌ Semgrep config file not found: $SEMGREP_CONFIG"
    exit 1
fi

# Check Semgrep authentication status
echo "🔐 Checking Semgrep authentication status..."
SEMGREP_LOGGED_IN=false

# Check for Semgrep settings file which indicates authentication
if [ -f "$HOME/.semgrep/settings.yml" ]; then
    # Verify the settings file contains authentication token
    if grep -q "api_token" "$HOME/.semgrep/settings.yml" 2>/dev/null; then
        echo "✅ Semgrep authenticated - using community rulesets with semgrep ci"
        SEMGREP_LOGGED_IN=true
        # Export token from settings file for semgrep ci
        if [ -z "$SEMGREP_APP_TOKEN" ]; then
            SEMGREP_APP_TOKEN=$(grep "api_token:" "$HOME/.semgrep/settings.yml" | cut -d'"' -f2 2>/dev/null || true)
            export SEMGREP_APP_TOKEN
        fi
    fi
fi

if [ "$SEMGREP_LOGGED_IN" = false ]; then
    echo "⚠️  Semgrep not logged in - some community rules may be limited"
    echo "💡 To login: semgrep login (for full access to community rules)"
    echo "💡 For CI/CD: Set SEMGREP_APP_TOKEN environment variable"
fi

# Build community rulesets configuration
COMMUNITY_CONFIG=""
for ruleset in "${SEMGREP_COMMUNITY_RULESETS[@]}"; do
    if [ -z "$COMMUNITY_CONFIG" ]; then
        COMMUNITY_CONFIG="$ruleset"
    else
        COMMUNITY_CONFIG="$COMMUNITY_CONFIG,$ruleset"
    fi
done

echo "🔍 Using community rulesets: $COMMUNITY_CONFIG"
echo "📋 Total rulesets: ${#SEMGREP_COMMUNITY_RULESETS[@]}"

if [ "$DIFF_AWARE_AVAILABLE" = true ]; then
    echo "📊 Git repository detected - diff-aware scanning available"
else
    echo "📊 Full repository scan (no git repository detected)"
fi

# Try semgrep ci first (recommended for CI/CD), fallback to regular semgrep
if [ "$SEMGREP_LOGGED_IN" = true ]; then
    echo "🚀 Running semgrep ci for enhanced integration..."
    
    # Use semgrep ci with community rulesets
    if semgrep ci --config="$COMMUNITY_CONFIG" --json --output="$PROJECT_ROOT/reports/security/poc/semgrep.json" --disable-version-check 2>/dev/null; then
        echo "✅ Semgrep CI scan completed successfully"
        SEMGREP_CI_SUCCESS=true
    else
        echo "⚠️  Semgrep CI failed, trying regular semgrep with community rules..."
        SEMGREP_CI_SUCCESS=false
    fi
else
    echo "⚠️  No authentication - using regular semgrep command"
    SEMGREP_CI_SUCCESS=false
fi

# Fallback to regular semgrep if semgrep ci failed or no auth
if [ "$SEMGREP_CI_SUCCESS" != true ]; then
    echo "🔄 Falling back to regular semgrep command..."
    $SEMGREP_PATH --config="$COMMUNITY_CONFIG" --json --output="$PROJECT_ROOT/reports/security/poc/semgrep.json" . --disable-version-check 2>/dev/null || {
        echo "⚠️  Community rules failed, using local rules..."
        $SEMGREP_PATH --config="$SEMGREP_CONFIG" --json --output="$PROJECT_ROOT/reports/security/poc/semgrep.json" . --disable-version-check
    }
fi

semgrep_end=$(date +%s)
semgrep_duration=$((semgrep_end - semgrep_start))

# Run Semgrep with SARIF output for GitHub Security integration
echo "🔍 Generating Semgrep SARIF output..."

if [ "$SEMGREP_LOGGED_IN" = true ]; then
    # Try semgrep ci for SARIF (automatically uploads if configured)
    if ! semgrep ci --config="$COMMUNITY_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" --disable-version-check 2>/dev/null; then
        echo "⚠️  Semgrep CI SARIF failed, trying regular semgrep..."
        $SEMGREP_PATH --config="$COMMUNITY_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" . --disable-version-check 2>/dev/null || {
            echo "⚠️  Community rules SARIF failed, trying local rules..."
            $SEMGREP_PATH --config="$SEMGREP_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" . --disable-version-check 2>/dev/null || {
                echo "⚠️  Semgrep SARIF generation failed"
            }
        }
    fi
else
    # No authentication - use regular semgrep
    $SEMGREP_PATH --config="$COMMUNITY_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" . --disable-version-check 2>/dev/null || {
        echo "⚠️  Community rules SARIF failed, trying local rules..."
        $SEMGREP_PATH --config="$SEMGREP_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" . --disable-version-check 2>/dev/null || {
            echo "⚠️  Semgrep SARIF generation failed"
        }
    }
fi

# End timing
end_time=$(date +%s)
total_duration=$((end_time - start_time))

# Generate POC summary report
{
    echo "📋 POC Security Analysis Summary:"
    echo "================================="
    echo "Generated on: $(date)"
    echo "Tools: Trivy + Semgrep CI"
    echo "Project root: $PROJECT_ROOT"
    echo "Semgrep config: $SEMGREP_CONFIG"
    echo "Community rulesets: ${#SEMGREP_COMMUNITY_RULESETS[@]} total"
    echo "Authentication: $( [ "$SEMGREP_LOGGED_IN" = true ] && echo "✅ Authenticated" || echo "⚠️ Not authenticated" )"
    echo "Scan type: $( [ "$DIFF_AWARE_AVAILABLE" = true ] && echo "📊 Diff-aware available" || echo "📊 Full repository scan" )"
    echo "Semgrep CI: $( [ "$SEMGREP_CI_SUCCESS" = true ] && echo "✅ Used semgrep ci" || echo "⚠️ Fallback to regular semgrep" )"
    echo ""
} > "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
{
    echo "🔍 Semgrep Community Rulesets Used:"
    for ruleset in "${SEMGREP_COMMUNITY_RULESETS[@]}"; do
        echo "  - $ruleset"
    done
    echo ""
} >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

# Performance metrics
{
    echo "⏱️  Performance Metrics:"
    echo "  Trivy scan time: ${trivy_duration}s"
    echo "  Semgrep scan time: ${semgrep_duration}s"
    echo "  Total scan time: ${total_duration}s"
    echo ""
} >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

# Count issues from JSON reports
if [ -f "$PROJECT_ROOT/reports/security/poc/trivy_fs.json" ]; then
    TRIVY_ISSUES=$(jq '.Results[]?.Vulnerabilities // [] | length' "$PROJECT_ROOT/reports/security/poc/trivy_fs.json" 2>/dev/null | awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Issues Found: $TRIVY_ISSUES" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
elif [ -f "$PROJECT_ROOT/reports/security/poc/trivy_config.json" ]; then
    TRIVY_FAILURES=$(jq '.Results[]?.MisconfSummary?.Failures // 0' "$PROJECT_ROOT/reports/security/poc/trivy_config.json" 2>/dev/null | awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Config Issues: $TRIVY_FAILURES" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
fi

if [ -f "$PROJECT_ROOT/reports/security/poc/semgrep.json" ]; then
    SEMGREP_ISSUES=$(jq '.results | length' "$PROJECT_ROOT/reports/security/poc/semgrep.json" 2>/dev/null || echo "0")
    echo "🔍 Semgrep Issues Found: $SEMGREP_ISSUES" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
fi

{
    echo ""
    echo "📁 POC Report Structure:"
    echo "  reports/security/poc/trivy_*.json    - Trivy scan results (JSON)"
    echo "  reports/security/poc/trivy.sarif     - Trivy SARIF for GitHub Security"
    echo "  reports/security/poc/semgrep.json    - Semgrep scan results (JSON)"
    echo "  reports/security/poc/semgrep.sarif   - Semgrep SARIF for GitHub Security"
    echo "  reports/security/poc/poc_summary.txt - This summary file"
} >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

echo ""
echo "✅ POC security analysis completed!"
echo "📊 Performance: Trivy ${trivy_duration}s + Semgrep ${semgrep_duration}s = Total ${total_duration}s"
echo "🔧 Semgrep method: $( [ "$SEMGREP_CI_SUCCESS" = true ] && echo "semgrep ci (enhanced)" || echo "regular semgrep (fallback)" )"
echo "🔐 Authentication: $( [ "$SEMGREP_LOGGED_IN" = true ] && echo "authenticated" || echo "not authenticated" )"
echo "📋 See reports/security/poc/poc_summary.txt for detailed results"