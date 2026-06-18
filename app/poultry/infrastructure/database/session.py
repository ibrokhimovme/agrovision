"""
Async SQLAlchemy session factory.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# M5: points at the consolidated `agrovision` database (was this module's own
# `livestock_db` under app.poultry.core.config). search_path includes `farm`
# so that the batches.farm_id FK to farm.farms (MD-003) resolves correctly if
# any unqualified cross-schema query is ever issued; this module's own tables
# still resolve from `poultry` first.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"server_settings": {"search_path": "poultry,farm"}},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
