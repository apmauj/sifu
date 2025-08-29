#!/usr/bin/env python3
"""
Security validation script for SIFU API
Tests input validation, sanitization, and security measures
"""
import requests
import json
import time
from typing import Dict, List

class SecurityTester:
    """Test security measures of the SIFU API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_xss_protection(self) -> Dict[str, bool]:
        """Test XSS protection in various endpoints"""
        print("Testing XSS protection...")

        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
        ]

        results = {}

        # Test UR range endpoint
        for payload in xss_payloads:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/ur/range",
                    json={"start_year": payload, "start_month": 1, "end_year": 2024, "end_month": 12}
                )
                # Check if payload was sanitized/escaped
                if payload in response.text:
                    results[f"UR XSS {payload[:20]}..."] = False
                else:
                    results[f"UR XSS {payload[:20]}..."] = True
            except:
                results[f"UR XSS {payload[:20]}..."] = False

        return results

    def test_sql_injection_protection(self) -> Dict[str, bool]:
        """Test SQL injection protection"""
        print("Testing SQL injection protection...")

        sql_payloads = [
            "'; DROP TABLE users; --",
            "1; SELECT * FROM users;",
            "UNION SELECT password FROM admin",
        ]

        results = {}

        # Test various endpoints
        endpoints = [
            ("/api/ur/year/{}", "path"),
            ("/api/exchange-rate/currency/{}", "path"),
        ]

        for endpoint_template, param_type in endpoints:
            for payload in sql_payloads:
                try:
                    if param_type == "path":
                        url = f"{self.base_url}{endpoint_template.format(payload)}"
                        response = self.session.get(url)
                    else:
                        response = self.session.get(f"{self.base_url}{endpoint_template}", params={"q": payload})

                    # Check if injection succeeded (would return error or unexpected data)
                    if response.status_code in [400, 422, 500]:
                        results[f"SQL Injection {payload[:20]}..."] = True
                    else:
                        results[f"SQL Injection {payload[:20]}..."] = False
                except:
                    results[f"SQL Injection {payload[:20]}..."] = True

        return results

    def test_rate_limiting(self) -> Dict[str, bool]:
        """Test rate limiting functionality"""
        print("Testing rate limiting...")

        results = {}

        # Test general rate limiting
        try:
            responses = []
            for i in range(25):  # Exceed burst limit
                response = self.session.get(f"{self.base_url}/api/health")
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay

            # Check if we got rate limited (429)
            if 429 in responses:
                results["General Rate Limiting"] = True
            else:
                results["General Rate Limiting"] = False
        except:
            results["General Rate Limiting"] = False

        # Test endpoint-specific rate limiting
        try:
            responses = []
            for i in range(10):
                response = self.session.post(f"{self.base_url}/api/refresh")
                responses.append(response.status_code)
                time.sleep(0.1)

            if 429 in responses:
                results["Endpoint Rate Limiting"] = True
            else:
                results["Endpoint Rate Limiting"] = False
        except:
            results["Endpoint Rate Limiting"] = False

        return results

    def test_input_validation(self) -> Dict[str, bool]:
        """Test input validation"""
        print("Testing input validation...")

        results = {}

        # Test invalid date formats
        try:
            response = self.session.get(f"{self.base_url}/api/ui/invalid-date")
            if response.status_code == 422:  # Pydantic validation error
                results["Date Validation"] = True
            else:
                results["Date Validation"] = False
        except:
            results["Date Validation"] = False

        # Test invalid currency codes
        try:
            response = self.session.get(f"{self.base_url}/api/exchange-rate/currency/INVALID")
            if response.status_code == 400:
                results["Currency Validation"] = True
            else:
                results["Currency Validation"] = False
        except:
            results["Currency Validation"] = False

        # Test invalid month values
        try:
            response = self.session.post(
                f"{self.base_url}/api/ur/range",
                json={"start_year": 2024, "start_month": 13, "end_year": 2024, "end_month": 12}
            )
            if response.status_code in [400, 422]:
                results["Month Validation"] = True
            else:
                results["Month Validation"] = False
        except:
            results["Month Validation"] = False

        return results

    def test_cors_configuration(self) -> Dict[str, any]:
        """Test CORS configuration"""
        print("Testing CORS configuration...")

        results = {}

        try:
            # Test preflight request
            response = self.session.options(
                f"{self.base_url}/api/health",
                headers={
                    "Origin": "https://malicious-site.com",
                    "Access-Control-Request-Method": "GET"
                }
            )

            cors_headers = {
                "allow_origin": response.headers.get("Access-Control-Allow-Origin"),
                "allow_methods": response.headers.get("Access-Control-Allow-Methods"),
                "allow_headers": response.headers.get("Access-Control-Allow-Headers"),
            }

            results["CORS Headers"] = cors_headers

            # Check if wildcard is used (security risk)
            if cors_headers.get("allow_origin") == "*":
                results["CORS Security"] = False
            else:
                results["CORS Security"] = True

        except Exception as e:
            results["CORS Error"] = str(e)
            results["CORS Security"] = False

        return results

    def run_all_tests(self) -> Dict[str, Dict]:
        """Run all security tests"""
        print("Running comprehensive security tests...\n")

        results = {
            "XSS Protection": self.test_xss_protection(),
            "SQL Injection Protection": self.test_sql_injection_protection(),
            "Rate Limiting": self.test_rate_limiting(),
            "Input Validation": self.test_input_validation(),
            "CORS Configuration": self.test_cors_configuration(),
        }

        return results

    def print_report(self, results: Dict[str, Dict]):
        """Print test results report"""
        print("\n" + "="*60)
        print("SECURITY TEST REPORT")
        print("="*60)

        total_tests = 0
        passed_tests = 0

        for category, tests in results.items():
            print(f"\n{category}:")
            print("-" * len(category))

            for test_name, result in tests.items():
                status = "✅ PASS" if result else "❌ FAIL"
                if isinstance(result, dict):
                    status = "ℹ️  INFO"
                    print(f"  {test_name}: {status}")
                    for key, value in result.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"  {test_name}: {status}")
                    total_tests += 1
                    if result:
                        passed_tests += 1

        print(f"\n{'='*60}")
        print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        if passed_tests == total_tests:
            print("🎉 All security tests passed!")
        else:
            print("⚠️  Some security issues detected. Review failed tests.")
        print("="*60)

def main():
    """Main function"""
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing security of SIFU API at {base_url}")
    print("Make sure the API is running before running this test.\n")

    tester = SecurityTester(base_url)
    results = tester.run_all_tests()
    tester.print_report(results)

if __name__ == "__main__":
    main()
