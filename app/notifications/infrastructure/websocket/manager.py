"""
WebSocket connection manager for real-time notification delivery.
SRS §5.23: critical notifications within 1 minute.
VG-01: real-time dashboards with top 10 KPIs.
Each user maintains a set of active WebSocket connections (multi-tab support).
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[str(user_id)].add(websocket)
        logger.info("WebSocket connected for user %s. Active connections: %d", user_id, len(self._connections[str(user_id)]))

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        key = str(user_id)
        self._connections[key].discard(websocket)
        if not self._connections[key]:
            del self._connections[key]

    async def send_to_user(self, user_id: UUID, payload: dict) -> None:
        key = str(user_id)
        dead: Set[WebSocket] = set()
        for ws in self._connections.get(key, set()):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def broadcast(self, farm_id: UUID, payload: dict) -> None:
        """Broadcast to all users connected for a given farm."""
        # TODO: maintain farm_id → user_id index for targeted farm broadcasts
        message = json.dumps(payload)
        dead_pairs: list[tuple[str, WebSocket]] = []
        for user_key, sockets in list(self._connections.items()):
            for ws in sockets:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_pairs.append((user_key, ws))
        for user_key, ws in dead_pairs:
            self._connections[user_key].discard(ws)

    @property
    def active_user_count(self) -> int:
        return len(self._connections)


ws_manager = WebSocketManager()
