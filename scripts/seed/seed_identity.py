"""
Identity Service Seed
======================
Creates: roles, permissions, users, farm reference.

Users created:
  admin@agrovision.uz       — Super Admin (platform admin)
  owner@toshkent-broiler.uz — Farm Owner (Toshkent Broiler Ferma)
  manager@toshkent-broiler.uz — Farm Manager
  accountant@toshkent-broiler.uz — Accountant
  worker1@toshkent-broiler.uz — Farm Worker
  vet@toshkent-broiler.uz   — Veterinarian

All passwords: Admin123! (super admin), or role name + 123! pattern.
"""
import asyncio
import asyncpg
from config import *

# Pre-computed bcrypt hashes (rounds=12) — use bcrypt.hashpw() to regenerate
_HASHES = {
    "Admin123!":      "$2b$12$nRr1tS6XX4ZkUAKN892pb.1cnCNz./3Uyo9RwfWTuFuX1ekyoeusK",
    "Owner123!":      "$2b$12$L6faMTfpMEeAQP620LxOfusacczjjP6q4VbLXbx6AkswWq6U9x8Je",
    "Manager123!":    "$2b$12$rwBMTqdbTH7au2uJy5DpQuKbnRbyQoKghDNCPRInAbE1vULOxJWHS",
    "Accountant123!": "$2b$12$.pxuBcsCrWbaHcTOUQAYMOZKoGlo40lyGi17BDPS0d/n.Vc1JdXaO",
    "Worker123!":     "$2b$12$yScB535kaBfHevrhmTqqHu.tNnS3xjHSpquOxgt4NIhfWctJ9p68y",
    "Vet123!":        "$2b$12$BCLgXRdDR/BDTO.BGr42DuGL59vm/2tI7Ci/lAXXX90Xl/QyZlqc.",
}


def hash_password(plain: str) -> str:
    return _HASHES[plain]


ROLES = [
    (ROLE_SUPER_ADMIN_ID, "super_admin",  "Super Admin",       True),
    (ROLE_FARM_OWNER_ID,  "farm_owner",   "Ferma egasi",       True),
    (ROLE_MANAGER_ID,     "farm_manager", "Ferma menejeri",    True),
    (ROLE_ACCOUNTANT_ID,  "accountant",   "Buxgalter",         True),
    (ROLE_WORKER_ID,      "farm_worker",  "Ferma ishchisi",    True),
    (ROLE_VET_ID,         "veterinarian", "Veterinar",         True),
]

