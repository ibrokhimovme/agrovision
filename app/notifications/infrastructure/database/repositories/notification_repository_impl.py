"""
SQLAlchemy implementation of AbstractNotificationRepository. SF-22.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.domain.models.notification import Notification
from app.notifications.domain.repositories.notification_repository import AbstractNotificationRepository


class SQLAlchemyNotificationRepository(AbstractNotificationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: UUID, page: int, page_size: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        q = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            q = q.where(Notification.is_read == False)  # noqa: E712
        q = q.order_by(Notification.is_read.asc(), Notification.created_at.desc())

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self._session.execute(count_q)).scalar_one()

        q = q.offset((page - 1) * page_size).limit(page_size)
        rows = (await self._session.execute(q)).scalars().all()
        return list(rows), total

    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        from datetime import datetime, timezone
        await self._session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True, updated_at=datetime.now(timezone.utc))
        )
        await self._session.flush()
        return await self.get_by_id(notification_id)

    async def count_unread(self, user_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        return result.scalar_one()
