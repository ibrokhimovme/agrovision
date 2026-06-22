# AgroVision

Parrandachilik fermalari uchun raqamli boshqaruv platformasi.

---

## 1. AgroVision haqida

AgroVision — O'zbekistondagi kichik va o'rta parrandachilik fermalari uchun yaratilgan ferma boshqaruv platformasi. U qog'oz daftar va tarqoq Excel fayllar o'rniga fermaning kundalik operatsiyalarini — partiya holatidan tortib, ozuqa, o'lim, vazn, vaksinatsiya va moliyaviy hisob-kitobgacha — yagona tizimda yuritish imkonini beradi.

Platforma quyidagi muammolarni hal qiladi:

- Ferma ma'lumotlari turli qog'oz va fayllarda tarqoq saqlanishi
- Partiya (parrandalar guruhi) bo'yicha xarajat va foydani aniq hisoblay olmaslik
- Ozuqa, dori-darmon va vaksina zaxiralarini nazoratsiz boshqarish
- Mijoz va ta'minotchilar bilan qarz-kreditorlik holatini kuzata olmaslik
- Fermalar va partiyalar bo'yicha tendensiyalarni solishtira olmaslik

AgroVision bir nechta fermani bitta hisob (account) ostida boshqarish, har bir partiyaning to'liq hayotiy siklini kuzatish va moliyaviy natijalarni real vaqtda ko'rish imkonini beradi.

---

## 2. Asosiy imkoniyatlar

- **Ferma boshqaruvi** — fermalar, binolar va seksiyalarni yaratish, tahrirlash, ko'rish
- **Parranda partiyalarini boshqarish** — partiyani ochish, avtomatik nomlash, faollik holati va yopish (sotish/yakunlash)
- **Kunlik ozuqa hisobi** — kunlik ozuqa va suv sarfini qayd etish
- **Kunlik o'lim hisobi** — o'lim sonini kuzatish, partiya jonli sonini avtomatik yangilash
- **Vazn nazorati** — davriy vazn o'lchovlari, o'rtacha vazn va o'sish ko'rsatkichlari
- **Vaksinatsiya va dorilash** — vaksinatsiya va davolash amallarini qayd etish
- **Ombor boshqaruvi** — omborlar, ozuqa/dori-darmon zaxiralarini boshqarish
- **Moliya nazorati** — xarajat va sotuvlarni qayd etish, qisman to'lovlarni kuzatish
- **Qarzdorlik va kreditorlik nazorati** — mijozlar (debitor) va ta'minotchilar (kreditor) bo'yicha qarz holatini ko'rish
- **Hisobotlar** — partiya bo'yicha PDF hisobot, fermalar va partiyalar kesimida tendensiya va taqqoslash tahlili
- **Boshqaruv paneli (Dashboard)** — fermalar bo'yicha asosiy ko'rsatkichlar va tendensiya grafiklari
- **Partiyalar arxivi** — yakunlangan partiyalarni arxivlash, arxivdagi ma'lumotlarni hisobotlarda saqlab qolish
- **Foydalanuvchi va rollar boshqaruvi** — hisob (account) doirasida foydalanuvchilarni yaratish, fermalarga bog'lash, rol tayinlash

---

## 3. Tizim arxitekturasi

| Qatlam | Texnologiya |
|---|---|
| Frontend | React + TypeScript (Vite) |
| Backend | FastAPI (Python) — modulli monolit |
| Ma'lumotlar bazasi | PostgreSQL |
| Kesh | Redis |
| Reverse proxy | Nginx |
| Konteynerizatsiya | Docker + Docker Compose |

Backend bitta FastAPI ilovasi sifatida ishlaydi va quyidagi modullardan iborat: identity (foydalanuvchilar/rollar), farm (fermalar), poultry (partiyalar va kundalik hisob), inventory (ombor), finance (moliya), reporting (hisobotlar), notifications (bildirishnomalar).

---

## 4. Talablar

Loyihani ishga tushirish uchun quyidagilar zarur:

- Docker
- Docker Compose

Boshqa hech qanday lokal o'rnatish (Python, Node.js va h.k.) talab qilinmaydi — barcha xizmatlar konteynerlarda ishlaydi.

---

## 5. Loyihani ishga tushirish

1. `.env.example` faylidan `.env` faylini yarating va kerakli qiymatlarni to'ldiring:

   ```
   cp .env.example .env
   ```

2. Stekni ishga tushiring:

   ```
   docker compose up --build
   ```

   Yoki `Makefile` orqali:

   ```
   make up
   ```

3. Ilovaga kirish:

   | Manzil | Tavsif |
   |---|---|
   | http://localhost | Frontend (asosiy ilova) |
   | http://localhost/api/ | Backend API (Nginx orqali) |
   | http://localhost/health | Backend sog'lik holati (health check) |

   Foydali `Makefile` buyruqlari: `make down`, `make restart`, `make logs`, `make ps`, `make shell`.

---

## 6. Demo foydalanuvchilar

`scripts/seed/seed_identity.py` orqali quyidagi namunaviy foydalanuvchilar yaratiladi:

