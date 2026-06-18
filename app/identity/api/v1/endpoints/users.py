"""
User management endpoints. SRS §5.2, SF-01.
GET  /users/me       — current user profile
POST /users/         — create user (Farm Owner role required)
GET  /users/         — list users: account-wide (multi-farm) if farm_id is
                        omitted, or for one farm if farm_id is given — EX-15
                        (execution-v2), decision_log.md BMD-017
GET  /users/{id}     — get user detail
PATCH /users/{id}    — update user
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.dependencies import get_current_user_id
from app.identity.application.dtos.user_dtos import UserResponse, CreateUserRequest, UpdateUserRequest
from app.identity.application.use_cases.create_user import CreateUserUseCase
from app.identity.application.use_cases.create_user import CreateUserRequest as CreateUserCmd
from app.identity.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.identity.infrastructure.clients.farm_client import FarmClient
from app.identity.infrastructure.database.session import get_db
from app.identity.infrastructure.database.repositories.user_repository_impl import SQLAlchemyUserRepository
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationParams
from shared.exceptions import EntityNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])


def _is_superuser(x_user_roles: str) -> bool:
    """EX-15 (execution-v2): same convention as app/farm/api/v1/endpoints/farms.py's
    _is_superuser — the bypass condition must be the actual super_admin role,
    not "account_id is absent" (a super-admin can legitimately own an account too)."""
    return "super_admin" in [r.strip() for r in x_user_roles.split(",") if r.strip()]


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
    x_account_id: str = Header(default="", alias="X-Account-Id"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    is_superuser = _is_superuser(x_user_roles)
    account_id: Optional[UUID] = None

    if body.farm_id is not None:
        # EX-15 (execution-v2): resolves T-EX15-04 — a farm outside the
        # caller's account 404s here exactly like it would for GET
        # /farms/{id} directly, since GetFarmUseCase enforces that already.
        # The new user inherits the farm's account, not the caller's own
        # (relevant for a superuser creating a user into someone else's account).
        farm = await FarmClient().get_farm(body.farm_id, x_account_id, x_user_roles)
        if farm is None:
            raise EntityNotFoundError("Farm", body.farm_id)
        farm_account_id = farm.get("account_id")
        account_id = UUID(farm_account_id) if farm_account_id else None
    elif not is_superuser:
        if not x_account_id:
            raise EntityNotFoundError("Account", "none")
        account_id = UUID(x_account_id)
    # else: superuser creating a farm-less/account-less user (e.g. another
    # platform admin) — account_id stays None, mirroring User.account_id's
    # own nullable-for-superuser design (see user.py).

    repo = SQLAlchemyUserRepository(db)
    cmd = CreateUserCmd(
        email=body.email,
        full_name=body.full_name,
        password=body.password,
        role_name=body.role_name,
        farm_id=body.farm_id,
        phone=body.phone,
        account_id=account_id,
    )
    user = await CreateUserUseCase(repo, db).execute(cmd)
    await db.commit()
    return APIResponse(data=UserResponse.model_validate(user), status_code=201)


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    farm_id: Optional[UUID] = Query(None, description="Filter to one farm; omit for account-wide listing"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    x_account_id: str = Header(default="", alias="X-Account-Id"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    is_superuser = _is_superuser(x_user_roles)
    params = PaginationParams(page=page, page_size=page_size)
    repo = SQLAlchemyUserRepository(db)

    if farm_id is not None:
        if not is_superuser:
            farm = await FarmClient().get_farm(farm_id, x_account_id, x_user_roles)
            if farm is None:
                raise EntityNotFoundError("Farm", farm_id)
        users, total = await repo.list_by_farm(farm_id, params.offset, params.page_size)
    else:
        # EX-15 (execution-v2): account-wide (multi-farm) listing, T-EX15-01.
        # A non-superuser caller with no account sees nothing — same "empty,
        # not every user" precedent as ListFarmsUseCase.
        if not is_superuser and not x_account_id:
            users, total = [], 0
        else:
            account_id = None if is_superuser else UUID(x_account_id)
            users, total = await repo.list_by_account(account_id, params.offset, params.page_size)

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
