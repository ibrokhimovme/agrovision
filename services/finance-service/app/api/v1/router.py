"""
API v1 router for finance-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.expenses import router as expenses_router
from app.api.v1.endpoints.sales import router as sales_router

router = APIRouter()

router.include_router(expenses_router)
router.include_router(sales_router)
