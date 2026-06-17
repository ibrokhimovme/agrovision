"""
Notification Service Seed
==========================
Creates realistic notifications tied to batch lifecycle events.

Notifications:
  1. [INFO]     Batch B-2026-001 joylashtirildi (farm_owner, manager)
  2. [WARNING]  Karantin davri tugaydi — ertaga faollashtirish (manager)
  3. [INFO]     Batch B-2026-001 faollashtirildi (farm_owner, manager)
  4. [WARNING]  IBD vaksinatsiyasi vaqti keldi — 14-kun (manager, vet)
  5. [INFO]     IBD vaksinatsiyasi bajarildi (farm_owner)
  6. [CRITICAL] O'lim ko'rsatkichi — 15 bosh yo'qotildi (manager, farm_owner)
  7. [WARNING]  Grower yemi kamaymoqda — minimum miqdorga yaqin (manager)
  8. [WARNING]  Newcastle vaksinatsiyasi vaqti keldi — 21-kun (manager, vet)
  9. [INFO]     Newcastle vaksinatsiyasi bajarildi (farm_owner)
 10. [INFO]     Og'irlik namunasi: o'rtacha 1.428 kg (manager)
 11. [WARNING]  Finisher yemiga o'tish vaqti — 35-kun (manager)
 12. [INFO]     Batch B-2026-001 yopildi — sotish bajarildi (farm_owner, accountant)
 13. [INFO]     Sotish tasdiqlandi: 329,280,000 UZS (accountant)
"""
import asyncio
import asyncpg
import uuid
from config import *


