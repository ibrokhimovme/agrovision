from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.identity.core.config import settings
from app.identity.core.exceptions import register_exception_handlers
from app.identity.api.v1.router import router as v1_router
from app.identity.infrastructure.cache.redis_client import get_redis, close_redis

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    # Runs in a worker thread so asyncio.run() inside env.py gets a clean event loop.
    cfg = AlembicConfig("/app/alembic.ini")
    alembic_command.upgrade(cfg, "head")
    logger.info("Alembic migrations applied.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s...", settings.SERVICE_NAME)
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        await loop.run_in_executor(pool, _run_migrations)
    await get_redis()
    yield
    await close_redis()
    logger.info("Shutting down %s...", settings.SERVICE_NAME)


app = FastAPI(
    title="AgroVision Identity Service",
    description="Authentication, authorization, user management, JWT lifecycle. SRS §5.1, §5.2, §11.",
    version="1.0.0",
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
    return {"status": "ok", "service": settings.SERVICE_NAME, "version": "1.0.0"}
