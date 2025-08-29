"""
Rate limiting middleware for FastAPI
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""

    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.requests: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP (in production, use a proper method to get real IP)
        client_ip = self._get_client_ip(request)

        # Clean old requests
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60  # Keep only requests from last minute
        ]

        # Check rate limits
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Check burst limit (requests in last 10 seconds)
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 10
        ]
        if len(recent_requests) >= self.burst_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests in short time. Please slow down."
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        # Process request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to client host
        return request.client.host if request.client else "unknown"

class EndpointRateLimitMiddleware(BaseHTTPMiddleware):
    """More granular rate limiting per endpoint"""

    def __init__(self, app, limits: Dict[str, Dict[str, int]] = None):
        super().__init__(app)
        self.limits = limits or {
            "/api/refresh": {"per_minute": 5, "burst": 2},
            "/api/ur/refresh": {"per_minute": 5, "burst": 2},
            "/api/exchange-rate/refresh": {"per_minute": 5, "burst": 2},
            "/api/exchange-rate/refresh-async": {"per_minute": 3, "burst": 1},
        }
        self.requests: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        client_ip = self._get_client_ip(request)

        # Check if this endpoint has specific limits
        if path in self.limits:
            limits = self.limits[path]
            current_time = time.time()

            # Clean old requests
            self.requests[client_ip][path] = [
                req_time for req_time in self.requests[client_ip][path]
                if current_time - req_time < 60
            ]

            # Check per-minute limit
            if len(self.requests[client_ip][path]) >= limits["per_minute"]:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests to {path}. Limit: {limits['per_minute']} per minute."
                )

            # Check burst limit
            recent_requests = [
                req_time for req_time in self.requests[client_ip][path]
                if current_time - req_time < 10
            ]
            if len(recent_requests) >= limits["burst"]:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests to {path} in short time. Please slow down."
                )

            # Add current request
            self.requests[client_ip][path].append(current_time)

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"
