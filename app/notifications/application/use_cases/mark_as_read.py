"""
MarkAsReadUseCase: T-13-07. SF-22.
"""
from __future__ import annotations

from uuid import UUID

from app.notifications.application.dtos.notification_dtos import NotificationResponse
from app.notifications.domain.repositories.notification_repository import AbstractNotificationRepository
from shared.exceptions import EntityNotFoundError


class MarkAsReadUseCase:

    def __init__(self, repo: AbstractNotificationRepository) -> None:
        self._repo = repo

    async def execute(self, notification_id: UUID) -> NotificationResponse:
        notif = await self._repo.mark_as_read(notification_id)
        if notif is None:
            raise EntityNotFoundError("Notification", str(notification_id))
        return NotificationResponse.model_validate(notif)
