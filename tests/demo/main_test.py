#!/usr/bin/env python3
"""
Simplified main.py for testing health checks
"""

from fastapi import FastAPI
from datetime import datetime

# Import health check functions
from src.infrastructure.health_checks import get_simple_health, get_advanced_health

# Create FastAPI application
app = FastAPI(
    title="SIFU Test", description="Test application for health checks", version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "SIFU Test Server", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/health/simple")
async def simple_health():
    """Simple health check"""
    return await get_simple_health()


@app.get("/api/health/advanced")
async def advanced_health(force_refresh: bool = False):
    """Advanced health check"""
    return await get_advanced_health(force_refresh=force_refresh)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
