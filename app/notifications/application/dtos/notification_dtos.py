"""
DTOs for notification management. SF-22.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.notifications.domain.models.notification import NotificationChannel, NotificationSeverity


class CreateNotificationRequest(BaseModel):
    user_id: UUID
    farm_id: Optional[UUID] = None
    title: str
    body: str
    channel: NotificationChannel = NotificationChannel.IN_APP
    severity: NotificationSeverity = NotificationSeverity.INFO
    event_type: Optional[str] = None
    reference_id: Optional[UUID] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    farm_id: Optional[UUID]
    title: str
    body: str
    channel: NotificationChannel
    severity: NotificationSeverity
    event_type: Optional[str]
    reference_id: Optional[UUID]
    is_read: bool
    is_delivered: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    unread_count: int
