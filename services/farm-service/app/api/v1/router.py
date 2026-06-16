"""
API v1 router for farm-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.farms import router as farms_router

router = APIRouter()

router.include_router(farms_router)
