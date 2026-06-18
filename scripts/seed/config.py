"""
AgroVision Seed Configuration
==============================
All hardcoded UUIDs and constants for cross-service referential integrity.

Business Scenario: Toshkent Broiler Ferma
  - 5000 broiler chicks arrived April 6, 2026
  - Quarantine until April 13, 2026
  - Active production April 13 – May 18, 2026 (42 days)
  - Sold May 18, 2026 → batch CLOSED
  - Full lifecycle data: feed, mortality, vaccinations, expenses, profit
"""
from uuid import UUID
from datetime import datetime, timezone, date, timedelta
import os

# ── Database connection ────────────────────────────────────────────────────────
#
# M7 (2026-06-18): the 7 per-service databases this module used to target were
# dropped (migrated into the single `agrovision` database, one schema per
# module — see .project-governance/monolith-migration/). DATABASES now holds
# the same DSN for every key; SCHEMAS maps each key to its schema so callers
# can open a connection with the right `search_path` via `connect()` below.

import asyncpg

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "agrovision")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "agrovision_dev")
POSTGRES_DB = os.getenv("POSTGRES_DB", "agrovision")

_AGROVISION_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

DATABASES = {
    "identity":     _AGROVISION_DSN,
    "farm":         _AGROVISION_DSN,
    "livestock":    _AGROVISION_DSN,
    "inventory":    _AGROVISION_DSN,
    "finance":      _AGROVISION_DSN,
    "notification": _AGROVISION_DSN,
}

SCHEMAS = {
    "identity":     "identity",
    "farm":         "farm",
    "livestock":    "poultry",
    "inventory":    "inventory",
    "finance":      "finance",
    "notification": "notifications",
}


async def connect(key: str) -> asyncpg.Connection:
    """Open a connection to the consolidated DB with search_path set to the module's schema."""
    return await asyncpg.connect(DATABASES[key], server_settings={"search_path": SCHEMAS[key]})

# ── Hardcoded UUIDs ────────────────────────────────────────────────────────────
# Format: descriptive prefix + service-unique suffix

# Identity — Users
USER_SUPER_ADMIN_ID  = UUID("aaaaaaaa-0001-0000-0000-000000000001")
USER_FARM_OWNER_ID   = UUID("aaaaaaaa-0001-0000-0000-000000000002")
USER_MANAGER_ID      = UUID("aaaaaaaa-0001-0000-0000-000000000003")
USER_ACCOUNTANT_ID   = UUID("aaaaaaaa-0001-0000-0000-000000000004")
USER_WORKER_ID       = UUID("aaaaaaaa-0001-0000-0000-000000000005")
USER_VET_ID          = UUID("aaaaaaaa-0001-0000-0000-000000000006")

# Identity — Roles
ROLE_SUPER_ADMIN_ID  = UUID("bbbbbbbb-0002-0000-0000-000000000001")
ROLE_FARM_OWNER_ID   = UUID("bbbbbbbb-0002-0000-0000-000000000002")
ROLE_MANAGER_ID      = UUID("bbbbbbbb-0002-0000-0000-000000000003")
ROLE_ACCOUNTANT_ID   = UUID("bbbbbbbb-0002-0000-0000-000000000004")
ROLE_WORKER_ID       = UUID("bbbbbbbb-0002-0000-0000-000000000005")
ROLE_VET_ID          = UUID("bbbbbbbb-0002-0000-0000-000000000006")

# Farm
FARM_ID              = UUID("cccccccc-0003-0000-0000-000000000001")
BUILDING_QUARANTINE_ID = UUID("cccccccc-0003-0000-0000-000000000002")
BUILDING_BROILER_1_ID  = UUID("cccccccc-0003-0000-0000-000000000003")
BUILDING_STORAGE_ID    = UUID("cccccccc-0003-0000-0000-000000000004")
SECTION_QUARANTINE_ID  = UUID("cccccccc-0003-0000-0000-000000000005")
SECTION_PROD_A_ID      = UUID("cccccccc-0003-0000-0000-000000000006")
SECTION_PROD_B_ID      = UUID("cccccccc-0003-0000-0000-000000000007")

# Livestock
BATCH_A_ID           = UUID("dddddddd-0004-0000-0000-000000000001")
VACC_SCHEDULE_IBD_ID    = UUID("dddddddd-0004-0000-0000-000000000010")
VACC_SCHEDULE_NDV_ID    = UUID("dddddddd-0004-0000-0000-000000000011")
VACC_SCHEDULE_IB_ID     = UUID("dddddddd-0004-0000-0000-000000000012")

