"""
API v1 router for notification-service.
"""
from fastapi import APIRouter

from app.notifications.api.v1.endpoints.notifications import router as notifications_router
from app.notifications.api.v1.endpoints.websocket import router as ws_router

router = APIRouter()

router.include_router(notifications_router)
router.include_router(ws_router)
