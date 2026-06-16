"""
AgroVision — Domain Exception Hierarchy
==========================================
All services raise domain exceptions from this hierarchy.
The API layer translates them to HTTP error responses.

Hierarchy:
  AgroVisionError
    ├── DomainError
    │     ├── EntityNotFoundError
    │     ├── BusinessRuleViolationError
    │     ├── DuplicateEntityError
    │     └── InvalidStateTransitionError
    ├── InfrastructureError
    │     ├── DatabaseError
    │     ├── MessagingError
    │     └── CacheError
    └── ApplicationError
          ├── AuthenticationError
          ├── AuthorizationError
          └── ServiceUnavailableError
"""

from __future__ import annotations

from typing import Any, Optional


class AgroVisionError(Exception):
    """Base exception for all AgroVision errors."""
    error_code: str = "AGROVISION_ERROR"
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: Optional[str] = None, details: Any = None) -> None:
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)


# ── Domain Exceptions ─────────────────────────────────────────────────────────

class DomainError(AgroVisionError):
    error_code = "DOMAIN_ERROR"


class EntityNotFoundError(DomainError):
    error_code = "NOT_FOUND"
    default_message = "The requested resource was not found."

    def __init__(self, entity_type: str, entity_id: Any) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id '{entity_id}' was not found.")


class BusinessRuleViolationError(DomainError):
    error_code = "BUSINESS_RULE"
    default_message = "A business rule was violated."

    def __init__(self, rule: str, message: Optional[str] = None) -> None:
        self.rule = rule
        super().__init__(message or f"Business rule violated: {rule}")


class DuplicateEntityError(DomainError):
    error_code = "CONFLICT"
    default_message = "The resource already exists."


class InvalidStateTransitionError(DomainError):
    error_code = "INVALID_STATE_TRANSITION"

    def __init__(self, entity_type: str, from_state: str, to_state: str) -> None:
        self.entity_type = entity_type
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Cannot transition {entity_type} from '{from_state}' to '{to_state}'."
        )


# ── Infrastructure Exceptions ─────────────────────────────────────────────────

class InfrastructureError(AgroVisionError):
    error_code = "INFRASTRUCTURE_ERROR"


class DatabaseError(InfrastructureError):
    error_code = "DATABASE_ERROR"


class MessagingError(InfrastructureError):
    error_code = "MESSAGING_ERROR"


class CacheError(InfrastructureError):
    error_code = "CACHE_ERROR"


# ── Application Exceptions ────────────────────────────────────────────────────

class ApplicationError(AgroVisionError):
    error_code = "APPLICATION_ERROR"


class AuthenticationError(ApplicationError):
    error_code = "AUTH_001"
    default_message = "Authentication failed."


class AuthorizationError(ApplicationError):
    error_code = "AUTH_004"
    default_message = "Insufficient permissions."

    def __init__(self, required_permission: Optional[str] = None) -> None:
        self.required_permission = required_permission
        super().__init__(
            f"Permission required: {required_permission}" if required_permission
            else self.default_message
        )


class ServiceUnavailableError(ApplicationError):
    error_code = "SERVICE_UNAVAILABLE"
    default_message = "A required service is unavailable."
