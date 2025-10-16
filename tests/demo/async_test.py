#!/usr/bin/env python3
"""
Test async health check functions
"""

import asyncio


async def test():
    try:
        from src.infrastructure.health_checks import get_simple_health

        result = await get_simple_health()
        print("✅ Async health check successful")
        print("Result:", result)
    except Exception as e:
        print("❌ Error in async health check:", e)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
