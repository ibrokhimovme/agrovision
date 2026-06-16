"""
Service-level exception handlers.
Maps domain exceptions → HTTP responses using shared error contracts.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shared.exceptions import (
    EntityNotFoundError,
    BusinessRuleViolationError,
    DuplicateEntityError,
    AuthenticationError,
    AuthorizationError,
    InvalidStateTransitionError,
)
from shared.contracts.api_standards import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def not_found_handler(request: Request, exc: EntityNotFoundError):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(BusinessRuleViolationError)
    async def business_rule_handler(request: Request, exc: BusinessRuleViolationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
                details={"rule": exc.rule},
            ).model_dump(),
        )

    @app.exception_handler(DuplicateEntityError)
    async def conflict_handler(request: Request, exc: DuplicateEntityError):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(AuthenticationError)
    async def auth_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(AuthorizationError)
    async def authz_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=403,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(InvalidStateTransitionError)
    async def state_transition_handler(request: Request, exc: InvalidStateTransitionError):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )
