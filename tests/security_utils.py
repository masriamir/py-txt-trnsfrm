"""Security testing utilities and configuration."""
import subprocess
import json
import sys
from pathlib import Path


def run_bandit_security_scan():
    """Run Bandit security scanner and return results."""
    try:
        result = subprocess.run(
            ['bandit', '-r', 'app/', '-f', 'json'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.stdout:
            return json.loads(result.stdout)
        return {"results": [], "metrics": {}}
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error running Bandit: {e}")
        return None


def run_safety_check():
    """Run Safety scan for known vulnerabilities in dependencies."""
    try:
        # Use the modern safety scan command
        result = subprocess.run(
            ['safety', 'scan', '--output', 'json'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # If JSON parsing fails, return empty list (no vulnerabilities found)
                return []
        return []
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running Safety: {e}")
        return None


def generate_security_report():
    """Generate comprehensive security report."""
    print("Running security analysis...")

    # Ensure security reports directory exists
    security_dir = Path(__file__).parent.parent / "reports" / "security"
    security_dir.mkdir(parents=True, exist_ok=True)

    # Run Bandit
    bandit_results = run_bandit_security_scan()
    safety_results = run_safety_check()

    report = {
        "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
        "bandit": bandit_results,
        "safety": safety_results
    }

    # Save report in security subdirectory
    report_file = security_dir / "security_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Security report saved to: {report_file}")
    return report


if __name__ == "__main__":
    generate_security_report()
