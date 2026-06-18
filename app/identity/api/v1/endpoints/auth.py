"""
Authentication endpoints. SRS §5.1, SF-01.
POST /auth/login    — email + password → JWT tokens
POST /auth/refresh  — refresh token → new access token
POST /auth/logout   — invalidate current access token
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.application.dtos.auth_dtos import (
    LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse,
)
from app.identity.application.use_cases.authenticate import AuthenticateUserUseCase
from app.identity.application.use_cases.refresh_token import RefreshTokenUseCase
from app.identity.application.use_cases.logout import LogoutUseCase
from app.identity.core.config import settings
from app.identity.infrastructure.database.session import get_db
from app.identity.infrastructure.database.repositories.user_repository_impl import SQLAlchemyUserRepository
from app.identity.infrastructure.cache.redis_client import get_redis
from shared.contracts.api_standards import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    use_case = AuthenticateUserUseCase(repo)
    tokens = await use_case.execute(body.email, body.password)
    return APIResponse(
        data=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    )


@router.post("/refresh", response_model=APIResponse[AccessTokenResponse])
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    use_case = RefreshTokenUseCase(repo)
    result = await use_case.execute(body.refresh_token)
    return APIResponse(data=AccessTokenResponse(**result))


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    request: Request,
    authorization: str = Header(default=""),
    redis=Depends(get_redis),
):
    token = authorization.removeprefix("Bearer ").strip()
    if token:
        use_case = LogoutUseCase(redis)
        await use_case.execute(token)
    return APIResponse(data={"message": "Logged out successfully"})
