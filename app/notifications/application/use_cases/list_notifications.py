"""
ListNotificationsUseCase: T-13-06. SF-22. Unread notifications returned first.
"""
from __future__ import annotations

from uuid import UUID

from app.notifications.application.dtos.notification_dtos import NotificationResponse
from app.notifications.domain.repositories.notification_repository import AbstractNotificationRepository


class ListNotificationsUseCase:

    def __init__(self, repo: AbstractNotificationRepository) -> None:
        self._repo = repo

    async def execute(
        self, user_id: UUID, page: int, page_size: int, unread_only: bool = False
    ) -> tuple[list[NotificationResponse], int]:
        notifications, total = await self._repo.list_by_user(
            user_id, page, page_size, unread_only=unread_only
        )
        return [NotificationResponse.model_validate(n) for n in notifications], total
