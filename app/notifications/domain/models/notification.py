"""
Notification domain models. SRS §5.23 (Notifications). SF-22.
Critical notifications must be delivered within 1 minute — SRS §6.
Channels: in-app (WebSocket), email, SMS.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class NotificationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Notification(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    A notification to be delivered to a user via one or more channels.
    SF-22: in-app, email, SMS for critical events and reminders.
    Critical events (mortality spike, disease outbreak, low stock, overdue vaccination)
    must trigger CRITICAL severity and deliver within 1 minute.
    """
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    farm_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(String(20), nullable=False)
    severity: Mapped[NotificationSeverity] = mapped_column(String(20), nullable=False, default=NotificationSeverity.INFO)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
