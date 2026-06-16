"""
AgroVision Notification Service
WebSocket delivery, email/SMS integration, alert management. SRS §5.22, §5.23.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import router as v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s...", settings.SERVICE_NAME)
    # TODO: initialise DB pool, RabbitMQ connection, Redis pool here
    yield
    logger.info("Shutting down %s...", settings.SERVICE_NAME)
    # TODO: close DB pool, RabbitMQ connection, Redis pool here


app = FastAPI(
    title="AgroVision Notification Service",
    description="WebSocket delivery, email/SMS integration, alert management. SRS §5.22, §5.23.",
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

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": settings.SERVICE_NAME, "version": "0.1.0"}
