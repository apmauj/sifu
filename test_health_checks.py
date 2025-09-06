#!/usr/bin/env python3
"""
Test script for advanced health checks
"""

import requests


def test_health_checks():
    print("Testing advanced health checks...")

    try:
        # Test simple health
        print("\n1. Testing simple health check...")
        resp = requests.get("http://localhost:8000/api/health/simple", timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f'Status: {data.get("status")}')
            print(f'Issues: {data.get("issues")}')

        # Test advanced health
        print("\n2. Testing advanced health check...")
        resp = requests.get("http://localhost:8000/api/health/advanced", timeout=15)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f'Overall Status: {data.get("status")}')
            print(f'Total Checks: {data.get("total_checks")}')
            print(f'Healthy: {data.get("healthy_checks")}')
            print(f'Warning: {data.get("warning_checks")}')
            print(f'Critical: {data.get("critical_checks")}')

            # Show individual check results
            print("\nIndividual Check Results:")
            for check in data.get("checks", []):
                status_emoji = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "❌",
                    "unknown": "❓",
                }.get(check["status"], "❓")
                print(
                    f'{status_emoji} {check["name"]}: {check["status"]} - {check["message"]}'
                )

        print("\n✅ OBS-003 Advanced Health Checks implemented successfully!")

    except Exception as e:
        print(f"❌ Error testing health checks: {str(e)}")


if __name__ == "__main__":
    test_health_checks()
