# AgroVision — UAT Test Script
**Version:** 1.0 | **Date:** 2026-06-17 | **Environment:** Staging / Production

---

## Prerequisites

- AgroVision stack running (`docker compose up`)
- Seed data loaded: `docker compose exec identity-service python seeds/seed_roles.py`
- Tester has Admin credentials: `admin@agrovision.uz` / `Admin@123`
- Browser: Chrome or Firefox latest

---

## TC-01 — Authentication

| # | Step | Expected |
|---|------|----------|
| 1 | Open `http://localhost:3000` | Redirected to `/login` |
| 2 | Enter wrong password, click "Kirish" | Red error: "Email yoki parol noto'g'ri" |
| 3 | Enter correct credentials, click "Kirish" | Redirected to Dashboard |
| 4 | Refresh page | Session persists, Dashboard visible |
| 5 | Click logout (top-right icon) | Redirected to `/login` |

**Pass/Fail:** ___

---

## TC-02 — Dashboard KPIs

| # | Step | Expected |
|---|------|----------|
| 1 | Log in as Admin | Dashboard loads |
| 2 | Verify 4 KPI cards visible | Faol partiyalar, Karantin, Faol parrandalar, Karantindagi parrandalar |
| 3 | Verify numbers are non-negative integers | No NaN / undefined displayed |
| 4 | Verify recent batch list shows last 5 batches | Batch codes, statuses, placement dates shown |

**Pass/Fail:** ___

---

## TC-03 — Farm Management

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Fermalar" in sidebar | Farm list page loads |
| 2 | Click "+ Yangi ferma" | Create modal opens |
| 3 | Submit with empty name | Button stays disabled |
| 4 | Enter name "Test Ferma", select "Parrandachilik", click "Saqlash" | Toast "Ferma yaratildi"; modal closes; new farm appears in list |
| 5 | Click "Tahrirlash" on the new farm | Edit modal pre-populated with existing values |
| 6 | Change name to "Test Ferma 2", click "Saqlash" | Toast "Ferma yangilandi"; card shows updated name |
| 7 | Click "Batafsil" on the farm | FarmDetailPage loads showing farm info |
| 8 | Click "+ Bino qo'shish" | Building form appears inline |
| 9 | Enter name "A-Bino", capacity "5000", click "Saqlash" | Toast "Bino qo'shildi"; building card appears |
| 10 | Click "+ Bo'lim qo'shish" on the building | Section inline form appears |
| 11 | Enter name "1-sektor", type "Ishlab chiqarish", click "Saqlash" | Toast "Bo'lim qo'shildi"; section appears in grid |
| 12 | Return to farm list; click "O'chirish" on Test Ferma 2 | Confirmation dialog appears |
| 13 | Confirm delete | Toast "Test Ferma 2 o'chirildi"; card removed from list |

**Pass/Fail:** ___

---

## TC-04 — Batch Creation (cascade dropdowns, no UUID input)

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Parrandalar" → "Yangi partiya" | NewBatchPage loads |
| 2 | Confirm no text field with UUID placeholder visible | PASS if no monospace UUID input shown |
| 3 | Select farm from "Ferma" dropdown | "Bino" dropdown appears |
| 4 | Select building from "Bino" dropdown | "Bo'lim" dropdown appears |
| 5 | Select section from "Bo'lim" dropdown | Section value populated |
| 6 | Fill in all required fields; click "Saqlash" | Redirected to batch list; new batch visible |

**Pass/Fail:** ___

---

## TC-05 — Batch Lifecycle Operations

| # | Step | Expected |
|---|------|----------|
| 1 | Open a Quarantine batch → click "Faollashtirish" | Status changes to Faol |
| 2 | Go to "Ozuqa" tab → add feed record (date, qty) | Feed record appears in list; feed summary updates |
| 3 | Go to "O'lim" tab → record 5 mortalities | Mortality record appears; current count decrements |
| 4 | Go to "Og'irlik" tab → add weight sampling | Weight record appears; metrics (ADG, FCR) calculated |
| 5 | Go to "Emlash" tab → mark a planned vaccination as complete | Status changes to "Bajarildi" |
| 6 | Go to "Sotish" tab → record a sale | Sale appears; revenue updated |
| 7 | Go to "Xarajat" tab → add an expense | Expense appears; cost summary updated |
| 8 | Go to "Foyda" tab | Gross profit, margin calculated correctly |
| 9 | Close batch with reason "Sotish" | Status changes to "Yopildi" |

**Pass/Fail:** ___

---

## TC-06 — Inventory

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Ombor" in sidebar | Inventory page loads |
| 2 | Create a warehouse (Ombor yaratch) | Warehouse appears in dropdown |
| 3 | Add a stock item (em, feed type) | Item appears in item list |
| 4 | Record a receipt (Kirim) | Item quantity increases |
| 5 | Record a dispatch (Chiqim) | Item quantity decreases; low-stock warning if below minimum |

**Pass/Fail:** ___

---

## TC-07 — Finance

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Moliya" in sidebar | Finance page loads with KPIs |
| 2 | KPI cards show Jami daromad, Jami xarajat, Sof foyda, Foyda marjasi | Non-zero values for seeded data |
| 3 | Record a new expense via "Xarajat qo'shish" | Expense appears in list |
| 4 | Record a sale via "Sotuv qo'shish" | Sale appears; revenue KPI updates |

**Pass/Fail:** ___

---

## TC-08 — Reports

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Hisobotlar" in sidebar | Reports page loads |
| 2 | Select farm and batch → click "Hisobot ko'rish" | BatchReportPage loads with full metrics |
| 3 | Verify FCR, ADG, mortality rate, revenue, profit all populated | No N/A for closed batches with data |
| 4 | Verify report loads in < 5 seconds | Timed from click to full render |

**Pass/Fail:** ___

---

## TC-09 — User Management

| # | Step | Expected |
|---|------|----------|
| 1 | Click "Foydalanuvchilar" in sidebar | Users page loads with user table |
| 2 | Click "+ Yangi foydalanuvchi" | Create modal opens |
| 3 | Fill email, name, password, select role "Worker" → "Saqlash" | Toast "Foydalanuvchi yaratildi"; new row in table |
| 4 | Click "Tahrirlash" on the new user | Edit modal opens with name pre-filled |
| 5 | Change name → "Saqlash" | Toast "Foydalanuvchi yangilandi"; table updates |
| 6 | Click the green toggle to disable user | Toggle turns grey; toast "Foydalanuvchi o'chirildi" |
| 7 | Click the grey toggle to re-enable | Toggle turns green; toast "Foydalanuvchi faollashtirildi" |

**Pass/Fail:** ___

---

## TC-10 — Mobile Responsiveness (360px viewport)

| # | Step | Expected |
|---|------|----------|
| 1 | Set browser viewport to 360×800 (Chrome DevTools) | No horizontal scroll on Dashboard |
| 2 | Verify hamburger menu button visible | Sidebar hidden; hamburger button in header shown |
| 3 | Click hamburger | Sidebar slides in with overlay |
| 4 | Navigate to Farms page | Farm cards stack vertically |
| 5 | Navigate to Users page | Table scrollable horizontally; phone column hidden |
| 6 | Open create farm modal | Modal fits within 360px width |

**Pass/Fail:** ___

---

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | PASS / FAIL |

**Total:** ___/10 test cases passed
