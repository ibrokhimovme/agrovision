"""
Abstract repository interface for Notification. SF-22.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.notifications.domain.models.notification import Notification


class AbstractNotificationRepository(ABC):

    @abstractmethod
    async def create(self, notification: Notification) -> Notification: ...

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]: ...

    @abstractmethod
    async def list_by_user(
        self, user_id: UUID, page: int, page_size: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]: ...

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]: ...

    @abstractmethod
    async def count_unread(self, user_id: UUID) -> int: ...
