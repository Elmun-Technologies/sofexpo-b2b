import os
import logging
from datetime import datetime
from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SPREADSHEET_ID

logger = logging.getLogger(__name__)

async def append_to_google_sheet(data: dict):
    """Google Sheets jadvaliga yangi ro'yxatdan o'tgan ma'lumotlarini qo'shadi."""
    if not GOOGLE_SPREADSHEET_ID or not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
        logger.info("Google Sheets integratsiyasi sozlanmagan yoki credentials fayli topilmadi.")
        return

    try:
        import gspread
        gc = gspread.service_account(filename=GOOGLE_SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(GOOGLE_SPREADSHEET_ID)
        worksheet = sh.get_worksheet(0)

        # Agarda jadval sarlavhasi yo'q bo'lsa yaratish
        existing = worksheet.get_all_values()
        if not existing:
            headers = [
                "Vaqt", "Telegram ID", "Username", "Til", "Ism va Familiya",
                "Lavozim", "Kompaniya", "Faoliyat sohasi", "Mamlakat",
                "Shahar", "Telefon", "Email", "Kelish kuni",
                "Tashrif maqsadi", "Qo'shimcha izoh"
            ]
            worksheet.append_row(headers)

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("telegram_id"),
            f"@{data.get('username')}" if data.get("username") else "",
            data.get("language", "uz"),
            data.get("full_name"),
            data.get("position"),
            data.get("company"),
            data.get("industry"),
            data.get("country"),
            data.get("city"),
            data.get("phone"),
            data.get("email", ""),
            data.get("visit_day"),
            data.get("visit_purpose"),
            data.get("comment", "")
        ]

        worksheet.append_row(row)
        logger.info("Google Sheets-ga ma'lumot muvaffaqiyatli saqlandi.")
    except Exception as e:
        logger.error(f"Google Sheets ga saqlashda xatolik yuz berdi: {e}")
