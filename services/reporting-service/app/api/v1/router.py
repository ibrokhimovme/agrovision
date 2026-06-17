"""
API v1 router for reporting-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.reports import router as reports_router

router = APIRouter()

router.include_router(reports_router)
