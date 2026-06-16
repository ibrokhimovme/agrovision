"""
AgroVision — API Response Standards
======================================
All service endpoints MUST return responses conforming to these schemas.
This ensures consistent client-side handling across all 8 services.

Versioning strategy:
  - URL prefix: /api/v1/...
  - Breaking changes increment the version: /api/v2/...
  - Non-breaking additions are backward-compatible within the same version.

Pagination:
  - All list endpoints accept: page (1-based), page_size (default 20, max 100).
  - Response wraps items in PaginatedResponse with full PaginationMeta.

Error codes:
  - 400 Bad Request    → ValidationErrorResponse (field-level errors)
  - 401 Unauthorized   → ErrorResponse (AUTH_001)
  - 403 Forbidden      → ErrorResponse (AUTH_002)
  - 404 Not Found      → ErrorResponse (NOT_FOUND)
  - 409 Conflict       → ErrorResponse (CONFLICT)
  - 422 Unprocessable  → ValidationErrorResponse
  - 429 Too Many Req   → ErrorResponse (RATE_LIMIT)
  - 500 Internal Error → ErrorResponse (INTERNAL)
"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── Success Responses ────────────────────────────────────────────────────────

class APIResponse(BaseModel, Generic[T]):
    """Standard single-resource response wrapper."""
    success: bool = True
    data: T
    message: Optional[str] = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list response wrapper."""
    success: bool = True
    data: List[T]
    pagination: PaginationMeta
    message: Optional[str] = None


# ── Error Responses ──────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response for all non-validation errors."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None
    trace_id: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Standard validation error response (422)."""
    success: bool = False
    error_code: str = "VALIDATION_ERROR"
    message: str = "Validation failed"
    errors: List[ErrorDetail]
    trace_id: Optional[str] = None


# ── Error Code Registry ───────────────────────────────────────────────────────

class ErrorCodes:
    # Auth
    AUTH_INVALID_CREDENTIALS = "AUTH_001"
    AUTH_TOKEN_EXPIRED = "AUTH_002"
    AUTH_TOKEN_INVALID = "AUTH_003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"
    AUTH_ACCOUNT_LOCKED = "AUTH_005"
    AUTH_2FA_REQUIRED = "AUTH_006"

    # Resource
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    GONE = "GONE"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT"

    # Server
    INTERNAL_ERROR = "INTERNAL"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"


# ── Pagination Helpers ────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def to_meta(self, total_items: int) -> PaginationMeta:
        import math
        total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        return PaginationMeta(
            page=self.page,
            page_size=self.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=self.page < total_pages,
            has_previous=self.page > 1,
        )
