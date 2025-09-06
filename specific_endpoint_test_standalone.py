#!/usr/bin/env python
import requests
import time


def test_specific_endpoint(url, description):
    try:
        print(f"Testing {description}...")
        start_time = time.time()
        response = requests.get(
            url,
            headers={"Origin": "https://edition-snake-rehab-ca.trycloudflare.com"},
            timeout=5,
        )  # Shorter timeout
        elapsed = time.time() - start_time
        print(f"✅ {description}: {response.status_code} ({elapsed:.2f}s)")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ {description}: TIMEOUT (5s)")
        return False
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return False


def main():
    base_url = "http://localhost:8000"

    # Test just the problematic endpoints
    endpoints = [
        (f"{base_url}/api/performance/budgets/status", "Performance Budget Status"),
        (f"{base_url}/api/performance/throughput", "Throughput Metrics"),
        (f"{base_url}/api/health/simple", "Simple Health Check"),
    ]

    print("🔍 Testing specific problematic endpoints...\n")

    for url, description in endpoints:
        if not test_specific_endpoint(url, description):
            print("   This endpoint is still timing out!")
        print()


if __name__ == "__main__":
    main()
