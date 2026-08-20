# SOF EXPO SAMARKAND — B2B Ro'yxatdan O'tish Telegram Boti

Ushbu Telegram bot **SOF EXPO SAMARKAND** ko'rgazmasiga keluvchi B2B tashrif buyuruvchilardan ma'lumotlarni ketma-ket yig'ish, Telegram guruhiga kartochka ko'rinishida yuborish, SQLite ma'lumotlar bazasiga va Google Sheets/Excel formatiga saqlash uchun mo'ljallangan.

---

## 📋 Imkoniyatlari

- **Ketma-ket anketa (11 ta savol):**
  1. Ism va familiya
  2. Lavozim
  3. Kompaniya nomi
  4. Faoliyat sohasi
  5. Mamlakat (O'zbekiston, Qozog'iston, Rossiya va b. tugmalari bilan)
  6. Shahar
  7. Telefon raqami (Telegram `contact` ulashish tugmasi va qo'lda kiritish)
  8. Email (O'tkazib yuborish imkoni bilan)
  9. Ko'rgazmaga kelish kuni (1-kun, 2-kun, 3-kun, Barcha kunlar)
  10. Tashrif maqsadi (Hamkor topish, Mijoz topish, Mahsulotlar bilan tanishish va b.)
  11. Qo'shimcha izoh (O'tkazib yuborish imkoni bilan)
- **Telegram Guruh integratsiyasi (Live Baza):**
  - Har bir yangi ro'yxatdan o'tgan foydalanuvchi ma'lumotlari avtomatik ravishda tashkilotchilarning **Telegram guruhiga** kelib tushadi.
- **Administrator / Guruh buyruqlari:**
  - `/stats` — Jami arizalar soni va kelish kunlari/maqsadlari bo'yicha statistika.
  - `/export` — Barcha foydalanuvchilar ma'lumotlarini tayyor formatlangan Excel (`.xlsx`) fayl ko'rinishida yuklab olish.

---

## 🛠 O'rnatish va Mahalliy Ishga Tushirish

1. **Repozitoriyani klonlash yoki yuklash:**
   ```bash
   git clone https://github.com/Elmun-Technologies/sofexpo-b2b.git
   cd sofexpo-b2b
   ```

2. **Virtual muhitni yaratish va faollashtirish:**
   ```bash
   python -m venv .venv
   # Windows uchun:
   .venv\Scripts\activate
   # Linux/macOS uchun:
   source .venv/bin/activate
   ```

3. **Kutubxonalarni o'rnatish:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Atrof-muhit faylini (.env) sozlash:**
   `.env.example` faylidan nusxa olib `.env` yaratasiz va o'z ma'lumotlaringizni kiritasiz:
   ```env
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_IDS=12345678,87654321
   ADMIN_GROUP_ID=-1001234567890
   DB_PATH=sofexpo_b2b.db
   ```

5. **Botni ishga tushirish:**
   ```bash
   python main.py
   ```

---

## 🚀 Fly.io Servisiga Deploy Qilish

Fly.io da botni 24/7 rejimida joylashtirish uchun:

1. **Fly CLI ni o'rnating va akkauntingizga kiring:**
   ```bash
   fly auth login
   ```

2. **Persistent Volume yaratish (SQLite bazasi o'chib ketmasligi uchun):**
   ```bash
   fly volumes create sofexpo_data --region fra --size 1
   ```

3. **Secrets (BOT_TOKEN, ADMIN_GROUP_ID va ADMIN_IDS) ni sozlash:**
   ```bash
   fly secrets set BOT_TOKEN="bot_tokeningiz" ADMIN_GROUP_ID="-1001234567890" ADMIN_IDS="admin_idlar"
   ```

4. **Deploy qilish:**
   ```bash
   fly deploy
   ```

---

## 📊 Google Sheets Integratsiyasi (Ixtiyoriy)

1. Google Cloud Console da Service Account yaratasiz va JSON kalitni yuklab olib proyekt papkasiga `credentials.json` nomi bilan saqlaysiz.
2. Google Sheets jadvali yaratib, uni Service Account emailiga tahrirlash (Editor) huquqini berasiz.
3. `.env` fayliga Sheet ID ni kiritasiz:
   `GOOGLE_SPREADSHEET_ID=1abc...xyz`
