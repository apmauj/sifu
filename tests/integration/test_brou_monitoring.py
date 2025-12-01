#!/usr/bin/env python3
"""
Script para probar el monitoreo BROU
"""

import requests
import json
from datetime import datetime


def test_brou_endpoint():
    print("=== Probando BROU endpoint ===")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/brou/current?full=true", timeout=10
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f'Success: {data.get("success")}')
            print(f'Message: {data.get("message")}')
            print(f'Data count: {len(data.get("data", []))}')
            print(f'Timestamp: {data.get("timestamp")}')
            print(f'Source: {data.get("source")}')
            print(f'Source type: {data.get("source_type")}')

            # Calcular edad si hay timestamp
            if data.get("timestamp"):
                timestamp = datetime.fromisoformat(
                    data["timestamp"].replace("Z", "+00:00")
                )
                age = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds() / 60
                print(f"Age: {age:.1f} minutes")
                return True
        else:
            print(f"Error response: {response.text}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health_endpoint():
    print()
    print("=== Probando health endpoint ===")
    try:
        response = requests.get("http://127.0.0.1:8000/api/health/advanced", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f'Overall status: {data.get("status")}')
            print(f'Total checks: {data.get("total_checks")}')

            # Buscar el check de BROU cache
            brou_checks = [
                check
                for check in data.get("checks", [])
                if check.get("name") == "brou_cache"
            ]
            if brou_checks:
                brou_check = brou_checks[0]
                print(f'BROU cache status: {brou_check.get("status")}')
                print(f'BROU cache message: {brou_check.get("message")}')
                print(
                    f'BROU cache details: {json.dumps(brou_check.get("details"), indent=2)}'
                )
                return True
            else:
                print("BROU cache check not found")
                return False

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    brou_ok = test_brou_endpoint()
    health_ok = test_health_endpoint()

    print()
    print("=== Resultado ===")
    print(f'BROU endpoint: {"✅ OK" if brou_ok else "❌ FAIL"}')
    print(f'Health endpoint: {"✅ OK" if health_ok else "❌ FAIL"}')
    print(f'Overall: {"✅ OK" if brou_ok and health_ok else "❌ FAIL"}')