| Email | Parol | Rol |
|---|---|---|
| admin@agrovision.uz | Admin123! | Super Admin |
| owner@toshkent-broiler.uz | Owner123! | Ferma egasi |
| manager@toshkent-broiler.uz | Manager123! | Ferma boshqaruvchisi |
| accountant@toshkent-broiler.uz | Accountant123! | Hisobchi |
| worker1@toshkent-broiler.uz | Worker123! | Ferma xodimi |
| vet@toshkent-broiler.uz | Vet123! | Veterinar |

Namunaviy ma'lumotlarni yuklash uchun: `python scripts/seed/run_all.py`.

---

## 7. Papkalar tuzilishi

```
AgroVision/
├── app/                  Backend — modulli monolit (FastAPI)
│   ├── identity/         Foydalanuvchilar, rollar, autentifikatsiya
│   ├── farm/             Fermalar, binolar, seksiyalar
│   ├── poultry/          Partiyalar, ozuqa, o'lim, vazn, vaksinatsiya
│   ├── inventory/        Omborlar va zaxiralar
│   ├── finance/          Xarajat, sotuv, qarzdorlik
│   ├── reporting/        Hisobotlar va tahlillar
│   ├── notifications/    Bildirishnomalar
│   └── core/             Umumiy konfiguratsiya va middleware
├── frontend/             React + TypeScript SPA
│   └── src/pages/        Sahifalar (fermalar, partiyalar, ombor, moliya, hisobotlar, foydalanuvchilar)
├── shared/               Modullar o'rtasida umumiy kod (kontrakt, model, util)
├── infrastructure/       Nginx va PostgreSQL konfiguratsiyalari
├── scripts/seed/         Namunaviy ma'lumot generatorlari
├── docs/                 Arxitektura va API hujjatlari, qarorlar (ADR)
├── tests/                Avtomatik testlar
├── docker-compose.yml    Asosiy Docker Compose konfiguratsiyasi
├── Dockerfile.monolith   Backend uchun Docker image
├── Makefile              Ishga tushirish buyruqlari
├── 1. BRD_AgroVision_Farm_Management_qism1.docx   Biznes talablar hujjati
└── 2. SRS_AgroVision_Farm_Management_v1.1.docx     Dasturiy talablar spetsifikatsiyasi
```

---

## 8. API hujjatlari

Backend ishga tushirilgandan so'ng, Swagger (OpenAPI) hujjatlari quyidagi manzilda mavjud:

- http://localhost:8100/docs (konteyner ichidan to'g'ridan-to'g'ri, dev muhitida)

Asosiy endpoint guruhlari (`/api/v1/...`): `/auth`, `/users`, `/roles`, `/farms`, `/batches`, `/inventory`, `/sales`, `/expenses`, `/reports`, `/notifications`.

---

## 9. Hozirgi loyiha holati

AgroVision hozirda MVP (Minimum Viable Product) bosqichida — asosiy ferma-partiya ish jarayoni to'liq ishlaydigan holatda.

**Amalga oshirilgan:**
- Hisob (account) asosida ko'p fermali boshqaruv
- Ferma, bino va seksiyalar bo'yicha CRUD
- Partiya hayotiy sikli (ochish → faol holat → yakunlash/arxivlash)
- Kunlik ozuqa, o'lim va vazn hisobi
- Vaksinatsiya va dorilash yozuvlari
- Ombor va zaxira boshqaruvi
- Xarajat va sotuv yozuvlari, qisman to'lovlar, debitor/kreditor nazorati
- Partiya va ferma kesimidagi hisobotlar, tendensiya va taqqoslash tahlili
- Foydalanuvchi va rol boshqaruvi

**Davom etmoqda / qisman:**
- To'liq audit jurnali interfeysi
- Avtomatik testlarni yangi backend tuzilishiga moslashtirish

**Rejalashtirilgan emas (joriy bosqichda):**
- Email/SMS orqali bildirishnomalar
- Rejalashtirilgan hisobot yuborish

---

## 10. Kelgusi rejalar

- AI Farm Assistant — fermerlar uchun aqlli yordamchi
- AI Farm Analyst — ma'lumotlarga asoslangan avtomatik tahlil va tavsiyalar
- Kengaytirilgan dashboard analitikasi
- Mobil ilova

---

## 11. Hujjatlar

| Hujjat | Tavsif |
|---|---|
| `1. BRD_AgroVision_Farm_Management_qism1.docx` | **BRD** — Biznes talablar hujjati: maqsadlar, manfaatdor tomonlar, biznes jarayonlari |
| `2. SRS_AgroVision_Farm_Management_v1.1.docx` | **SRS** — Dasturiy talablar spetsifikatsiyasi: tizim xususiyatlari, funksional va nofunksional talablar |
| `docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md` | **ADR** — MVP doirasini O'zbekiston parrandachilik fermalariga moslashtirish bo'yicha arxitektura qarori |
| `docs/architecture/` | Tizim arxitekturasi va modullar tuzilishi haqida qo'shimcha hujjatlar |
| `DEPLOYMENT.md` | Production muhitiga joylashtirish bo'yicha qo'llanma |
