#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Circuit Breaker functionality

This script demonstrates the circuit breaker pattern implementation
for protecting external API calls.
"""

import time
import requests
from circuit_breaker import (
    get_circuit_breaker,
    get_all_circuit_breakers,
    CircuitBreakerOpenException,
)


def test_circuit_breaker_basic():
    """Test basic circuit breaker functionality"""
    print("🧪 Testing Circuit Breaker Basic Functionality")
    print("=" * 50)

    # Get a circuit breaker
    cb = get_circuit_breaker("TEST_API")

    print(f"✅ Circuit breaker created: {cb.config.name}")
    print(f"   - State: {cb.state.value}")
    print(f"   - Failure threshold: {cb.config.failure_threshold}")
    print(f"   - Recovery timeout: {cb.config.recovery_timeout}s")

    # Test successful call
    try:
        with cb:
            print("   📡 Simulating successful API call...")
            # Simulate successful operation
            pass
        print("   ✅ Call succeeded, circuit remains CLOSED")
        print(f"   - State: {cb.state.value}")
        print(f"   - Failure count: {cb.failure_count}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    print()


def test_circuit_breaker_failure():
    """Test circuit breaker failure handling"""
    print("🧪 Testing Circuit Breaker Failure Handling")
    print("=" * 50)

    # Create a test circuit breaker with low threshold
    from circuit_breaker import CircuitBreakerConfig

    test_config = CircuitBreakerConfig(
        name="TEST_FAILURE_API",
        failure_threshold=2,  # Open after 2 failures
        recovery_timeout=5,  # Quick recovery for testing
        success_threshold=1,
    )
    cb = get_circuit_breaker("TEST_FAILURE_API", test_config)

    print("✅ Test circuit breaker created with low threshold")
    print(f"   - Failure threshold: {cb.config.failure_threshold}")
    print(f"   - Initial state: {cb.state.value}")

    # Simulate failures
    for i in range(3):
        try:
            with cb:
                print(f"   📡 Attempting call {i+1}...")
                raise requests.RequestException("Simulated network error")
        except CircuitBreakerOpenException:
            print(f"   🚫 Circuit breaker OPEN - failing fast on attempt {i+1}")
            break
        except Exception as e:
            print(f"   ❌ Call {i+1} failed: {e}")
            print(f"      State: {cb.state.value}, Failures: {cb.failure_count}")

    print(f"   📊 Final state: {cb.state.value}")
    print(f"   📊 Final failure count: {cb.failure_count}")

    # Wait for recovery timeout
    print(f"   ⏳ Waiting {cb.config.recovery_timeout} seconds for recovery...")
    time.sleep(cb.config.recovery_timeout + 1)

    # Test recovery
    try:
        with cb:
            print("   📡 Testing recovery - simulating successful call...")
            pass
        print("   ✅ Recovery successful, circuit CLOSED")
        print(f"      State: {cb.state.value}")
    except Exception as e:
        print(f"   ❌ Recovery failed: {e}")

    print()


def test_all_circuit_breakers():
    """Test getting status of all circuit breakers"""
    print("🧪 Testing Circuit Breaker Registry")
    print("=" * 50)

    all_cb = get_all_circuit_breakers()

    print(f"✅ Found {len(all_cb)} registered circuit breakers:")

    for name, cb in all_cb.items():
        print(f"   🔧 {name}:")
        print(f"      - State: {cb.state.value}")
        print(f"      - Failures: {cb.failure_count}")
        print(f"      - Threshold: {cb.config.failure_threshold}")
        print(f"      - Timeout: {cb.config.recovery_timeout}s")

    print()


def main():
    """Run all circuit breaker tests"""
    print("🚀 Circuit Breaker Test Suite")
    print("=" * 60)
    print()

    test_circuit_breaker_basic()
    test_circuit_breaker_failure()
    test_all_circuit_breakers()

    print("🎉 Circuit Breaker Tests Completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
