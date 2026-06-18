"""
Notification REST endpoints. T-13-06, T-13-07. SF-22.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.application.dtos.notification_dtos import (
    CreateNotificationRequest,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.application.use_cases.create_notification import CreateNotificationUseCase
from app.notifications.application.use_cases.list_notifications import ListNotificationsUseCase
from app.notifications.application.use_cases.mark_as_read import MarkAsReadUseCase
from app.notifications.infrastructure.database.repositories.notification_repository_impl import (
    SQLAlchemyNotificationRepository,
)
from app.notifications.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/notifications/",
    response_model=APIResponse[NotificationResponse],
    status_code=201,
    tags=["Notifications"],
)
async def create_notification(
    body: CreateNotificationRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    result = await CreateNotificationUseCase(repo).execute(body)
    return APIResponse(data=result)


@router.get(
    "/notifications/",
    response_model=PaginatedResponse[NotificationResponse],
    tags=["Notifications"],
)
async def list_notifications(
    user_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    notifications, total = await ListNotificationsUseCase(repo).execute(
        user_id, page, page_size, unread_only
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse(
        data=notifications,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


@router.get(
    "/notifications/unread-count",
    response_model=APIResponse[UnreadCountResponse],
    tags=["Notifications"],
)
async def unread_count(
    user_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    count = await repo.count_unread(user_id)
    return APIResponse(data=UnreadCountResponse(unread_count=count))


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=APIResponse[NotificationResponse],
    tags=["Notifications"],
)
async def mark_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyNotificationRepository(db)
    result = await MarkAsReadUseCase(repo).execute(notification_id)
    return APIResponse(data=result)