async def run(conn: asyncpg.Connection) -> None:
    await conn.execute("DELETE FROM notifications WHERE farm_id = $1", FARM_ID)
    print("  → Notifications (15 records)...")

    notifications = [
        # Batch placement
        (USER_FARM_OWNER_ID, "in_app", "info", "batch.placed",
         "Partiya B-2026-001 joylashtirildi",
         "5000 bosh broiler jo'jasi karantinga joylashtirildi. Sana: 6-aprel 2026. "
         "Yetkazib beruvchi: Samarqand Inkubator MChJ.",
         BATCH_A_ID, BATCH_ARRIVAL, True, True),

        (USER_MANAGER_ID, "in_app", "info", "batch.placed",
         "Yangi partiya B-2026-001 joylashtirildi",
         "5000 bosh broiler jo'jasi A-sektorda karantinga qo'yildi. "
         "Karantin muddati: 6-aprel dan 13-aprelgacha.",
         BATCH_A_ID, BATCH_ARRIVAL, True, True),

        # Quarantine ending reminder (day 6)
        (USER_MANAGER_ID, "in_app", "warning", "batch.quarantine_ending",
         "Karantin ertaga tugaydi — B-2026-001",
         "B-2026-001 partiyasining karantin davri ertaga (13-aprel) tugaydi. "
         "Faollashtirish uchun tayyor bo'ling. O'sish ko'rsatkichlari normal.",
         BATCH_A_ID, d(6), True, True),

        # Batch activated
        (USER_FARM_OWNER_ID, "in_app", "info", "batch.activated",
         "Partiya B-2026-001 faollashtirildi",
         "Karantin muvaffaqiyatli yakunlandi. B-2026-001 partiyasi ishlab chiqarish "
         "holatiga o'tkazildi. Joriy soni: 4977 bosh.",
         BATCH_A_ID, BATCH_ACTIVATED, True, True),

        # High mortality alert — Day 3 (15 dead)
        (USER_FARM_OWNER_ID, "in_app", "critical", "batch.mortality_spike",
         "MUHIM: 15 bosh yo'qotildi — B-2026-001",
         "3-kun: 15 bosh transport stressidan nobud bo'ldi. Umumiy yo'qotish: 15 bosh (0.3%). "
         "Veterinar tekshiruvini o'tkazing.",
         BATCH_A_ID, d(3), True, True),

        (USER_MANAGER_ID, "in_app", "critical", "batch.mortality_spike",
         "MUHIM: Yuqori o'lim ko'rsatkichi — 15 bosh",
         "3-kun: 15 bosh transport stressidan yo'qoldi. Veterinar Mirzayev S. ga xabar berildi. "
         "Vitamini D3 kursini boshlang.",
         BATCH_A_ID, d(3), True, True),

        # IBD vaccination reminder — Day 14
        (USER_VET_ID, "in_app", "warning", "vaccination.due",
         "IBD vaksinatsiyasi vaqti keldi — 14-kun",
         "B-2026-001 partiyasi uchun IBD (Gumboro) vaksinatsiyasi bugun bajarilishi kerak. "
         "Inventarda 60 ml mavjud. Ichimlik suvi orqali bering.",
         BATCH_A_ID, d(14), True, True),

        (USER_MANAGER_ID, "in_app", "warning", "vaccination.due",
         "Vaksinatsiya eslatmasi: IBD — B-2026-001",
         "14-kunlik IBD (Gumboro) vaksinatsiyasi bugun. Veterinar tayyor. "
         "Suv ta'minotini 2 soat oldin o'chiring.",
         BATCH_A_ID, d(14), True, True),

        # IBD vaccination completed
        (USER_FARM_OWNER_ID, "in_app", "info", "vaccination.completed",
         "IBD vaksinatsiyasi muvaffaqiyatli bajarildi",
         "14-kun: IBD vaksinatsiyasi 4985 boshga amalga oshirildi. "
         "Sarflangan: 50 ml. Veterinar: Mirzayev S.",
         BATCH_A_ID, d(14), True, True),

        # Newcastle vaccination reminder — Day 21
        (USER_VET_ID, "in_app", "warning", "vaccination.due",
         "Newcastle vaksinatsiyasi vaqti keldi — 21-kun",
         "B-2026-001: Newcastle (ND) vaksinatsiyasi bugun bajarilishi kerak. "
         "Spray usulida. Inventarda 60 ml mavjud.",
         BATCH_A_ID, d(21), True, True),

        # Newcastle vaccination completed
        (USER_FARM_OWNER_ID, "in_app", "info", "vaccination.completed",
         "Newcastle vaksinatsiyasi bajarildi",
         "21-kun: Newcastle vaksinatsiyasi muvaffaqiyatli. 4974 boshga spray usulida. "
         "O'rtacha vazn: 0.872 kg. FCR: 1.32",
         BATCH_A_ID, d(21), True, True),

        # Low grower feed stock warning
        (USER_MANAGER_ID, "in_app", "warning", "inventory.low_stock",
         "Grower yemi kamaymoqda — omborni to'ldiring",
         "Grower yemi qoldig'i 3000 kg ga tushdi — minimal chegara: 1000 kg. "
         "Yaqin 5 kunda taxminan 3500 kg kerak bo'ladi. Buyurtma bering.",
         None, d(27), False, False),

        # Weight milestone Day 28
        (USER_MANAGER_ID, "in_app", "info", "batch.weight_milestone",
         "Og'irlik namunasi: 1.428 kg — B-2026-001",
         "28-kun: o'rtacha vazn 1.428 kg (100 bosh namuna). Kutilgan ko'rsatkich: 1.4 kg. "
         "FCR hisoblash: 1.35. O'sish rejada!",
         BATCH_A_ID, d(28), True, True),

        # Batch closed — sale completed
        (USER_FARM_OWNER_ID, "in_app", "info", "batch.closed",
         "Partiya B-2026-001 yopildi — sotish yakunlandi",
         "42-kun: 4900 bosh, 13720 kg @ 24,000 UZS/kg = 329,280,000 UZS. "
         "Ferma ochiq. Keyingi tsikl uchun dezinfeksiya boshlaning.",
         BATCH_A_ID, BATCH_CLOSED, True, True),

        # Sale confirmed — for accountant
        (USER_ACCOUNTANT_ID, "in_app", "info", "sale.confirmed",
         "Sotish tasdiqlandi: 329,280,000 UZS",
         "B-2026-001 partiyasi to'liq sotildi. Xaridor: Bektemir go'sht bozori. "
         "To'lov holati: to'liq to'landi (naqd). Xarajatlar: 100,650,000 UZS. "
         "Foyda: 228,630,000 UZS.",
         BATCH_A_ID, BATCH_CLOSED, True, True),
    ]

    for (user_id, channel, severity, event_type,
         title, body, ref_id, created_at, is_read, is_delivered) in notifications:
        delivered_at = created_at if is_delivered else None
        await conn.execute("""
            INSERT INTO notifications
              (id, user_id, farm_id, title, body,
               channel, severity, event_type, reference_id,
               is_read, is_delivered, delivered_at,
               created_at, updated_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$13)
            ON CONFLICT (id) DO NOTHING
        """, uuid.uuid4(), user_id, FARM_ID, title, body,
             channel, severity, event_type, ref_id,
             is_read, is_delivered, delivered_at, created_at)

    print("  ✓ notification-service seeded")


async def main():
    print("\n[notification-service]")
    conn = await asyncpg.connect(DATABASES["notification"])
    try:
        await run(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
