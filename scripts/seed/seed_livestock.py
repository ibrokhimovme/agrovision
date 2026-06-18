"""
Livestock Service Seed
=======================
Creates the full lifecycle of Batch B-2026-001:
  - 1 batch (5000 broiler chicks → completed after sale)
  - 8 mortality records (total 42 dead)
  - 6 weight samplings (growth curve from 0.18 kg to 2.81 kg)
  - 3 vaccination schedules (IBD, Newcastle, IB)
  - 3 vaccination records (completed)
  - 2 medication records (vitamins + antibiotics)
  - 42 daily feed consumption records

Feed consumption design (by phase):
  Starter  (days  1-14): starts 75 kg/day → grows to 225 kg/day
  Grower   (days 15-35): starts 300 kg/day → grows to 700 kg/day
  Finisher (days 36-42): 780-820 kg/day
"""
import asyncio
import asyncpg
import uuid
from decimal import Decimal
from datetime import timedelta
from config import *


def dt(offset: int) -> "datetime":
    return d(offset)


async def run(conn: asyncpg.Connection) -> None:
    # Clean up child records before re-seeding (they use random UUIDs so ON CONFLICT won't dedup)
    await conn.execute("DELETE FROM feed_consumptions WHERE batch_id = $1", BATCH_A_ID)
    await conn.execute("DELETE FROM medication_records WHERE batch_id = $1", BATCH_A_ID)
    await conn.execute("DELETE FROM vaccination_records WHERE batch_id = $1", BATCH_A_ID)
    await conn.execute("DELETE FROM weight_samplings WHERE batch_id = $1", BATCH_A_ID)
    await conn.execute("DELETE FROM mortality_records WHERE batch_id = $1", BATCH_A_ID)

    print("  → Farm reference...")
    await conn.execute("""
        INSERT INTO farms_ref (id, name) VALUES ($1, $2)
        ON CONFLICT (id) DO NOTHING
    """, FARM_ID, "Toshkent Broiler Ferma")

    # ── Vaccination schedules (templates) ─────────────────────────────────────
    print("  → Vaccination schedules...")
    schedules = [
        (VACC_SCHEDULE_IBD_ID, FARM_ID, "broiler",
         "IBD (Gumboro) vaksinasi", 14, True,
         "Gumboro kasalligiga qarshi. Ichimlik suvi orqali beriladi."),
        (VACC_SCHEDULE_NDV_ID, FARM_ID, "broiler",
         "Newcastle (ND) vaksinasi", 21, True,
         "Nyukasl kasalligiga qarshi. Spray usulida beriladi."),
        (VACC_SCHEDULE_IB_ID,  FARM_ID, "broiler",
         "Infeksion bronxit (IB) vaksinasi", 28, True,
         "Infeksion bronxitga qarshi. Spray usulida beriladi."),
    ]
    for s in schedules:
        await conn.execute("""
            INSERT INTO vaccination_schedules
              (id, farm_id, species, vaccine_name, day_of_age,
               is_mandatory, notes, created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$8,$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, *s, FARM_SETUP_DATE, USER_SUPER_ADMIN_ID)

    # ── Batch ─────────────────────────────────────────────────────────────────
    print("  → Batch B-2026-001...")
    await conn.execute("""
        INSERT INTO batches
          (id, farm_id, section_id, species, status, batch_code,
           initial_count, current_count,
           placement_date, closed_at, close_reason,
           supplier_name, chick_price_per_head, notes,
           created_at, updated_at, created_by, updated_by)
        VALUES ($1,$2,$3,'broiler','completed','B-2026-001',
                $4,$5,
                $6,$7,'sale',
                'Samarqand Inkubator MChJ', 4500.00,
                'Aprel 2026 tsikli. Ross-308 zoti. FCR 1.38. Muvaffaqiyatli tsikl.',
                $6,$7,$8,$8)
        ON CONFLICT (id) DO NOTHING
    """, BATCH_A_ID, FARM_ID, SECTION_PROD_A_ID,
         INITIAL_CHICK_COUNT, CURRENT_COUNT,
         BATCH_ARRIVAL, BATCH_CLOSED,
         USER_MANAGER_ID)

    # ── Mortality records ──────────────────────────────────────────────────────
    print("  → Mortality records (8 events, 42 total)...")
    mortalities = [
        # (day_offset, quantity, cause_category, cause_description, disposal_method)
        (3,  15, "transport_stress",
         "Transport stressidan kelib chiqqan yo'qotish. Jo'ja tashish paytida qochirib olish.",
         "burial"),
        (6,   8, "weak_chick",
         "Zaif jo'jalar — inkubatorda yetarli rivojlanmagan.",
         "burial"),
        (10,  5, "respiratory",
         "Nafas yo'llari kasalligi belgilari. Antibiotik muolajasi boshlandi.",
         "burial"),
        (15,  3, "respiratory",
         "Nafas yo'llari kasalligining davomi. Muolaja davom ettirildi.",
         "burial"),
        (24,  4, "heat_stress",
         "Issiq havoda issiqlik stressi. Ventilyatsiya kuchaytirildi.",
         "burial"),
        (30,  2, "other",
         "Aniq sabab aniqlanmadi. Umumiy o'lim ko'rsatkichi normal chegarada.",
         "burial"),
        (38,  3, "other",
         "Sotish oldidan yuzaga kelgan. Sabab: yoshi bo'yicha tabiiy yo'qotish.",
         "burial"),
        (40,  2, "other",
         "Tabiiy yo'qotish. Partiya yopilishdan 2 kun oldin.",
         "burial"),
    ]
    for offset, qty, cat, desc, disposal in mortalities:
        await conn.execute("""
            INSERT INTO mortality_records
              (id, batch_id, farm_id, quantity, cause_category, cause_description,
               disposal_method, deceased_at, reported_by,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$8,$8,$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), BATCH_A_ID, FARM_ID,
             qty, cat, desc, disposal, dt(offset), USER_WORKER_ID)

    # ── Weight samplings ───────────────────────────────────────────────────────
    print("  → Weight samplings (6 records, growth curve)...")
    samplings = [
        # (day, sample_size, avg_weight_kg, age_days)
        (7,  100, "0.180", 7,  "Birinchi hafta yakuni. O'sish normal."),
        (14, 100, "0.395", 14, "Starter fazasi o'rtasi. Kutilgan o'sishga mos."),
        (21, 100, "0.872", 21, "Grower fazasiga o'tish. FCR hisoblandi: 1.32"),
        (28, 100, "1.428", 28, "O'sish sur'ati yaxshi. Yem konversiyasi samarali."),
        (35, 100, "2.118", 35, "Finisher fazasiga kirish. Umumiy vazn 8% kutilgandan yuqori."),
        (42, 100, "2.810", 42, "Sotish kunida so'nggi o'lchov. O'rtacha 2.81 kg/bosh."),
    ]
    for day, sample, avg_w, age, notes in samplings:
        total_w = Decimal(avg_w) * sample
        await conn.execute("""
            INSERT INTO weight_samplings
              (id, batch_id, farm_id, sample_size, average_weight_kg,
               total_sample_weight_kg, age_days, measured_at, measured_by, notes,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$8,$8,$9,$9)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), BATCH_A_ID, FARM_ID,
             sample, Decimal(avg_w), total_w, age,
             dt(day), USER_MANAGER_ID, notes)

    # ── Vaccination records ────────────────────────────────────────────────────
    print("  → Vaccination records (3 vaccinations completed)...")
    vaccinations = [
        # (day_scheduled, day_done, schedule_id, vaccine_name, item_id, qty_used, unit, performed_by, notes)
        (14, 14, VACC_SCHEDULE_IBD_ID,
         "IBD (Gumboro) vaksinasi", ITEM_IBD_VACCINE_ID,
         "50.0000", "ml", USER_VET_ID,
         "Ichimlik suvi orqali berildi. Barcha 4985 bosh vaksinatsiya qilindi."),
        (21, 21, VACC_SCHEDULE_NDV_ID,
         "Newcastle (ND) vaksinasi", ITEM_NDV_VACCINE_ID,
         "50.0000", "ml", USER_VET_ID,
         "Spray usulida berildi. Barcha boshlar vaksinatsiya qilindi."),
        (28, 28, VACC_SCHEDULE_IB_ID,
         "Infeksion bronxit (IB) vaksinasi", ITEM_IB_VACCINE_ID,
         "50.0000", "ml", USER_VET_ID,
         "Spray usulida berildi. 4968 bosh vaksinatsiya qilindi."),
    ]
    for day_sch, day_done, sched_id, vacc_name, item_id, qty, unit, perf_by, notes in vaccinations:
        await conn.execute("""
            INSERT INTO vaccination_records
              (id, batch_id, farm_id, schedule_id, vaccine_name,
               vaccine_inventory_item_id, quantity_used, unit,
               status, scheduled_at, vaccinated_at, performed_by, notes,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,
                    'completed',$9,$10,$11,$12,$9,$10,$11,$11)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), BATCH_A_ID, FARM_ID,
             sched_id, vacc_name, item_id, qty, unit,
             dt(day_sch), dt(day_done), perf_by, notes)

    # ── Medication records ─────────────────────────────────────────────────────
    print("  → Medication records (2 records)...")
    medications = [
        # (day, name, item_id, qty, unit, reason, dosage, administered_by)
        (5, "Vitamin AD3E", ITEM_VITAMIN_ID, "150.0000", "ml",
         "Profilaktik maqsadda vitamin berish — transport stressidan keyin immunitetni mustahkamlash.",
         "1 ml / 2 litr ichimlik suvi. 5 kun davomida.",
         USER_VET_ID),
        (11, "Enrofloxacin 10%", ITEM_ANTIBIO_ID, "80.0000", "ml",
         "Nafas yo'llari kasalligi belgilari (10-kundan so'ng) — profilaktik antibiotik kursi.",
         "0.5 ml / 1 litr suv. 5 kun davomida.",
         USER_VET_ID),
    ]
    for day, name, item_id, qty, unit, reason, dosage, by_user in medications:
        await conn.execute("""
            INSERT INTO medication_records
              (id, batch_id, farm_id, medicine_name, medicine_inventory_item_id,
               quantity_used, unit, reason, dosage_notes,
               administered_at, administered_by, notes,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,NULL,$10,$10,$11,$11)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), BATCH_A_ID, FARM_ID,
             name, item_id, qty, unit, reason, dosage,
             dt(day), by_user)

    # ── Feed consumption — 42 daily records ───────────────────────────────────
    print("  → Feed consumption (42 daily records)...")

    # Linear interpolation for daily feed amounts (kg)
    # Phase boundaries: days 1-14 = Starter, 15-35 = Grower, 36-42 = Finisher
    # Water is approx 1.8x feed volume
    def feed_for_day(day: int):
        if day <= 7:
            # Starter week 1: 60→90 kg/day
            qty = 60 + (day - 1) * (90 - 60) / 6
            feed_type = "starter"
            item_id = ITEM_STARTER_ID
        elif day <= 14:
            # Starter week 2: 95→225 kg/day
            qty = 95 + (day - 8) * (225 - 95) / 6
            feed_type = "starter"
            item_id = ITEM_STARTER_ID
        elif day <= 21:
            # Grower week 3: 280→390 kg/day
            qty = 280 + (day - 15) * (390 - 280) / 6
            feed_type = "grower"
            item_id = ITEM_GROWER_ID
        elif day <= 28:
            # Grower week 4: 420→560 kg/day
            qty = 420 + (day - 22) * (560 - 420) / 6
            feed_type = "grower"
            item_id = ITEM_GROWER_ID
        elif day <= 35:
            # Grower week 5: 580→700 kg/day
            qty = 580 + (day - 29) * (700 - 580) / 6
            feed_type = "grower"
            item_id = ITEM_GROWER_ID
        else:
            # Finisher week 6: 770→820 kg/day
            qty = 770 + (day - 36) * (820 - 770) / 6
            feed_type = "finisher"
            item_id = ITEM_FINISHER_ID
        water = qty * 1.8
        return round(qty, 1), round(water, 1), feed_type, item_id

    for day in range(1, 43):
        qty_kg, water_l, feed_type, item_id = feed_for_day(day)
        feed_date = (BATCH_ARRIVAL + timedelta(days=day)).date()
        await conn.execute("""
            INSERT INTO feed_consumptions
              (id, batch_id, farm_id, feed_date, feed_type,
               quantity_kg, water_liters, age_days,
               feed_inventory_item_id, notes,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,NULL,$10,$10,$11,$11)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), BATCH_A_ID, FARM_ID,
             feed_date, feed_type,
             Decimal(str(qty_kg)), Decimal(str(water_l)), day,
             item_id, dt(day), USER_WORKER_ID)

    print("  ✓ livestock-service seeded")


async def main():
    print("\n[livestock-service]")
    conn = await connect("livestock")
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
