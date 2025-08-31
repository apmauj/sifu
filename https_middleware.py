"""
HTTPS Middleware for FastAPI
Forces HTTPS redirection and security headers
"""

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to redirect HTTP to HTTPS"""

    async def dispatch(self, request: Request, call_next):
        # Check if request is behind proxy/load balancer
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()

        # If request is HTTP and not behind HTTPS proxy, redirect to HTTPS
        if request.url.scheme == "http" and forwarded_proto != "https":
            # Only redirect in production
            if os.getenv("ENVIRONMENT") == "production":
                https_url = request.url.replace(scheme="https")
                return RedirectResponse(https_url, status_code=301)

        # Continue with request
        response = await call_next(request)

        # Add security headers
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

class SSLHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add SSL/TLS related security headers"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add SSL-related headers
        response.headers["X-SSL-Protocol"] = request.headers.get("X-SSL-Protocol", "unknown")
        response.headers["X-SSL-Cipher"] = request.headers.get("X-SSL-Cipher", "unknown")

        return response
