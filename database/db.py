import aiosqlite
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

async def init_db():
    """Ma'lumotlar bazasini va jadvallarni yaratadi."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                position TEXT NOT NULL,
                company TEXT NOT NULL,
                industry TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                visit_day TEXT NOT NULL,
                visit_purpose TEXT NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        logger.info("Database initialization completed.")

async def save_registration(data: dict) -> int:
    """Yangi anketa ma'lumotlarini saqlaydi."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO registrations (
                telegram_id, username, full_name, position, company,
                industry, country, city, phone, email, visit_day,
                visit_purpose, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("telegram_id"),
            data.get("username", ""),
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
        ))
        await db.commit()
        return cursor.lastrowid

async def get_stats() -> dict:
    """Statistika ma'lumotlarini qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM registrations") as cursor:
            total_count = (await cursor.fetchone())[0]

        # Kelish kunlari bo'yicha guruhlash
        async with db.execute(
            "SELECT visit_day, COUNT(*) FROM registrations GROUP BY visit_day"
        ) as cursor:
            by_day = await cursor.fetchall()

        # Tashrif maqsadi bo'yicha guruhlash
        async with db.execute(
            "SELECT visit_purpose, COUNT(*) FROM registrations GROUP BY visit_purpose"
        ) as cursor:
            by_purpose = await cursor.fetchall()

        return {
            "total": total_count,
            "by_day": dict(by_day),
            "by_purpose": dict(by_purpose)
        }

async def get_all_registrations() -> list:
    """Barcha ro'yxatdan o'tganlarni ro'yxat shaklida qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM registrations ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