# Inventory
WAREHOUSE_FEED_ID    = UUID("eeeeeeee-0005-0000-0000-000000000001")
WAREHOUSE_VET_ID     = UUID("eeeeeeee-0005-0000-0000-000000000002")

ITEM_STARTER_ID      = UUID("eeeeeeee-0005-0000-0000-000000000010")
ITEM_GROWER_ID       = UUID("eeeeeeee-0005-0000-0000-000000000011")
ITEM_FINISHER_ID     = UUID("eeeeeeee-0005-0000-0000-000000000012")
ITEM_IBD_VACCINE_ID  = UUID("eeeeeeee-0005-0000-0000-000000000013")
ITEM_NDV_VACCINE_ID  = UUID("eeeeeeee-0005-0000-0000-000000000014")
ITEM_VITAMIN_ID      = UUID("eeeeeeee-0005-0000-0000-000000000015")
ITEM_ANTIBIO_ID      = UUID("eeeeeeee-0005-0000-0000-000000000016")
ITEM_IB_VACCINE_ID   = UUID("eeeeeeee-0005-0000-0000-000000000017")

# Finance
CUSTOMER_ID          = UUID("ffffffff-0006-0000-0000-000000000001")
SALE_RECORD_ID       = UUID("ffffffff-0006-0000-0000-000000000002")

# ── Business timeline ──────────────────────────────────────────────────────────

def d(offset_from_batch: int) -> datetime:
    """Returns UTC datetime relative to batch placement date."""
    base = datetime(2026, 4, 6, 8, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(days=offset_from_batch)


BATCH_ARRIVAL    = d(0)   # April 6, 2026
BATCH_ACTIVATED  = d(7)   # April 13, 2026 (quarantine end)
BATCH_CLOSED     = d(42)  # May 18, 2026
FARM_SETUP_DATE  = d(-10) # March 27, 2026 — farm setup / inventory received

# ── Business constants ─────────────────────────────────────────────────────────

INITIAL_CHICK_COUNT   = 5000
CHICK_PRICE_PER_HEAD  = "4500.00"   # UZS
TOTAL_MORTALITY       = 42
CURRENT_COUNT         = INITIAL_CHICK_COUNT - TOTAL_MORTALITY  # 4958

BIRDS_SOLD            = 4900
SALE_AVG_WEIGHT_KG    = "2.80"
SALE_QUANTITY_KG      = "13720.000"  # 4900 × 2.80
SALE_PRICE_PER_KG     = "24000.00"
SALE_TOTAL_REVENUE    = "329280000.00"  # 13720 × 24000

# Feed quantities used (matches feed records below)
STARTER_FEED_INITIAL  = "4000.000"   # kg received
GROWER_FEED_INITIAL   = "14000.000"  # kg received
FINISHER_FEED_INITIAL = "7000.000"   # kg received

STARTER_FEED_USED     = "2100.000"   # kg (weeks 1-2)
GROWER_FEED_USED      = "11550.000"  # kg (weeks 3-5)
FINISHER_FEED_USED    = "5600.000"   # kg (week 6)

STARTER_FEED_REMAIN   = "1900.000"   # 4000 - 2100
GROWER_FEED_REMAIN    = "2450.000"   # 14000 - 11550
FINISHER_FEED_REMAIN  = "1400.000"   # 7000 - 5600

IBD_VACCINE_INITIAL   = "60.0000"    # ml
NDV_VACCINE_INITIAL   = "60.0000"    # ml
IB_VACCINE_INITIAL    = "60.0000"    # ml
VITAMIN_INITIAL       = "500.0000"   # ml
ANTIBIO_INITIAL       = "200.0000"   # ml

IBD_VACCINE_USED      = "50.0000"    # ml
NDV_VACCINE_USED      = "50.0000"    # ml
IB_VACCINE_USED       = "50.0000"    # ml
VITAMIN_USED          = "150.0000"   # ml
ANTIBIO_USED          = "80.0000"    # ml

IBD_VACCINE_REMAIN    = "10.0000"
NDV_VACCINE_REMAIN    = "10.0000"
IB_VACCINE_REMAIN     = "10.0000"
VITAMIN_REMAIN        = "350.0000"
ANTIBIO_REMAIN        = "120.0000"
