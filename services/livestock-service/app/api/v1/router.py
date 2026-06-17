"""
API v1 router for livestock-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.batches import router as batches_router
from app.api.v1.endpoints.feed import router as feed_router

router = APIRouter()

router.include_router(batches_router)
router.include_router(feed_router)
