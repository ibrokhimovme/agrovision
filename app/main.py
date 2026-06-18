"""
Modular monolith application (M5 — API Consolidation).

Mounts every module's existing v1 router on a single FastAPI instance under
the same /api/v1/... prefixes the api-gateway's ROUTE_MAP used to proxy to
(see .project-governance/monolith-migration/current_state_architecture_report.md
§5 for the original prefix table) — external API surface is unchanged, so the
frontend requires no changes.

Replaces:
  - the gateway's httpx reverse-proxy (app/gateway/api/v1/router.py) with
    direct in-process router inclusion
  - per-service JWT verification-at-the-edge with one app-wide middleware
    (app/core/auth_middleware.py) that does the same header-injection the
    gateway used to do, so no module's endpoint code needed to change

Two ASGI objects are exported, mirroring the old trust boundary exactly:

  - `fastapi_app`: the routers + CORS + exception handlers, with NO JWT
    middleware — this is the equivalent of "all 7 microservices", which
    never re-verified a JWT themselves (only the gateway did). Used by
    reporting's in-process clients (app/reporting/infrastructure/clients/),
    which replace what used to be direct service-to-service httpx calls
    that also bypassed the gateway and were therefore never re-authenticated
    (see current_state_architecture_report.md §2). Using `fastapi_app`
    directly for those calls preserves that exact (lack of) behavior —
    wrapping them in the JWT middleware instead would be a new restriction
    that didn't exist before, not a faithful migration.
  - `app`: `fastapi_app` wrapped in the JWT/header-injection middleware —
    the equivalent of the gateway sitting in front. This is what actually
    gets served (uvicorn app.main:app).

Does NOT yet:
  - run any Alembic migrations on startup (M4 already applied them manually
    against the consolidated `agrovision` database; wiring that into this
    app's lifespan is M6 — Runtime Simplification)
  - get included in docker-compose (M6)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth_middleware import AuthHeaderInjectionMiddleware
from app.core.config import settings
from app.identity.core.exceptions import register_exception_handlers
from app.identity.infrastructure.cache.redis_client import get_redis, close_redis

from app.identity.api.v1.router import router as identity_router
from app.farm.api.v1.router import router as farm_router
from app.poultry.api.v1.router import router as poultry_router
from app.inventory.api.v1.router import router as inventory_router
from app.finance.api.v1.router import router as finance_router
from app.notifications.api.v1.router import router as notifications_router
from app.reporting.api.v1.router import router as reporting_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()
    yield
    await close_redis()


fastapi_app = FastAPI(
    title="AgroVision (modular monolith)",
    description="Consolidated identity/farm/poultry/inventory/finance/notifications/reporting modules.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register_exception_handlers is byte-identical across all 8 modules
# (shared.exceptions -> shared.contracts.api_standards.ErrorResponse mapping)
# — registering it once from one module covers every module.
register_exception_handlers(fastapi_app)

# Mounted under the same prefixes the gateway's ROUTE_MAP used to proxy to.
fastapi_app.include_router(identity_router, prefix="/api/v1")       # /auth, /users, /roles
fastapi_app.include_router(farm_router, prefix="/api/v1")             # /farms, /buildings
fastapi_app.include_router(poultry_router, prefix="/api/v1")           # /batches, /vaccinations, /vaccination-schedules, /health-records, /mortality
fastapi_app.include_router(inventory_router, prefix="/api/v1")        # /warehouses, /stock-items, /inventory
fastapi_app.include_router(finance_router, prefix="/api/v1")          # /expenses, /sales, /profit
fastapi_app.include_router(notifications_router, prefix="/api/v1")    # /notifications
fastapi_app.include_router(reporting_router, prefix="/api/v1")        # /reports


@fastapi_app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": settings.SERVICE_NAME, "version": "1.0.0"}


# Externally-served app — equivalent of the old api-gateway sitting in front
# of all 7 microservices. Point uvicorn/docker at this, not at fastapi_app.
app = AuthHeaderInjectionMiddleware(fastapi_app)
