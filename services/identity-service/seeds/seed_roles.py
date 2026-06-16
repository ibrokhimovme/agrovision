"""
Seed script: system roles + default admin user.
Run once after alembic upgrade head:
  python seeds/seed_roles.py

SRS §5.2: 8 predefined system roles.
"""
from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import bcrypt as _bcrypt_mod
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.domain.models.user import Role, User

SYSTEM_ROLES = [
    ("farm_owner",          "Ferma Egasi"),
    ("farm_director",       "Ferma Direktori"),
    ("farm_manager",        "Ferma Boshqaruvchisi"),
    ("veterinarian",        "Veterinar"),
    ("accountant",          "Hisobchi"),
    ("warehouse_manager",   "Ombor Menejeri"),
    ("sales_personnel",     "Sotuv Xodimi"),
    ("farm_worker",         "Ferma Xodimi"),
]

async def seed(session: AsyncSession) -> None:
    # Roles
    for name, display_name in SYSTEM_ROLES:
        result = await session.execute(select(Role).where(Role.name == name))
        if result.scalar_one_or_none() is None:
            session.add(Role(name=name, display_name=display_name, is_system=True))
            print(f"  + role: {name}")
        else:
            print(f"  ~ role already exists: {name}")
    await session.flush()

    # Default superuser
    admin_email = "admin@agrovision.uz"
    result = await session.execute(select(User).where(User.email == admin_email))
    if result.scalar_one_or_none() is None:
        admin = User(
            email=admin_email,
            full_name="System Administrator",
            hashed_password=_bcrypt_mod.hashpw(b"Admin@123", _bcrypt_mod.gensalt()).decode(),
            is_superuser=True,
            is_active=True,
        )
        result = await session.execute(select(Role).where(Role.name == "farm_owner"))
        owner_role = result.scalar_one_or_none()
        if owner_role:
            admin.roles.append(owner_role)
        session.add(admin)
        print(f"  + admin user: {admin_email} (password: Admin@123)")
    else:
        print(f"  ~ admin user already exists: {admin_email}")

    await session.commit()
    print("Seed complete.")


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