# (role_id, module, action)
ROLE_PERMISSIONS = [
    # Super Admin — all modules, all actions
    *[(ROLE_SUPER_ADMIN_ID, m, a)
      for m in ["farms", "batches", "feed", "mortality", "vaccinations", "health",
                "inventory", "finance", "reports", "notifications", "users", "roles"]
      for a in ["read", "create", "update", "delete", "approve"]],

    # Farm Owner — read/approve everything, create/update operational records
    (ROLE_FARM_OWNER_ID, "farms",         "read"),
    (ROLE_FARM_OWNER_ID, "farms",         "update"),
    (ROLE_FARM_OWNER_ID, "batches",       "read"),
    (ROLE_FARM_OWNER_ID, "batches",       "create"),
    (ROLE_FARM_OWNER_ID, "batches",       "update"),
    (ROLE_FARM_OWNER_ID, "feed",          "read"),
    (ROLE_FARM_OWNER_ID, "mortality",     "read"),
    (ROLE_FARM_OWNER_ID, "vaccinations",  "read"),
    (ROLE_FARM_OWNER_ID, "vaccinations",  "approve"),
    (ROLE_FARM_OWNER_ID, "health",        "read"),
    (ROLE_FARM_OWNER_ID, "inventory",     "read"),
    (ROLE_FARM_OWNER_ID, "inventory",     "approve"),
    (ROLE_FARM_OWNER_ID, "finance",       "read"),
    (ROLE_FARM_OWNER_ID, "finance",       "create"),
    (ROLE_FARM_OWNER_ID, "finance",       "approve"),
    (ROLE_FARM_OWNER_ID, "reports",       "read"),
    (ROLE_FARM_OWNER_ID, "users",         "read"),

    # Farm Manager — daily operations
    (ROLE_MANAGER_ID, "farms",         "read"),
    (ROLE_MANAGER_ID, "batches",       "read"),
    (ROLE_MANAGER_ID, "batches",       "create"),
    (ROLE_MANAGER_ID, "batches",       "update"),
    (ROLE_MANAGER_ID, "feed",          "read"),
    (ROLE_MANAGER_ID, "feed",          "create"),
    (ROLE_MANAGER_ID, "feed",          "update"),
    (ROLE_MANAGER_ID, "mortality",     "read"),
    (ROLE_MANAGER_ID, "mortality",     "create"),
    (ROLE_MANAGER_ID, "vaccinations",  "read"),
    (ROLE_MANAGER_ID, "vaccinations",  "create"),
    (ROLE_MANAGER_ID, "health",        "read"),
    (ROLE_MANAGER_ID, "health",        "create"),
    (ROLE_MANAGER_ID, "inventory",     "read"),
    (ROLE_MANAGER_ID, "inventory",     "create"),
    (ROLE_MANAGER_ID, "inventory",     "update"),
    (ROLE_MANAGER_ID, "finance",       "read"),
    (ROLE_MANAGER_ID, "finance",       "create"),
    (ROLE_MANAGER_ID, "reports",       "read"),
    (ROLE_MANAGER_ID, "notifications", "read"),

    # Accountant — financial records
    (ROLE_ACCOUNTANT_ID, "finance",   "read"),
    (ROLE_ACCOUNTANT_ID, "finance",   "create"),
    (ROLE_ACCOUNTANT_ID, "finance",   "update"),
    (ROLE_ACCOUNTANT_ID, "finance",   "approve"),
    (ROLE_ACCOUNTANT_ID, "inventory", "read"),
    (ROLE_ACCOUNTANT_ID, "batches",   "read"),
    (ROLE_ACCOUNTANT_ID, "reports",   "read"),

    # Farm Worker — daily data entry
    (ROLE_WORKER_ID, "batches",      "read"),
    (ROLE_WORKER_ID, "feed",         "read"),
    (ROLE_WORKER_ID, "feed",         "create"),
    (ROLE_WORKER_ID, "mortality",    "read"),
    (ROLE_WORKER_ID, "mortality",    "create"),
    (ROLE_WORKER_ID, "vaccinations", "read"),
    (ROLE_WORKER_ID, "health",       "read"),
    (ROLE_WORKER_ID, "health",       "create"),

    # Veterinarian — health and vaccination management
    (ROLE_VET_ID, "batches",      "read"),
    (ROLE_VET_ID, "vaccinations", "read"),
    (ROLE_VET_ID, "vaccinations", "create"),
    (ROLE_VET_ID, "vaccinations", "update"),
    (ROLE_VET_ID, "vaccinations", "approve"),
    (ROLE_VET_ID, "health",       "read"),
    (ROLE_VET_ID, "health",       "create"),
    (ROLE_VET_ID, "health",       "update"),
    (ROLE_VET_ID, "mortality",    "read"),
    (ROLE_VET_ID, "inventory",    "read"),
    (ROLE_VET_ID, "reports",      "read"),
]

