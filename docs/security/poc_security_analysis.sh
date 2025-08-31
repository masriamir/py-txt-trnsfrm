#!/bin/bash
# POC Security analysis script using Trivy + Semgrep
# This script demonstrates the proposed replacement for Snyk with open-source tools

echo "🔒 Running POC security analysis with Trivy + Semgrep..."

# Determine project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Create reports directory structure from project root
mkdir -p "$PROJECT_ROOT/reports/security/poc"

# Semgrep configuration file path
SEMGREP_CONFIG="$SCRIPT_DIR/semgrep-rules.yaml"

# Tool paths (adjust based on installation)
TRIVY_PATH="${TRIVY_PATH:-trivy}"
SEMGREP_PATH="${SEMGREP_PATH:-semgrep}"

# Start timing
start_time=$(date +%s)

# Change to project root for scans
cd "$PROJECT_ROOT"

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

# Try community rules first, fallback to local rules
$SEMGREP_PATH --config=p/security-audit --json --output="$PROJECT_ROOT/reports/security/poc/semgrep.json" . --disable-version-check 2>/dev/null || {
    echo "⚠️  Community rules failed, using local rules..."
    $SEMGREP_PATH --config="$SEMGREP_CONFIG" --json --output="$PROJECT_ROOT/reports/security/poc/semgrep.json" . --disable-version-check
}
semgrep_end=$(date +%s)
semgrep_duration=$((semgrep_end - semgrep_start))

# Run Semgrep with SARIF output for GitHub Security integration
echo "🔍 Generating Semgrep SARIF output..."
$SEMGREP_PATH --config="$SEMGREP_CONFIG" --sarif --output="$PROJECT_ROOT/reports/security/poc/semgrep.sarif" . --disable-version-check 2>/dev/null || {
    echo "⚠️  Semgrep SARIF generation failed"
}

# End timing
end_time=$(date +%s)
total_duration=$((end_time - start_time))

# Generate POC summary report
echo "📋 POC Security Analysis Summary:" > "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "=================================" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "Generated on: $(date)" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "Tools: Trivy + Semgrep" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "Project root: $PROJECT_ROOT" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "Semgrep config: $SEMGREP_CONFIG" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

# Performance metrics
echo "⏱️  Performance Metrics:" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  Trivy scan time: ${trivy_duration}s" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  Semgrep scan time: ${semgrep_duration}s" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  Total scan time: ${total_duration}s" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

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

echo "" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "📁 POC Report Structure:" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  reports/security/poc/trivy_*.json    - Trivy scan results (JSON)" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  reports/security/poc/trivy.sarif     - Trivy SARIF for GitHub Security" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  reports/security/poc/semgrep.json    - Semgrep scan results (JSON)" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  reports/security/poc/semgrep.sarif   - Semgrep SARIF for GitHub Security" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"
echo "  reports/security/poc/poc_summary.txt - This summary file" >> "$PROJECT_ROOT/reports/security/poc/poc_summary.txt"

echo ""
echo "✅ POC security analysis completed!"
echo "📊 Performance: Trivy ${trivy_duration}s + Semgrep ${semgrep_duration}s = Total ${total_duration}s"
echo "📋 See reports/security/poc/poc_summary.txt for detailed results"