"""
Farm Service Seed
==================
Creates: 1 farm, 3 buildings, 3 sections.

Farm: Toshkent Broiler Ferma
  Building 1: Karantin bloki      → Section: Karantin bo'limi (quarantine)
  Building 2: Broiler 1-xona      → Section A: A-sektor (production, 2500)
                                  → Section B: B-sektor (production, 2500)
  Building 3: Ozuqa ombori binosi → (storage building, no sections)
"""
import asyncio
import asyncpg
from config import *


async def run(conn: asyncpg.Connection) -> None:
    print("  → Farm...")
    await conn.execute("""
        INSERT INTO farms (id, name, farm_type, address, region,
                           owner_user_id, is_active, notes,
                           created_at, updated_at, created_by, updated_by)
        VALUES ($1,$2,'poultry',
                'Chirchiq tumani, Toshkent viloyati, O''zbekiston',
                'Toshkent viloyati',
                $3, true,
                '5000 bosh broiler parrandasi yetishtirishga ixtisoslashgan zamonaviy ferma. Yiliga 4 aylanma tsikl.',
                $4, $4, $5, $5)
        ON CONFLICT (id) DO NOTHING
    """, FARM_ID, "Toshkent Broiler Ferma", USER_FARM_OWNER_ID,
         FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    print("  → Buildings...")
    buildings = [
        (BUILDING_QUARANTINE_ID, FARM_ID, "Karantin bloki",     500,
         "Yangi kelgan jo'jalar uchun 7 kunlik karantin xonasi"),
        (BUILDING_BROILER_1_ID,  FARM_ID, "Broiler 1-xona",     5000,
         "Asosiy broiler o'stiriladigan xona. Ikki sektorga bo'lingan."),
        (BUILDING_STORAGE_ID,    FARM_ID, "Ozuqa ombori binosi", None,
         "Yem-xashak va veterinariya preparatlari saqlanadigan bino"),
    ]
    for b in buildings:
        await conn.execute("""
            INSERT INTO buildings (id, farm_id, name, capacity, notes,
                                   created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$6,$7,$7)
            ON CONFLICT (id) DO NOTHING
        """, *b, FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    print("  → Sections...")
    sections = [
        (SECTION_QUARANTINE_ID, BUILDING_QUARANTINE_ID, FARM_ID,
         "Karantin bo'limi", "quarantine", 500),
        (SECTION_PROD_A_ID,     BUILDING_BROILER_1_ID,  FARM_ID,
         "A-sektor",          "production", 2500),
        (SECTION_PROD_B_ID,     BUILDING_BROILER_1_ID,  FARM_ID,
         "B-sektor",          "production", 2500),
    ]
    for s in sections:
        await conn.execute("""
            INSERT INTO sections (id, building_id, farm_id, name, section_type,
                                  capacity, is_active,
                                  created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,true,$7,$7,$8,$8)
            ON CONFLICT (id) DO NOTHING
        """, *s, FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    print("  ✓ farm-service seeded")


async def main():
    print("\n[farm-service]")
    conn = await asyncpg.connect(DATABASES["farm"])
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
