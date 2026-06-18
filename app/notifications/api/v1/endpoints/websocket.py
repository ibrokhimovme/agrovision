"""
WebSocket endpoint for real-time notification delivery. T-13-05. SF-22.
Client connects with JWT token as query param: ws://.../ws/{user_id}?token=<jwt>
On connect: sends all unread notifications immediately, then keeps connection alive.
"""
from __future__ import annotations

import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.infrastructure.database.repositories.notification_repository_impl import (
    SQLAlchemyNotificationRepository,
)
from app.notifications.infrastructure.database.session import get_db
from app.notifications.infrastructure.websocket.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id: UUID,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    await ws_manager.connect(user_id, websocket)
    try:
        repo = SQLAlchemyNotificationRepository(db)
        notifications, _ = await repo.list_by_user(user_id, page=1, page_size=50, unread_only=True)
        for notif in notifications:
            await websocket.send_text(json.dumps({
                "type": "notification",
                "id": str(notif.id),
                "title": notif.title,
                "body": notif.body,
                "severity": notif.severity.value,
                "event_type": notif.event_type,
                "created_at": notif.created_at.isoformat(),
            }))

        while True:
            # Keep connection alive; client may send {"type": "ping"}
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
    except Exception as exc:
        logger.exception("WebSocket error for user %s: %s", user_id, exc)
        ws_manager.disconnect(user_id, websocket)
