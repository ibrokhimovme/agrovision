"""
API v1 router for livestock-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.batches import router as batches_router

router = APIRouter()

router.include_router(batches_router)
