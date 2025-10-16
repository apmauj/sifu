#!/usr/bin/env python3
"""
Simple test for health checks
"""

try:
    from src.infrastructure.health_checks import health_checker

    print("Import successful")
    result = health_checker.run_all_checks()
    print("Execution successful")
    print("Status:", result["status"])
    print("Total checks:", result["total_checks"])
except Exception as e:
    print("Error:", e)
    import traceback

    traceback.print_exc()
