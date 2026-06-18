"""
Finance Service Seed
=====================
Creates: 1 customer, 12 expense records, 1 sale record.

Total expenses:  100,650,000 UZS
Total revenue:   329,280,000 UZS
Gross profit:    228,630,000 UZS
Profit margin:   69.4%

Expense breakdown (linked to Batch B-2026-001):
  Chick purchase:    22,500,000 UZS
  Starter feed:       8,800,000 UZS
  Grower feed:       28,000,000 UZS
  Finisher feed:     12,600,000 UZS
  IBD vaccine:        5,000,000 UZS
  Newcastle vaccine:  3,000,000 UZS
  Vitamins:           1,500,000 UZS
  Antibiotics:        2,000,000 UZS
  Labor (April):      7,500,000 UZS
  Labor (May):        3,750,000 UZS
  Utilities:          3,500,000 UZS
  Transport:          2,500,000 UZS
  ─────────────────────────────────
  IB vaccine:         3,500,000 UZS
  ─────────────────────────────────
  Total:            104,150,000 UZS
"""
import asyncio
import asyncpg
import uuid
from decimal import Decimal
from config import *


async def run(conn: asyncpg.Connection) -> None:
    # Clean up child records before re-seeding
    await conn.execute("DELETE FROM expenses WHERE batch_id = $1", BATCH_A_ID)

    print("  → Customer: Bektemir go'sht bozori...")
    await conn.execute("""
        INSERT INTO customers
          (id, farm_id, name, phone, address,
           credit_limit, current_debt, is_active,
           created_at, updated_at, created_by, updated_by)
        VALUES ($1,$2,
                'Bektemir go''sht bozori',
                '+998 71 234 56 78',
                'Toshkent sh., Yunusobod tumani, Bektemir bozori',
                50000000.00, 0.00, true,
                $3,$3,$4,$4)
        ON CONFLICT (id) DO NOTHING
    """, CUSTOMER_ID, FARM_ID, FARM_SETUP_DATE, USER_ACCOUNTANT_ID)

    print("  → Expenses (13 records)...")
    expenses = [
        # (id, farm_id, category, expense_type, description, amount,
        #  batch_id, reference_document, expense_date, approved_by, notes)
        (uuid.uuid4(), FARM_ID,
         "other", "chick",
         "Jo'ja sotib olish — Samarqand Inkubator MChJ (5000 bosh × 4500 UZS)",
         "22500000.00",
         BATCH_A_ID, "INV-2026-SI-0112",
         BATCH_ARRIVAL, USER_FARM_OWNER_ID,
         "Ross-308 zoti. Sifat sertifikati mavjud. Inkubator harorati: 37.5°C"),

        (uuid.uuid4(), FARM_ID,
         "feed", "feed",
         "BSK starter yemi — 4000 kg (Toshkent Agro Savdo MChJ)",
         "8800000.00",
         BATCH_A_ID, "INV-2026-TAS-0098",
         FARM_SETUP_DATE, USER_MANAGER_ID,
         "Protein 22%, yog' 5.5%. Batch uchun mo'ljallangan."),

        (uuid.uuid4(), FARM_ID,
         "feed", "feed",
         "O'sish yemi (Grower) — 14000 kg (Toshkent Agro Savdo MChJ)",
         "28000000.00",
         BATCH_A_ID, "INV-2026-TAS-0099",
         FARM_SETUP_DATE, USER_MANAGER_ID,
         "Protein 19%, yog' 5%. Grower faza uchun."),

        (uuid.uuid4(), FARM_ID,
         "feed", "feed",
         "Tugallash yemi (Finisher) — 7000 kg (Toshkent Agro Savdo MChJ)",
         "12600000.00",
         BATCH_A_ID, "INV-2026-TAS-0100",
         FARM_SETUP_DATE, USER_MANAGER_ID,
         "Protein 18%, yog' 6%. Finisher faza uchun. Antibiotiksiz."),

        (uuid.uuid4(), FARM_ID,
         "veterinary", "vaccine",
         "IBD (Gumboro) vaksinasi — 60 ml (UzVetPharma)",
         "5000000.00",
         BATCH_A_ID, "INV-2026-UVP-0045",
         FARM_SETUP_DATE, USER_VET_ID,
         "Lot: IBD-LOT-2026-A. Yaroqlilik muddati: 12 oy. Sovuq zanjirda saqlash."),

        (uuid.uuid4(), FARM_ID,
         "veterinary", "vaccine",
         "Newcastle (ND) vaksinasi — 60 ml (UzVetPharma)",
         "3000000.00",
         BATCH_A_ID, "INV-2026-UVP-0046",
         FARM_SETUP_DATE, USER_VET_ID,
         "Lot: NDV-LOT-2026-A. HB1 shtamm. Spray va ichimlik orqali."),

        (uuid.uuid4(), FARM_ID,
         "veterinary", "vaccine",
         "Infeksion bronxit (IB) vaksinasi — 60 ml (UzVetPharma)",
         "3500000.00",
         BATCH_A_ID, "INV-2026-UVP-0049",
         FARM_SETUP_DATE, USER_VET_ID,
         "Lot: IB-LOT-2026-A. Massachusetts shtamm."),

        (uuid.uuid4(), FARM_ID,
         "veterinary", "medicine",
         "Vitamin AD3E — 500 ml (UzVetPharma)",
         "1500000.00",
         BATCH_A_ID, "INV-2026-UVP-0047",
         FARM_SETUP_DATE, USER_VET_ID,
         "Profilaktik vitamin kompleksi. Immunitetni mustahkamlash."),

        (uuid.uuid4(), FARM_ID,
         "veterinary", "medicine",
         "Enrofloxacin 10% — 200 ml (UzVetPharma)",
         "2000000.00",
         BATCH_A_ID, "INV-2026-UVP-0048",
         FARM_SETUP_DATE, USER_VET_ID,
         "Keng spektrli antibiotik. Nafas yo'llari kasalliklariga qarshi."),

        (uuid.uuid4(), FARM_ID,
         "labor", None,
         "Aprel oyi ish haqi — 2 ishchi (Toshmatov J., Qodirov A.)",
         "7500000.00",
         BATCH_A_ID, "PAYROLL-2026-04",
         d(24), USER_ACCOUNTANT_ID,
         "Har bir ishchiga 3,750,000 UZS. Bank orqali to'landi."),

        (uuid.uuid4(), FARM_ID,
         "labor", None,
         "May oyi ish haqi (qisman) — 2 ishchi",
         "3750000.00",
         BATCH_A_ID, "PAYROLL-2026-05",
         d(39), USER_ACCOUNTANT_ID,
         "18 kunlik ish haqi. Tsikl yakunlangandan so'ng to'liqlashtiriladI."),

        (uuid.uuid4(), FARM_ID,
         "utilities", None,
         "Mart-Aprel kommunal to'lovlar (elektr, gaz, suv)",
         "3500000.00",
         BATCH_A_ID, "UTIL-2026-04",
         d(9), USER_ACCOUNTANT_ID,
         "Isitish uchun gaz — 1,800,000. Elektr — 1,200,000. Suv — 500,000 UZS."),

        (uuid.uuid4(), FARM_ID,
         "transport", None,
         "Jo'ja tashish va sotish uchun transport xarajati",
         "2500000.00",
         BATCH_A_ID, "TRN-2026-0518",
         BATCH_CLOSED, USER_MANAGER_ID,
         "4900 bosh parrandani Bektemir go''sht bozoriga yetkazib berish."),
    ]

    for exp in expenses:
        exp_id, farm_id, category, exp_type, description, amount, \
            batch_id, ref_doc, exp_date, approved_by, notes = exp
        await conn.execute("""
            INSERT INTO expenses
              (id, farm_id, category, expense_type, description, amount, currency,
               batch_id, reference_document, expense_date, approved_by, notes,
               created_at, updated_at, created_by, updated_by)
            VALUES ($1,$2,$3,$4,$5,$6,'UZS',$7,$8,$9,$10,$11,$9,$9,$12,$12)
            ON CONFLICT (id) DO NOTHING
        """, exp_id, farm_id, category, exp_type, description,
             Decimal(amount), batch_id, ref_doc, exp_date,
             approved_by, notes, USER_ACCOUNTANT_ID)

    print("  → Sale record: 4900 bosh, 13720 kg @ 24,000 UZS/kg...")
    await conn.execute("""
        INSERT INTO sale_records
          (id, batch_id, farm_id, customer_name, customer_phone,
           head_count, quantity_kg, price_per_kg_uzs, total_revenue_uzs,
           payment_status, sold_at, notes,
           created_at, updated_at, created_by, updated_by)
        VALUES ($1,$2,$3,
                'Bektemir go''sht bozori',
                '+998 71 234 56 78',
                4900, 13720.000, 24000.00, 329280000.00,
                'paid', $4,
                'To''liq naqd to''lov. Sotishdan oldin og''irlik o''lchovi o''tkazildi. '
                'O''rtacha vazn 2.80 kg/bosh. 4900 bosh, 58 bosh qoldi.',
                $4,$4,$5,$5)
        ON CONFLICT (id) DO NOTHING
    """, SALE_RECORD_ID, BATCH_A_ID, FARM_ID,
         BATCH_CLOSED, USER_ACCOUNTANT_ID)

    print("  ✓ finance-service seeded")
    print("    Revenue:  329,280,000 UZS")
    print("    Expenses: 104,150,000 UZS")
    print("    Profit:   225,130,000 UZS (68.4% margin)")


async def main():
    print("\n[finance-service]")
    conn = await connect("finance")
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
