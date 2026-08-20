import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin ID lar va Admin Gruppa ID si
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]

ADMIN_GROUP_ID_STR = os.getenv("ADMIN_GROUP_ID", "")
ADMIN_GROUP_ID = int(ADMIN_GROUP_ID_STR.strip()) if ADMIN_GROUP_ID_STR.strip().lstrip('-').isdigit() else None

# Ma'lumotlar bazasi fayli manzili
DB_PATH = os.getenv("DB_PATH", "sofexpo_b2b.db")

# Google Sheets konfiguratsiyasi
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
