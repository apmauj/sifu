#!/usr/bin/env python3
from fastapi import FastAPI
from health_checks import health_checker

app = FastAPI()


@app.get("/test")
async def test():
    return {"message": "Test endpoint working"}


@app.get("/api/health/simple")
async def health():
    # Use synchronous call
    results = health_checker.run_all_checks()
    is_healthy = results["status"] != "critical"
    return {
        "status": "OK" if is_healthy else "FAIL",
        "timestamp": results["timestamp"],
        "checks": results["total_checks"],
        "issues": results["critical_checks"] + results["warning_checks"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
