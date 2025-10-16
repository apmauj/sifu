#!/usr/bin/env python3
"""
Test run_all_checks function
"""

print("Testing run_all_checks()...")
try:
    from src.infrastructure.health_checks import health_checker

    result = health_checker.run_all_checks()
    print("✅ run_all_checks() completed successfully")
    print("Status:", result["status"])
    print("Total checks:", result["total_checks"])
    print("Healthy:", result["healthy_checks"])
    print("Critical:", result["critical_checks"])
    print("Warning:", result["warning_checks"])
except Exception as e:
    print("❌ run_all_checks() error:", e)
    import traceback

    traceback.print_exc()
