"""
User management endpoints. SRS §5.2, SF-01.
GET  /users/me       — current user profile
POST /users/         — create user (Farm Owner role required)
GET  /users/         — list users for farm
GET  /users/{id}     — get user detail
PATCH /users/{id}    — update user
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id
from app.application.dtos.user_dtos import UserResponse, CreateUserRequest, UpdateUserRequest
from app.application.use_cases.create_user import CreateUserUseCase
from app.application.use_cases.create_user import CreateUserRequest as CreateUserCmd
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.user_repository_impl import SQLAlchemyUserRepository
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyUserRepository(db)
    user = await GetCurrentUserUseCase(repo).execute(current_user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("/", response_model=APIResponse[UserResponse], status_code=201)
async def create_user(
    body: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyUserRepository(db)
    cmd = CreateUserCmd(
        email=body.email,
        full_name=body.full_name,
        password=body.password,
        role_name=body.role_name,
        farm_id=body.farm_id,
        phone=body.phone,
    )
    user = await CreateUserUseCase(repo, db).execute(cmd)
    await db.commit()
    return APIResponse(data=UserResponse.model_validate(user), status_code=201)


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    farm_id: UUID = Query(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, page_size=page_size)
    repo = SQLAlchemyUserRepository(db)
    users, total = await repo.list_by_farm(farm_id, params.offset, params.page_size)
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        pagination=params.to_meta(total),
    )


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyUserRepository(db)
    user = await GetCurrentUserUseCase(repo).execute(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.patch("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyUserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        from shared.exceptions import EntityNotFoundError
        raise EntityNotFoundError("User", user_id)
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.phone is not None:
        user.phone = body.phone
    if body.is_active is not None:
        user.is_active = body.is_active
    user = await repo.update(user)
    await db.commit()
    return APIResponse(data=UserResponse.model_validate(user))
