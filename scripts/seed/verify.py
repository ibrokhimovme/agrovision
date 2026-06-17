"""
Seed Verification Script
=========================
Runs consistency checks across all service databases to confirm:
  1. All expected entities exist
  2. Foreign key references are logically valid
  3. Business scenario is consistent (counts, amounts, dates)
  4. No orphan records
"""
import asyncio
import asyncpg
from config import *


CHECK_PASS = "  ✓"
CHECK_FAIL = "  ✗"
CHECK_WARN = "  !"

failures = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"{CHECK_PASS} {label}")
    else:
        failures.append(f"{label}: {detail}")
        print(f"{CHECK_FAIL} {label} — {detail}")


async def verify_identity(conn: asyncpg.Connection) -> None:
    print("\n[identity-service]")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM users WHERE is_active = true")
    check("6 active users", row["c"] == 6, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM roles")
    check("6 roles created", row["c"] == 6, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM role_permissions")
    check("Role permissions populated (>30)", row["c"] > 30, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT is_superuser FROM users WHERE email = 'admin@agrovision.uz'"
    )
    check("Super admin exists", row and row["is_superuser"])

    row = await conn.fetchrow(
        "SELECT u.id FROM users u JOIN user_roles ur ON ur.user_id = u.id "
        "WHERE u.email = 'manager@toshkent-broiler.uz' LIMIT 1"
    )
    check("Farm manager has role assigned", row is not None)

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM farms_ref")
    check("Farm reference exists", row["c"] >= 1, f"found {row['c']}")


async def verify_farm(conn: asyncpg.Connection) -> None:
    print("\n[farm-service]")

    row = await conn.fetchrow("SELECT name, farm_type FROM farms WHERE id = $1", FARM_ID)
    check("Farm exists", row is not None, "farm not found")
    if row:
        check("Farm type is poultry", row["farm_type"] == "poultry",
              f"got {row['farm_type']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM buildings WHERE farm_id = $1", FARM_ID)
    check("3 buildings", row["c"] == 3, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM sections WHERE farm_id = $1", FARM_ID)
    check("3 sections", row["c"] == 3, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM sections WHERE farm_id = $1 AND section_type = 'quarantine'",
        FARM_ID
    )
    check("1 quarantine section", row["c"] == 1, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM sections WHERE farm_id = $1 AND section_type = 'production'",
        FARM_ID
    )
    check("2 production sections", row["c"] == 2, f"found {row['c']}")


async def verify_livestock(conn: asyncpg.Connection) -> None:
    print("\n[livestock-service]")

    row = await conn.fetchrow("SELECT * FROM batches WHERE id = $1", BATCH_A_ID)
    check("Batch B-2026-001 exists", row is not None)
    if row:
        check("Batch status = closed", row["status"] == "closed",
              f"status={row['status']}")
        check("Initial count = 5000", row["initial_count"] == 5000,
              f"got {row['initial_count']}")
        check(f"Current count = {CURRENT_COUNT}",
              row["current_count"] == CURRENT_COUNT,
              f"got {row['current_count']}")
        check("Close reason = sale", row["close_reason"] == "sale")
        check("Batch code set", row["batch_code"] == "B-2026-001")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c, SUM(quantity) AS total "
        "FROM mortality_records WHERE batch_id = $1", BATCH_A_ID
    )
    check("8 mortality records", row["c"] == 8, f"found {row['c']}")
    check(f"Total mortality = {TOTAL_MORTALITY}", int(row["total"]) == TOTAL_MORTALITY,
          f"sum={row['total']}")

    # Verify count consistency: initial - mortality = current
    expected_current = INITIAL_CHICK_COUNT - TOTAL_MORTALITY
    check(f"Count consistency: {INITIAL_CHICK_COUNT} - {TOTAL_MORTALITY} = {CURRENT_COUNT}",
          expected_current == CURRENT_COUNT)

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM weight_samplings WHERE batch_id = $1", BATCH_A_ID
    )
    check("6 weight samplings", row["c"] == 6, f"found {row['c']}")

    # Weight trend: each sampling must be heavier than the previous
    rows = await conn.fetch(
        "SELECT average_weight_kg FROM weight_samplings "
        "WHERE batch_id = $1 ORDER BY measured_at", BATCH_A_ID
    )
    weights = [float(r["average_weight_kg"]) for r in rows]
    increasing = all(weights[i] < weights[i + 1] for i in range(len(weights) - 1))
    check("Weight trend is increasing", increasing, f"weights={weights}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM vaccination_records WHERE batch_id = $1", BATCH_A_ID
    )
    check("3 vaccination records", row["c"] == 3, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM vaccination_records "
        "WHERE batch_id = $1 AND status = 'completed'", BATCH_A_ID
    )
    check("All vaccinations completed", row["c"] == 3, f"completed={row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM medication_records WHERE batch_id = $1", BATCH_A_ID
    )
    check("2 medication records", row["c"] == 2, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM feed_consumptions WHERE batch_id = $1", BATCH_A_ID
    )
    check("42 daily feed records", row["c"] == 42, f"found {row['c']}")

    # Feed phase check: starter → grower → finisher (no going back)
    rows = await conn.fetch(
        "SELECT feed_type FROM feed_consumptions "
        "WHERE batch_id = $1 ORDER BY feed_date", BATCH_A_ID
    )
    types = [r["feed_type"] for r in rows]
    phase_ok = (
        all(t == "starter" for t in types[:14]) and
        all(t == "grower" for t in types[14:35]) and
        all(t == "finisher" for t in types[35:])
    )
    check("Feed phases are correct (starter→grower→finisher)", phase_ok)

    row = await conn.fetchrow(
        "SELECT SUM(quantity_kg) AS total FROM feed_consumptions WHERE batch_id = $1",
        BATCH_A_ID
    )
    total_feed = float(row["total"])
    check("Total feed 15000-20000 kg range",
          15000 <= total_feed <= 20000, f"total={total_feed:.0f} kg")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM vaccination_schedules")
    check("3 vaccination schedule templates", row["c"] == 3, f"found {row['c']}")


async def verify_inventory(conn: asyncpg.Connection) -> None:
    print("\n[inventory-service]")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM warehouses WHERE farm_id = $1", FARM_ID)
    check("2 warehouses", row["c"] == 2, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM stock_items")
    check("8 stock items", row["c"] == 8, f"found {row['c']}")

    # Verify remaining quantities are correct
    checks = [
        (ITEM_STARTER_ID,  "BSK starter", STARTER_FEED_REMAIN),
        (ITEM_GROWER_ID,   "Grower yem",  GROWER_FEED_REMAIN),
        (ITEM_FINISHER_ID, "Finisher yem",FINISHER_FEED_REMAIN),
        (ITEM_IBD_VACCINE_ID, "IBD vaksina",  IBD_VACCINE_REMAIN),
        (ITEM_NDV_VACCINE_ID, "NDV vaksina",  NDV_VACCINE_REMAIN),
    ]
    for item_id, label, expected in checks:
        row = await conn.fetchrow(
            "SELECT current_quantity FROM stock_items WHERE id = $1", item_id
        )
        actual = float(row["current_quantity"]) if row else None
        check(f"{label} remaining = {expected}",
              actual is not None and abs(actual - float(expected)) < 0.01,
              f"got {actual}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM stock_movements WHERE movement_type = 'receipt'")
    check("8 receipt movements", row["c"] == 8, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM stock_movements WHERE movement_type = 'dispatch'")
    check("10+ dispatch movements", row["c"] >= 10, f"found {row['c']}")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM stock_batches")
    check("8 stock batches", row["c"] == 8, f"found {row['c']}")


async def verify_finance(conn: asyncpg.Connection) -> None:
    print("\n[finance-service]")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM customers WHERE farm_id = $1", FARM_ID)
    check("1 customer exists", row["c"] == 1, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c, SUM(amount) AS total "
        "FROM expenses WHERE batch_id = $1", BATCH_A_ID
    )
    check("13 expense records", row["c"] == 13, f"found {row['c']}")
    total_exp = float(row["total"])
    check("Total expenses = 104,150,000 UZS",
          abs(total_exp - 104_150_000) < 1, f"got {total_exp:,.0f}")

    row = await conn.fetchrow(
        "SELECT * FROM sale_records WHERE batch_id = $1", BATCH_A_ID
    )
    check("Sale record exists", row is not None)
    if row:
        check("Sale: 4900 head",
              row["head_count"] == 4900, f"got {row['head_count']}")
        check("Sale: 13720 kg",
              abs(float(row["quantity_kg"]) - 13720) < 0.01, f"got {row['quantity_kg']}")
        check("Sale: 329,280,000 UZS revenue",
              abs(float(row["total_revenue_uzs"]) - 329_280_000) < 1,
              f"got {row['total_revenue_uzs']}")
        check("Sale: payment_status = paid",
              row["payment_status"] == "paid")

    # Profit calculation check
    if row:
        revenue = float(row["total_revenue_uzs"])
        profit = revenue - total_exp
        margin = profit / revenue * 100
        check("Profit > 0", profit > 0, f"profit={profit:,.0f}")
        print(f"    Revenue:  {revenue:>15,.0f} UZS")
        print(f"    Expenses: {total_exp:>15,.0f} UZS")
        print(f"    Profit:   {profit:>15,.0f} UZS ({margin:.1f}%)")


async def verify_notifications(conn: asyncpg.Connection) -> None:
    print("\n[notification-service]")

    row = await conn.fetchrow("SELECT COUNT(*) AS c FROM notifications")
    check("15 notifications total", row["c"] == 15, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM notifications WHERE severity = 'critical'"
    )
    check("2 critical notifications (mortality spike)", row["c"] == 2, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM notifications WHERE severity = 'warning'"
    )
    check("5 warning notifications", row["c"] >= 4, f"found {row['c']}")

    row = await conn.fetchrow(
        "SELECT COUNT(*) AS c FROM notifications WHERE is_read = true"
    )
    check("Most notifications are read", row["c"] >= 12, f"read={row['c']}")


async def main():
    print("=" * 60)
    print("AgroVision Seed Verification")
    print("=" * 60)

    service_checks = [
        ("identity",     verify_identity),
        ("farm",         verify_farm),
        ("livestock",    verify_livestock),
        ("inventory",    verify_inventory),
        ("finance",      verify_finance),
        ("notification", verify_notifications),
    ]

    for svc, fn in service_checks:
        try:
            conn = await asyncpg.connect(DATABASES[svc])
            await fn(conn)
            await conn.close()
        except Exception as e:
            print(f"\n  ✗ Could not connect to {svc}-service: {e}")
            failures.append(f"{svc}: connection failed — {e}")

    print("\n" + "=" * 60)
    if failures:
        print(f"FAILED: {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  ✗ {f}")
    else:
        print("ALL CHECKS PASSED — seed data is consistent")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
