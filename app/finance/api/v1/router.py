"""
API v1 router for finance-service.
"""
from fastapi import APIRouter

from app.finance.api.v1.endpoints.debt import router as debt_router
from app.finance.api.v1.endpoints.expenses import router as expenses_router
from app.finance.api.v1.endpoints.profit import router as profit_router
from app.finance.api.v1.endpoints.sales import router as sales_router
from app.finance.api.v1.endpoints.suppliers import router as suppliers_router

router = APIRouter()

router.include_router(expenses_router)
router.include_router(sales_router)
router.include_router(profit_router)
router.include_router(suppliers_router)
router.include_router(debt_router)
