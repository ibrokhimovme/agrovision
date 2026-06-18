"""
AgroVision Reporting Service
Report generation, KPI aggregation, PDF export. SRS §5.21, BRD §3.1 SG-03.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.reporting.core.config import settings
from app.reporting.core.exceptions import register_exception_handlers
from app.reporting.api.v1.router import router as v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s...", settings.SERVICE_NAME)
    yield
    logger.info("Shutting down %s...", settings.SERVICE_NAME)


app = FastAPI(
    title="AgroVision Reporting Service",
    description="Report generation, KPI aggregation, PDF export. SRS §5.21, BRD §3.1 SG-03.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": settings.SERVICE_NAME, "version": "0.1.0"}
