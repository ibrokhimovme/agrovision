"""
Unit tests for notification use cases. P-13, SF-22.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.application.dtos.notification_dtos import CreateNotificationRequest
from app.application.use_cases.create_notification import CreateNotificationUseCase
from app.application.use_cases.list_notifications import ListNotificationsUseCase
from app.application.use_cases.mark_as_read import MarkAsReadUseCase
from app.domain.models.notification import Notification, NotificationChannel, NotificationSeverity
from shared.exceptions import EntityNotFoundError


def _make_notification(user_id=None, is_read=False) -> Notification:
    from datetime import datetime, timezone
    n = Notification()
    n.id = uuid4()
    n.user_id = user_id or uuid4()
    n.farm_id = None
    n.title = "Test"
    n.body = "Test body"
    n.channel = NotificationChannel.IN_APP
    n.severity = NotificationSeverity.INFO
    n.event_type = "test.event"
    n.reference_id = None
    n.is_read = is_read
    n.is_delivered = False
    n.delivered_at = None
    n.scheduled_for = None
    n.created_at = datetime.now(timezone.utc)
    n.updated_at = datetime.now(timezone.utc)
    return n


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_notification(repo):
    user_id = uuid4()
    notif = _make_notification(user_id)
    repo.create = AsyncMock(return_value=notif)

    req = CreateNotificationRequest(
        user_id=user_id,
        title="Vaktsina muddati o'tdi",
        body="Partiya #42 uchun vaktsina rejalashtirilgan edi.",
        severity=NotificationSeverity.WARNING,
    )

    with patch("app.application.use_cases.create_notification.ws_manager") as mock_ws:
        mock_ws.send_to_user = AsyncMock()
        result = await CreateNotificationUseCase(repo).execute(req)

    assert result.title == "Test"
    assert result.is_read is False
    mock_ws.send_to_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_notifications_empty(repo):
    user_id = uuid4()
    repo.list_by_user = AsyncMock(return_value=([], 0))
    results, total = await ListNotificationsUseCase(repo).execute(user_id, 1, 20)
    assert results == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_notifications_returns_items(repo):
    user_id = uuid4()
    notifications = [_make_notification(user_id), _make_notification(user_id)]
    repo.list_by_user = AsyncMock(return_value=(notifications, 2))
    results, total = await ListNotificationsUseCase(repo).execute(user_id, 1, 20)
    assert len(results) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_mark_as_read(repo):
    notif = _make_notification(is_read=True)
    repo.mark_as_read = AsyncMock(return_value=notif)
    result = await MarkAsReadUseCase(repo).execute(notif.id)
    assert result.is_read is True
    repo.mark_as_read.assert_awaited_once_with(notif.id)


@pytest.mark.asyncio
async def test_mark_as_read_not_found(repo):
    repo.mark_as_read = AsyncMock(return_value=None)
    with pytest.raises(EntityNotFoundError):
        await MarkAsReadUseCase(repo).execute(uuid4())


@pytest.mark.asyncio
async def test_create_notification_sends_ws(repo):
    user_id = uuid4()
    notif = _make_notification(user_id)
    repo.create = AsyncMock(return_value=notif)
    req = CreateNotificationRequest(user_id=user_id, title="T", body="B")

    with patch("app.application.use_cases.create_notification.ws_manager") as mock_ws:
        mock_ws.send_to_user = AsyncMock()
        await CreateNotificationUseCase(repo).execute(req)
        payload = mock_ws.send_to_user.call_args[0][1]
        assert payload["type"] == "notification"
        assert "title" in payload
