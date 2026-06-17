"""
AgroVision Seed Runner
=======================
Runs all service seeds in the correct dependency order, then verifies.

Order:
  1. identity-service  (no dependencies)
  2. farm-service      (references identity UUIDs in owner_user_id)
  3. livestock-service (references farm_id, user IDs)
  4. inventory-service (references farm_id, user IDs, batch_id via movements)
  5. finance-service   (references farm_id, batch_id, user IDs)
  6. notification-service (references user IDs, farm_id, batch_id)
  7. verify            (cross-checks all services)

Usage:
  # Default (localhost:5432, password agrovision_dev)
  python run_all.py

  # Against Docker (if port 5433 is mapped)
  POSTGRES_PORT=5433 python run_all.py

  # Against running Docker containers from inside Docker network
  POSTGRES_HOST=postgres python run_all.py
"""
import asyncio
import sys
import os

# Ensure config.py is on path when running from repo root
sys.path.insert(0, os.path.dirname(__file__))

import asyncpg
from config import DATABASES

from seed_identity     import run as seed_identity,     main as _m1
from seed_farm         import run as seed_farm,         main as _m2
from seed_livestock    import run as seed_livestock,    main as _m3
from seed_inventory    import run as seed_inventory,    main as _m4
from seed_finance      import run as seed_finance,      main as _m5
from seed_notifications import run as seed_notifications, main as _m6
from verify            import main as verify_all


async def wait_for_db(svc: str, dsn: str, retries: int = 10) -> bool:
    for i in range(retries):
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            return True
        except Exception:
            if i < retries - 1:
                print(f"  Waiting for {svc} database... ({i+1}/{retries})")
                await asyncio.sleep(2)
    return False


async def main():
    print("=" * 60)
    print("AgroVision Development Seed")
    print("=" * 60)
    print(f"Target: {DATABASES['identity'].split('@')[1].split('/')[0]}")
    print()

    print("Checking database connectivity...")
    all_ready = True
    for svc, dsn in DATABASES.items():
        ready = await wait_for_db(svc, dsn)
        if ready:
            print(f"  ✓ {svc}-db")
        else:
            print(f"  ✗ {svc}-db — cannot connect. Is the database running?")
            all_ready = False

    if not all_ready:
        print("\nNot all databases are reachable. Run `docker compose up -d` first.")
        sys.exit(1)

    print()
    steps = [
        ("identity",      DATABASES["identity"],     seed_identity),
        ("farm",          DATABASES["farm"],          seed_farm),
        ("livestock",     DATABASES["livestock"],     seed_livestock),
        ("inventory",     DATABASES["inventory"],     seed_inventory),
        ("finance",       DATABASES["finance"],       seed_finance),
        ("notification",  DATABASES["notification"],  seed_notifications),
    ]

    for svc, dsn, seed_fn in steps:
        print(f"\n[{svc}-service]")
        try:
            conn = await asyncpg.connect(dsn)
            await seed_fn(conn)
            await conn.close()
        except Exception as e:
            print(f"  ✗ Error seeding {svc}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    print("\n")
    await verify_all()

    print("\n✓ Seed complete. Application is ready to use.")
    print()
    print("Login credentials:")
    print("  admin@agrovision.uz         → Admin123!")
    print("  owner@toshkent-broiler.uz   → Owner123!")
    print("  manager@toshkent-broiler.uz → Manager123!")
    print("  accountant@toshkent-broiler.uz → Accountant123!")
    print("  worker1@toshkent-broiler.uz → Worker123!")
    print("  vet@toshkent-broiler.uz     → Vet123!")


if __name__ == "__main__":
    asyncio.run(main())
