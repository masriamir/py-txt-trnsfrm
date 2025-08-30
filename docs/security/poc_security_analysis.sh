#!/bin/bash
# POC Security analysis script using Trivy + Semgrep
# This script demonstrates the proposed replacement for Snyk with open-source tools

echo "🔒 Running POC security analysis with Trivy + Semgrep..."

# Create reports directory structure
mkdir -p reports/security/poc

# Tool paths (adjust based on installation)
TRIVY_PATH="${TRIVY_PATH:-trivy}"
SEMGREP_PATH="${SEMGREP_PATH:-semgrep}"

# Start timing
start_time=$(date +%s)

# Run Trivy filesystem scan for dependencies and config
echo "📊 Running Trivy filesystem scan..."
trivy_start=$(date +%s)
$TRIVY_PATH fs --format json --output reports/security/poc/trivy_fs.json . 2>/dev/null || {
    echo "⚠️  Trivy filesystem scan failed - trying config scan only..."
    $TRIVY_PATH config --format json --output reports/security/poc/trivy_config.json .
}
trivy_end=$(date +%s)
trivy_duration=$((trivy_end - trivy_start))

# Run Trivy SARIF output for GitHub Security integration
echo "📊 Generating Trivy SARIF output..."
$TRIVY_PATH config --format sarif --output reports/security/poc/trivy.sarif . 2>/dev/null || {
    echo "⚠️  Trivy SARIF generation failed"
}

# Run Semgrep code analysis
echo "🔍 Running Semgrep code analysis..."
semgrep_start=$(date +%s)

# Try community rules first, fallback to local rules
$SEMGREP_PATH --config=p/security-audit --json --output=reports/security/poc/semgrep.json . --disable-version-check 2>/dev/null || {
    echo "⚠️  Community rules failed, using local rules..."
    
    # Create minimal local rules if needed
    cat > /tmp/semgrep_rules.yaml << 'EOF'
rules:
  - id: hardcoded-secret
    pattern: SECRET_KEY = "..."
    message: Hardcoded secret key found
    languages: [python]
    severity: WARNING
    
  - id: flask-debug-enabled
    pattern: app.run(debug=True)
    message: Flask debug mode enabled
    languages: [python]
    severity: ERROR
EOF
    
    $SEMGREP_PATH --config=/tmp/semgrep_rules.yaml --json --output=reports/security/poc/semgrep.json . --disable-version-check
}
semgrep_end=$(date +%s)
semgrep_duration=$((semgrep_end - semgrep_start))

# Run Semgrep with SARIF output for GitHub Security integration
echo "🔍 Generating Semgrep SARIF output..."
$SEMGREP_PATH --config=/tmp/semgrep_rules.yaml --sarif --output=reports/security/poc/semgrep.sarif . --disable-version-check 2>/dev/null || {
    echo "⚠️  Semgrep SARIF generation failed"
}

# End timing
end_time=$(date +%s)
total_duration=$((end_time - start_time))

# Generate POC summary report
echo "📋 POC Security Analysis Summary:" > reports/security/poc/poc_summary.txt
echo "=================================" >> reports/security/poc/poc_summary.txt
echo "Generated on: $(date)" >> reports/security/poc/poc_summary.txt
echo "Tools: Trivy + Semgrep" >> reports/security/poc/poc_summary.txt
echo "" >> reports/security/poc/poc_summary.txt

# Performance metrics
echo "⏱️  Performance Metrics:" >> reports/security/poc/poc_summary.txt
echo "  Trivy scan time: ${trivy_duration}s" >> reports/security/poc/poc_summary.txt
echo "  Semgrep scan time: ${semgrep_duration}s" >> reports/security/poc/poc_summary.txt
echo "  Total scan time: ${total_duration}s" >> reports/security/poc/poc_summary.txt
echo "" >> reports/security/poc/poc_summary.txt

# Count issues from JSON reports
if [ -f "reports/security/poc/trivy_fs.json" ]; then
    TRIVY_ISSUES=$(jq '.Results[]?.Vulnerabilities // [] | length' reports/security/poc/trivy_fs.json 2>/dev/null | awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Issues Found: $TRIVY_ISSUES" >> reports/security/poc/poc_summary.txt
elif [ -f "reports/security/poc/trivy_config.json" ]; then
    TRIVY_FAILURES=$(jq '.Results[]?.MisconfSummary?.Failures // 0' reports/security/poc/trivy_config.json 2>/dev/null | awk '{s+=$1} END {print s+0}')
    echo "🔍 Trivy Config Issues: $TRIVY_FAILURES" >> reports/security/poc/poc_summary.txt
fi

if [ -f "reports/security/poc/semgrep.json" ]; then
    SEMGREP_ISSUES=$(jq '.results | length' reports/security/poc/semgrep.json 2>/dev/null || echo "0")
    echo "🔍 Semgrep Issues Found: $SEMGREP_ISSUES" >> reports/security/poc/semgrep.json
fi

echo "" >> reports/security/poc/poc_summary.txt
echo "📁 POC Report Structure:" >> reports/security/poc/poc_summary.txt
echo "  reports/security/poc/trivy_*.json    - Trivy scan results (JSON)" >> reports/security/poc/poc_summary.txt
echo "  reports/security/poc/trivy.sarif     - Trivy SARIF for GitHub Security" >> reports/security/poc/poc_summary.txt
echo "  reports/security/poc/semgrep.json    - Semgrep scan results (JSON)" >> reports/security/poc/poc_summary.txt
echo "  reports/security/poc/semgrep.sarif   - Semgrep SARIF for GitHub Security" >> reports/security/poc/poc_summary.txt
echo "  reports/security/poc/poc_summary.txt - This summary file" >> reports/security/poc/poc_summary.txt

echo ""
echo "✅ POC security analysis completed!"
echo "📊 Performance: Trivy ${trivy_duration}s + Semgrep ${semgrep_duration}s = Total ${total_duration}s"
echo "📋 See reports/security/poc/poc_summary.txt for detailed results"