USERS = [
    {
        "id": USER_SUPER_ADMIN_ID,
        "email": "admin@agrovision.uz",
        "full_name": "Platform Administrator",
        "phone": "+998 90 000 00 00",
        "hashed_password": hash_password("Admin123!"),
        "is_active": True,
        "is_superuser": True,
        "farm_id": None,
        "roles": [ROLE_SUPER_ADMIN_ID],
    },
    {
        "id": USER_FARM_OWNER_ID,
        "email": "owner@toshkent-broiler.uz",
        "full_name": "Yusupov Baxtiyor Hamidovich",
        "phone": "+998 71 200 11 22",
        "hashed_password": hash_password("Owner123!"),
        "is_active": True,
        "is_superuser": False,
        "farm_id": FARM_ID,
        "roles": [ROLE_FARM_OWNER_ID],
    },
    {
        "id": USER_MANAGER_ID,
        "email": "manager@toshkent-broiler.uz",
        "full_name": "Rahimov Dilshod Baxtiyorovich",
        "phone": "+998 90 300 44 55",
        "hashed_password": hash_password("Manager123!"),
        "is_active": True,
        "is_superuser": False,
        "farm_id": FARM_ID,
        "roles": [ROLE_MANAGER_ID],
    },
    {
        "id": USER_ACCOUNTANT_ID,
        "email": "accountant@toshkent-broiler.uz",
        "full_name": "Nazarova Mohira Tursunovna",
        "phone": "+998 90 400 66 77",
        "hashed_password": hash_password("Accountant123!"),
        "is_active": True,
        "is_superuser": False,
        "farm_id": FARM_ID,
        "roles": [ROLE_ACCOUNTANT_ID],
    },
    {
        "id": USER_WORKER_ID,
        "email": "worker1@toshkent-broiler.uz",
        "full_name": "Toshmatov Jamshid Normatovich",
        "phone": "+998 93 500 88 99",
        "hashed_password": hash_password("Worker123!"),
        "is_active": True,
        "is_superuser": False,
        "farm_id": FARM_ID,
        "roles": [ROLE_WORKER_ID],
    },
    {
        "id": USER_VET_ID,
        "email": "vet@toshkent-broiler.uz",
        "full_name": "Mirzayev Sanjar Abdullayevich",
        "phone": "+998 91 600 11 22",
        "hashed_password": hash_password("Vet123!"),
        "is_active": True,
        "is_superuser": False,
        "farm_id": FARM_ID,
        "roles": [ROLE_VET_ID],
    },
]


async def run(conn: asyncpg.Connection) -> None:
    print("  → Farm reference...")
    await conn.execute("""
        INSERT INTO farms_ref (id, name, created_at, updated_at)
        VALUES ($1, $2, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """, FARM_ID, "Toshkent Broiler Ferma")

    print("  → Roles...")
    for role_id, name, display_name, is_system in ROLES:
        await conn.execute("""
            INSERT INTO roles (id, name, display_name, is_system, created_at, updated_at, created_by, updated_by)
            VALUES ($1, $2, $3, $4, NOW(), NOW(), $5, $5)
            ON CONFLICT (id) DO NOTHING
        """, role_id, name, display_name, is_system, USER_SUPER_ADMIN_ID)

    print("  → Role permissions...")
    import uuid
    for role_id, module, action in ROLE_PERMISSIONS:
        await conn.execute("""
            INSERT INTO role_permissions (id, role_id, module, action)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """, uuid.uuid4(), role_id, module, action)

    print("  → Users...")
    for u in USERS:
        await conn.execute("""
            INSERT INTO users (id, email, phone, full_name, hashed_password,
                               is_active, is_superuser, failed_login_attempts, is_locked,
                               farm_id, created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,0,false,$8,NOW(),NOW(),$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, u["id"], u["email"], u["phone"], u["full_name"], u["hashed_password"],
             u["is_active"], u["is_superuser"], u["farm_id"], USER_SUPER_ADMIN_ID)

    print("  → User-role assignments...")
    for u in USERS:
        for role_id in u["roles"]:
            await conn.execute("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """, u["id"], role_id)

    print("  ✓ identity-service seeded")


async def main():
    print("\n[identity-service]")
    conn = await connect("identity")
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
