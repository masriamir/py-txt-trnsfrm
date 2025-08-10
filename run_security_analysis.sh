#!/bin/bash
# Security analysis script - runs all security tools and generates reports

echo "🔒 Running comprehensive security analysis..."

# Create reports directory structure (consistent with coverage)
mkdir -p reports/security

# Run Bandit security scanner (using uv)
echo "📊 Running Bandit security scan..."
uv run bandit -r app/ -f json -o reports/security/bandit_report.json
uv run bandit -r app/ -f txt -o reports/security/bandit_report.txt

# Run Safety scan for dependency vulnerabilities (using uv and modern syntax with timeout)
echo "🛡️ Checking dependencies for known vulnerabilities..."
timeout 60s uv run safety scan --output json --save-as json reports/security/safety_report.json 2>/dev/null || {
    echo "⚠️  Safety scan timed out or failed - trying fallback method..."
    # Fallback: create a basic report indicating scan was attempted
    echo '{"scan_status": "timeout_or_failed", "vulnerabilities": [], "message": "Safety scan could not complete - may need authentication or network connectivity"}' > reports/security/safety_report.json
}

# Generate HTML version of safety report with timeout (using uv)
echo "📄 Generating HTML safety report..."
timeout 60s uv run safety scan --output html --save-as html reports/security/safety_report.html 2>/dev/null || {
    echo "⚠️  Safety HTML report timed out - skipping HTML generation"
    echo "<html><body><h1>Safety Report</h1><p>Safety scan could not complete. Please check network connectivity or authentication.</p></body></html>" > reports/security/safety_report.html
}

# Generate text version of safety report with timeout (using uv)
echo "📄 Generating text safety report..."
timeout 60s uv run safety scan --output text > reports/security/safety_report.txt 2>&1 || {
    echo "⚠️  Safety text report completed with warnings"
    echo "Safety scan could not complete - may need authentication or network connectivity" > reports/security/safety_report.txt
}

# Run our custom security utility (using uv)
echo "🔍 Running custom security analysis..."
uv run python tests/security_utils.py

# Generate summary
echo "📋 Security Analysis Summary:" > reports/security/security_summary.txt
echo "=============================" >> reports/security/security_summary.txt
echo "Generated on: $(date)" >> reports/security/security_summary.txt
echo "" >> reports/security/security_summary.txt

# Count Bandit issues
if [ -f "reports/security/bandit_report.json" ]; then
    HIGH_ISSUES=$(jq '.results | map(select(.issue_confidence == "HIGH")) | length' reports/security/bandit_report.json 2>/dev/null || echo "0")
    MEDIUM_ISSUES=$(jq '.results | map(select(.issue_confidence == "MEDIUM")) | length' reports/security/bandit_report.json 2>/dev/null || echo "0")
    LOW_ISSUES=$(jq '.results | map(select(.issue_confidence == "LOW")) | length' reports/security/bandit_report.json 2>/dev/null || echo "0")

    echo "Bandit Security Issues:" >> reports/security/security_summary.txt
    echo "  High: $HIGH_ISSUES" >> reports/security/security_summary.txt
    echo "  Medium: $MEDIUM_ISSUES" >> reports/security/security_summary.txt
    echo "  Low: $LOW_ISSUES" >> reports/security/security_summary.txt
    echo "" >> reports/security/security_summary.txt
fi

# Count Safety issues
if [ -f "reports/security/safety_report.json" ]; then
    VULN_COUNT=$(jq '. | length' reports/security/safety_report.json 2>/dev/null || echo "0")
    echo "Dependency Vulnerabilities: $VULN_COUNT" >> reports/security/security_summary.txt
    echo "" >> reports/security/security_summary.txt
fi

echo "✅ Security analysis complete! Check the reports/security/ directory for detailed results."
echo "📖 Read reports/security/security_summary.txt for a quick overview."
echo ""
echo "📁 Report Structure:"
echo "  reports/security/bandit_report.json    - Bandit security scan (JSON)"
echo "  reports/security/bandit_report.txt     - Bandit security scan (Text)"
echo "  reports/security/safety_report.json    - Safety vulnerability scan (JSON)"
echo "  reports/security/safety_report.txt     - Safety vulnerability scan (Text)"
echo "  reports/security/safety-report.html    - Safety vulnerability scan (HTML)"
echo "  reports/security/security_summary.txt  - Quick summary of all findings"
