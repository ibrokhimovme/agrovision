"""
API v1 router for livestock-service.
"""
from fastapi import APIRouter

from app.poultry.api.v1.endpoints.batches import router as batches_router
from app.poultry.api.v1.endpoints.feed import router as feed_router
from app.poultry.api.v1.endpoints.mortality import router as mortality_router
from app.poultry.api.v1.endpoints.vaccination import router as vaccination_router
from app.poultry.api.v1.endpoints.weight import router as weight_router

router = APIRouter()

router.include_router(batches_router)
router.include_router(feed_router)
router.include_router(mortality_router)
router.include_router(vaccination_router)
router.include_router(weight_router)
