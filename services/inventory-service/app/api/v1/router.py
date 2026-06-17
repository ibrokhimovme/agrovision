"""
API v1 router for inventory-service.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.warehouses import router as warehouses_router
from app.api.v1.endpoints.stock import router as stock_router

router = APIRouter()

router.include_router(warehouses_router)
router.include_router(stock_router)
