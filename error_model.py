"""
RFC 7807 Problem Details for HTTP APIs
Standardized error response model for all API endpoints.
Ref: https://tools.ietf.org/html/rfc7807
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details JSON object."""
    
    type: str = Field(
        default="about:blank",
        description="A URI reference identifying the problem type."
    )
    title: str = Field(
        description="A short, human-readable summary of the problem."
    )
    status: int = Field(
        description="The HTTP status code."
    )
    detail: Optional[str] = Field(
        default=None,
        description="A human-readable explanation of the specific problem."
    )
    instance: Optional[str] = Field(
        default=None,
        description="A URI reference identifying the specific occurrence of the problem."
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="Correlation/trace ID for this request (for debugging)."
    )
    
    class Config:
        example = {
            "type": "https://api.example.com/errors/validation",
            "title": "Validation Error",
            "status": 400,
            "detail": "Invalid date format in UR range query.",
            "instance": "/api/ur/range?from=2025-13-01&to=2025-12-31",
            "trace_id": "550e8400-e29b-41d4-a716-446655440000"
        }


class ProblemResponse(BaseModel):
    """Wrapper for error responses."""
    
    @staticmethod
    def create(
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        trace_id: Optional[str] = None,
        problem_type: str = "about:blank"
    ) -> ProblemDetail:
        """
        Factory to create a ProblemDetail instance.
        
        Args:
            title: Short summary of the problem.
            status: HTTP status code.
            detail: Detailed explanation (optional).
            instance: Request URI or identifier (optional).
            trace_id: Correlation ID (optional).
            problem_type: Problem type URI (default: about:blank).
            
        Returns:
            ProblemDetail instance ready to serialize.
        """
        return ProblemDetail(
            type=problem_type,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            trace_id=trace_id
        )


# Common problem type URIs
PROBLEM_TYPES = {
    "validation": "https://api.sifu.local/errors/validation",
    "not_found": "https://api.sifu.local/errors/not-found",
    "unauthorized": "https://api.sifu.local/errors/unauthorized",
    "forbidden": "https://api.sifu.local/errors/forbidden",
    "conflict": "https://api.sifu.local/errors/conflict",
    "rate_limit": "https://api.sifu.local/errors/rate-limit",
    "service_unavailable": "https://api.sifu.local/errors/service-unavailable",
    "internal_error": "https://api.sifu.local/errors/internal-error",
}
