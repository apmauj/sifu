#!/usr/bin/env python3
from health_checks import health_checker

print("Testing run_all_checks...")
try:
    result = health_checker.run_all_checks()
    print("✅ run_all_checks successful")
    print("Status:", result["status"])
    print("Total checks:", result["total_checks"])
    print("Healthy:", result["healthy_checks"])
    print("Critical:", result["critical_checks"])
except Exception as e:
    print("❌ run_all_checks error:", e)
    import traceback

    traceback.print_exc()
