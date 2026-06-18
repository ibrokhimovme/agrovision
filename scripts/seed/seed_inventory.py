"""
Inventory Service Seed
=======================
Creates: 2 warehouses, 7 stock items, 7 stock batches, stock movements.

Warehouses:
  1. Asosiy ozuqa ombori (feed warehouse)
  2. Veterinariya ombori  (medicine/vaccine warehouse)

Stock items (current quantity reflects AFTER batch B-2026-001 consumption):
  Feed warehouse:
    - BSK starter yemi:  1900 kg remaining (4000 received - 2100 used)
    - O'sish yemi:       2450 kg remaining (14000 received - 11550 used)
    - Tugallash yemi:    1400 kg remaining (7000 received - 5600 used)
  Vet warehouse:
    - IBD vaksinasi:     10 ml remaining (60 received - 50 used)
    - Newcastle vaksinasi: 10 ml remaining (60 received - 50 used)
    - Vitamin AD3E:      350 ml remaining (500 received - 150 used)
    - Enrofloxacin 10%:  120 ml remaining (200 received - 80 used)

Stock movements:
  - Receipt movements (March 27, 2026 — before batch arrival)
  - Dispatch movements (weekly aggregates for feed, single events for vaccines)
"""
import asyncio
import asyncpg
import uuid
from decimal import Decimal
from config import *


