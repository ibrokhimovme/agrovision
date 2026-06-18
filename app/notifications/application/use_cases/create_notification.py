"""
CreateNotificationUseCase: T-13-xx. SF-22.
Creates and immediately delivers notification via WebSocket if user is connected.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.notifications.application.dtos.notification_dtos import CreateNotificationRequest, NotificationResponse
from app.notifications.domain.models.notification import Notification
from app.notifications.domain.repositories.notification_repository import AbstractNotificationRepository
from app.notifications.infrastructure.websocket.manager import ws_manager


class CreateNotificationUseCase:

    def __init__(self, repo: AbstractNotificationRepository) -> None:
        self._repo = repo

    async def execute(self, req: CreateNotificationRequest) -> NotificationResponse:
        now = datetime.now(timezone.utc)
        notif = Notification()
        notif.id = uuid4()
        notif.user_id = req.user_id
        notif.farm_id = req.farm_id
        notif.title = req.title
        notif.body = req.body
        notif.channel = req.channel
        notif.severity = req.severity
        notif.event_type = req.event_type
        notif.reference_id = req.reference_id
        notif.is_read = False
        notif.is_delivered = False
        notif.created_at = now
        notif.updated_at = now

        notif = await self._repo.create(notif)

        payload = {
            "type": "notification",
            "id": str(notif.id),
            "title": notif.title,
            "body": notif.body,
            "severity": notif.severity.value,
            "event_type": notif.event_type,
            "created_at": notif.created_at.isoformat(),
        }
        await ws_manager.send_to_user(req.user_id, payload)

        return NotificationResponse.model_validate(notif)
