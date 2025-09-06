#!/usr/bin/env python
import requests
import time
import sys


def test_endpoint(url, description):
    try:
        print(f"Testing {description}...")
        response = requests.get(
            url,
            headers={"Origin": "https://edition-snake-rehab-ca.trycloudflare.com"},
            timeout=10,
        )
        print(f"✅ {description}: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
            return True
        else:
            print(f"   ❌ Status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ {description}: TIMEOUT (10s)")
        return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False


def main():
    base_url = "http://localhost:8000"

    endpoints = [
        (f"{base_url}/api/health/advanced", "Advanced Health Check"),
        (f"{base_url}/api/performance/budgets", "Performance Budgets"),
        (f"{base_url}/api/performance/budgets/status", "Performance Budget Status"),
        (f"{base_url}/api/performance/throughput", "Throughput Metrics"),
        (f"{base_url}/api/health", "Basic Health Check"),
    ]

    print("🚀 Testing API endpoints...\n")

    success_count = 0
    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1
        print()
        time.sleep(0.5)  # Small delay between requests

    print(f"📊 Results: {success_count}/{len(endpoints)} endpoints working")

    if success_count == len(endpoints):
        print("🎉 All endpoints are working correctly!")
        sys.exit(0)
    else:
        print("⚠️ Some endpoints failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