async def run(conn: asyncpg.Connection) -> None:
    # Clean up child records before re-seeding
    item_ids = [
        ITEM_STARTER_ID, ITEM_GROWER_ID, ITEM_FINISHER_ID,
        ITEM_IBD_VACCINE_ID, ITEM_NDV_VACCINE_ID, ITEM_VITAMIN_ID,
        ITEM_ANTIBIO_ID, ITEM_IB_VACCINE_ID,
    ]
    await conn.execute(
        "DELETE FROM stock_movements WHERE stock_item_id = ANY($1::uuid[])", item_ids
    )
    await conn.execute(
        "DELETE FROM stock_batches WHERE stock_item_id = ANY($1::uuid[])", item_ids
    )

    print("  → Warehouses...")
    warehouses = [
        (WAREHOUSE_FEED_ID, FARM_ID,
         "Asosiy ozuqa ombori",
         "Broiler 1-xona yonida, №3 bino",
         "Yem-xashak saqlanadigan asosiy ombor. Quruq, shamollatilgan."),
        (WAREHOUSE_VET_ID, FARM_ID,
         "Veterinariya ombori",
         "Ozuqa ombori binosida",
         "Vaksinalar, dorilar va veterinariya jihozlari uchun maxsus ombor. +4°C saqlash."),
    ]
    for wh in warehouses:
        await conn.execute("""
            INSERT INTO warehouses (id, farm_id, name, location, is_active, notes,
                                    created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,true,$5,$6,$6,$7,$7)
            ON CONFLICT (id) DO NOTHING
        """, *wh, FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    print("  → Stock items...")
    items = [
        # (id, warehouse_id, name, item_type, unit, current_qty, minimum_qty, unit_cost, sku)
        (ITEM_STARTER_ID,   WAREHOUSE_FEED_ID,
         "BSK starter yemi (0-14 kun)", "feed", "kg",
         STARTER_FEED_REMAIN,  "500.0000", "2200.00",  "FEED-BSK-001"),
        (ITEM_GROWER_ID,    WAREHOUSE_FEED_ID,
         "O'sish yemi (Grower 15-35 kun)", "feed", "kg",
         GROWER_FEED_REMAIN,   "1000.0000", "2000.00", "FEED-GRW-001"),
        (ITEM_FINISHER_ID,  WAREHOUSE_FEED_ID,
         "Tugallash yemi (Finisher 36-42 kun)", "feed", "kg",
         FINISHER_FEED_REMAIN, "500.0000", "1800.00",  "FEED-FIN-001"),
        (ITEM_IBD_VACCINE_ID, WAREHOUSE_VET_ID,
         "IBD (Gumboro) vaksinasi", "vaccine", "ml",
         IBD_VACCINE_REMAIN, "20.0000", "83333.33",    "VAC-IBD-001"),
        (ITEM_NDV_VACCINE_ID, WAREHOUSE_VET_ID,
         "Newcastle (ND) vaksinasi", "vaccine", "ml",
         NDV_VACCINE_REMAIN, "20.0000", "50000.00",    "VAC-NDV-001"),
        (ITEM_VITAMIN_ID,   WAREHOUSE_VET_ID,
         "Vitamin AD3E (300 000 IU/ml)", "medicine", "ml",
         VITAMIN_REMAIN,  "100.0000", "3000.00",       "MED-VIT-001"),
        (ITEM_ANTIBIO_ID,   WAREHOUSE_VET_ID,
         "Enrofloxacin 10% (antibiotik)", "medicine", "ml",
         ANTIBIO_REMAIN,  "50.0000", "10000.00",       "MED-ENR-001"),
        (ITEM_IB_VACCINE_ID, WAREHOUSE_VET_ID,
         "Infeksion bronxit (IB) vaksinasi", "vaccine", "ml",
         IB_VACCINE_REMAIN, "20.0000", "58333.33",     "VAC-IB-001"),
    ]
    for item in items:
        await conn.execute("""
            INSERT INTO stock_items
              (id, warehouse_id, name, item_type, unit,
               current_quantity, minimum_quantity, unit_cost, sku, is_active,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,true,$10,$10,$11,$11)
            ON CONFLICT (id) DO NOTHING
        """, *item, FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    print("  → Stock batches (received lots)...")
    stock_batches = [
        # (id, stock_item_id, batch_number, qty, remaining, unit_cost, received_at, expiry_date)
        (uuid.uuid4(), ITEM_STARTER_ID,   "BSK-2026-03",
         "4000.0000", STARTER_FEED_REMAIN, "2200.00",
         FARM_SETUP_DATE, d(60)),       # expires +60 days from batch arrival
        (uuid.uuid4(), ITEM_GROWER_ID,    "GRW-2026-03",
         "14000.0000", GROWER_FEED_REMAIN, "2000.00",
         FARM_SETUP_DATE, d(90)),
        (uuid.uuid4(), ITEM_FINISHER_ID,  "FIN-2026-03",
         "7000.0000", FINISHER_FEED_REMAIN, "1800.00",
         FARM_SETUP_DATE, d(90)),
        (uuid.uuid4(), ITEM_IBD_VACCINE_ID, "IBD-LOT-2026-A",
         IBD_VACCINE_INITIAL, IBD_VACCINE_REMAIN, "83333.33",
         FARM_SETUP_DATE, d(365)),     # 1 year expiry for vaccines
        (uuid.uuid4(), ITEM_NDV_VACCINE_ID, "NDV-LOT-2026-A",
         NDV_VACCINE_INITIAL, NDV_VACCINE_REMAIN, "50000.00",
         FARM_SETUP_DATE, d(365)),
        (uuid.uuid4(), ITEM_VITAMIN_ID,   "VIT-2026-03",
         VITAMIN_INITIAL, VITAMIN_REMAIN, "3000.00",
         FARM_SETUP_DATE, d(180)),
        (uuid.uuid4(), ITEM_ANTIBIO_ID,   "ENR-2026-03",
         ANTIBIO_INITIAL, ANTIBIO_REMAIN, "10000.00",
         FARM_SETUP_DATE, d(180)),
        (uuid.uuid4(), ITEM_IB_VACCINE_ID, "IB-LOT-2026-A",
         IB_VACCINE_INITIAL, IB_VACCINE_REMAIN, "58333.33",
         FARM_SETUP_DATE, d(365)),
    ]
    for sb in stock_batches:
        await conn.execute("""
            INSERT INTO stock_batches
              (id, stock_item_id, batch_number, quantity, remaining_quantity,
               unit_cost, received_at, expiry_date,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$7,$7,$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, *sb, USER_MANAGER_ID)

    print("  → Stock movements (receipts + dispatches)...")

    # Receipt movements — when inventory was initially received
    receipts = [
        (ITEM_STARTER_ID,   WAREHOUSE_FEED_ID, "4000.0000", "kg",   "2200.00",
         "receipt", "Ozuqa yetkazib beruvchi: Toshkent Agro Savdo MChJ",
         "Mart 2026 tsikl uchun starter yem qabul qilindi", FARM_SETUP_DATE),
        (ITEM_GROWER_ID,    WAREHOUSE_FEED_ID, "14000.0000", "kg",  "2000.00",
         "receipt", "Ozuqa yetkazib beruvchi: Toshkent Agro Savdo MChJ",
         "Mart 2026 tsikl uchun grower yem qabul qilindi", FARM_SETUP_DATE),
        (ITEM_FINISHER_ID,  WAREHOUSE_FEED_ID, "7000.0000", "kg",   "1800.00",
         "receipt", "Ozuqa yetkazib beruvchi: Toshkent Agro Savdo MChJ",
         "Mart 2026 tsikl uchun finisher yem qabul qilindi", FARM_SETUP_DATE),
        (ITEM_IBD_VACCINE_ID, WAREHOUSE_VET_ID, IBD_VACCINE_INITIAL, "ml", "83333.33",
         "receipt", "Veterinariya ta'minotchisi: UzVetPharma",
         "IBD vaksinasi qabul qilindi", FARM_SETUP_DATE),
        (ITEM_NDV_VACCINE_ID, WAREHOUSE_VET_ID, NDV_VACCINE_INITIAL, "ml", "50000.00",
         "receipt", "Veterinariya ta'minotchisi: UzVetPharma",
         "Newcastle vaksinasi qabul qilindi", FARM_SETUP_DATE),
        (ITEM_VITAMIN_ID,   WAREHOUSE_VET_ID, VITAMIN_INITIAL, "ml", "3000.00",
         "receipt", "Veterinariya ta'minotchisi: UzVetPharma",
         "Vitamin AD3E qabul qilindi", FARM_SETUP_DATE),
        (ITEM_ANTIBIO_ID,   WAREHOUSE_VET_ID, ANTIBIO_INITIAL, "ml", "10000.00",
         "receipt", "Veterinariya ta'minotchisi: UzVetPharma",
         "Enrofloxacin 10% qabul qilindi", FARM_SETUP_DATE),
        (ITEM_IB_VACCINE_ID, WAREHOUSE_VET_ID, IB_VACCINE_INITIAL, "ml", "58333.33",
         "receipt", "Veterinariya ta'minotchisi: UzVetPharma",
         "IB vaksinasi qabul qilindi", FARM_SETUP_DATE),
    ]
    for item_id, wh_id, qty, unit, cost, mv_type, purpose, notes, moved_at in receipts:
        await conn.execute("""
            INSERT INTO stock_movements
              (id, stock_item_id, warehouse_id, movement_type, quantity, unit,
               unit_cost, purpose, reference_id, reference_type, notes, moved_at,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,NULL,NULL,$9,$10,$10,$10,$11,$11)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), item_id, wh_id, mv_type,
             Decimal(qty), unit, Decimal(cost), purpose, notes, moved_at,
             USER_MANAGER_ID)

    # Dispatch movements — weekly feed usage aggregated
    feed_dispatches = [
        # (item_id, week_label, qty_kg, day_offset, purpose)
        (ITEM_STARTER_ID, "1-hafta starter yemi (kun 1-7)",   "525.000",  7),
        (ITEM_STARTER_ID, "2-hafta starter yemi (kun 8-14)",  "1575.000", 14),
        (ITEM_GROWER_ID,  "3-hafta grower yemi (kun 15-21)",  "2380.000", 21),
        (ITEM_GROWER_ID,  "4-hafta grower yemi (kun 22-28)",  "3430.000", 28),
        (ITEM_GROWER_ID,  "5-hafta grower yemi (kun 29-35)",  "4550.000", 35),
        (ITEM_FINISHER_ID,"6-hafta finisher yemi (kun 36-42)","5600.000", 42),
    ]
    for item_id, label, qty, day in feed_dispatches:
        await conn.execute("""
            INSERT INTO stock_movements
              (id, stock_item_id, warehouse_id, movement_type, quantity, unit,
               purpose, reference_id, reference_type, notes, moved_at,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,'dispatch',$4,'kg',
                    $5,$6,'batch',
                    'B-2026-001 partiyasi uchun sarflandi',$7,$7,$7,$8,$8)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), item_id, WAREHOUSE_FEED_ID,
             Decimal(qty), label, BATCH_A_ID, d(day), USER_WORKER_ID)

    # Dispatch movements — vaccine and medicine usage
    vet_dispatches = [
        (ITEM_IBD_VACCINE_ID, WAREHOUSE_VET_ID, IBD_VACCINE_USED, "ml",
         "IBD vaksinatsiyasi — partiya B-2026-001", d(14)),
        (ITEM_NDV_VACCINE_ID, WAREHOUSE_VET_ID, NDV_VACCINE_USED, "ml",
         "Newcastle vaksinatsiyasi — partiya B-2026-001", d(21)),
        (ITEM_VITAMIN_ID,     WAREHOUSE_VET_ID, VITAMIN_USED, "ml",
         "Vitamin AD3E profilaktikasi — partiya B-2026-001", d(5)),
        (ITEM_ANTIBIO_ID,     WAREHOUSE_VET_ID, ANTIBIO_USED, "ml",
         "Enrofloxacin muolajasi — nafas yo'llari kasalligi, B-2026-001", d(11)),
        (ITEM_IB_VACCINE_ID,  WAREHOUSE_VET_ID, IB_VACCINE_USED, "ml",
         "IB vaksinatsiyasi — partiya B-2026-001", d(28)),
    ]
    for item_id, wh_id, qty, unit, purpose, moved_at in vet_dispatches:
        await conn.execute("""
            INSERT INTO stock_movements
              (id, stock_item_id, warehouse_id, movement_type, quantity, unit,
               purpose, reference_id, reference_type, notes, moved_at,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,'dispatch',$4,$5,$6,$7,'batch',
                    'B-2026-001 partiyasi uchun sarflandi',$8,$8,$8,$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), item_id, wh_id,
             Decimal(qty), unit, purpose, BATCH_A_ID, moved_at, USER_VET_ID)

    print("  ✓ inventory-service seeded")


async def main():
    print("\n[inventory-service]")
    conn = await connect("inventory")
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
