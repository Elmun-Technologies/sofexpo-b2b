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
                language TEXT DEFAULT 'uz',
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
        
        # Add language column if db already existed without it
        try:
            await db.execute("ALTER TABLE registrations ADD COLUMN language TEXT DEFAULT 'uz'")
        except Exception:
            pass

        # Guruh va analitika jadvallari
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_id, telegram_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                telegram_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
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
                telegram_id, username, language, full_name, position, company,
                industry, country, city, phone, email, visit_day,
                visit_purpose, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("telegram_id"),
            data.get("username", ""),
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
        ))
        await db.commit()
        return cursor.lastrowid

async def get_stats() -> dict:
    """Statistika ma'lumotlarini qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM registrations") as cursor:
            total_count = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM registrations WHERE DATE(created_at) = DATE('now')") as cursor:
            today_count = (await cursor.fetchone())[0]

        # Faoliyat sohasi (kategoriya) bo'yicha guruhlash
        async with db.execute(
            "SELECT industry, COUNT(*) FROM registrations GROUP BY industry ORDER BY COUNT(*) DESC"
        ) as cursor:
            by_industry = await cursor.fetchall()

        # Kelish kunlari bo'yicha guruhlash
        async with db.execute(
            "SELECT visit_day, COUNT(*) FROM registrations GROUP BY visit_day ORDER BY COUNT(*) DESC"
        ) as cursor:
            by_day = await cursor.fetchall()

        # Tashrif maqsadi bo'yicha guruhlash
        async with db.execute(
            "SELECT visit_purpose, COUNT(*) FROM registrations GROUP BY visit_purpose ORDER BY COUNT(*) DESC"
        ) as cursor:
            by_purpose = await cursor.fetchall()

        # Mamlakatlar bo'yicha guruhlash
        async with db.execute(
            "SELECT country, COUNT(*) FROM registrations GROUP BY country ORDER BY COUNT(*) DESC"
        ) as cursor:
            by_country = await cursor.fetchall()

        # Tillar bo'yicha guruhlash
        async with db.execute(
            "SELECT language, COUNT(*) FROM registrations GROUP BY language ORDER BY COUNT(*) DESC"
        ) as cursor:
            by_lang = await cursor.fetchall()

        return {
            "total": total_count,
            "today": today_count,
            "by_industry": dict(by_industry),
            "by_day": dict(by_day),
            "by_purpose": dict(by_purpose),
            "by_country": dict(by_country),
            "by_language": dict(by_lang)
        }

async def get_all_registrations() -> list:
    """Barcha ro'yxatdan o'tganlarni ro'yxat shaklida qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM registrations ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def register_group_user(group_id: int, telegram_id: int, username: str, full_name: str):
    """Guruh foydalanuvchisini ro'yxatga olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO group_users (group_id, telegram_id, username, full_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(group_id, telegram_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name
        """, (group_id, telegram_id, username, full_name))
        await db.commit()

async def log_activity(group_id: int, telegram_id: int, action_type: str):
    """Guruhdagi foydalanuvchi faolligini log qilish."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO activity_logs (group_id, telegram_id, action_type)
            VALUES (?, ?, ?)
        """, (group_id, telegram_id, action_type))
        await db.commit()

async def get_group_stats(group_id: int) -> dict:
    """Guruh statistikasi va analitikasini olish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(DISTINCT telegram_id) FROM group_users WHERE group_id = ?", (group_id,)) as cursor:
            total_members = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM activity_logs WHERE group_id = ?", (group_id,)) as cursor:
            total_actions = (await cursor.fetchone())[0]

        async with db.execute(
            "SELECT action_type, COUNT(*) FROM activity_logs WHERE group_id = ? GROUP BY action_type",
            (group_id,)
        ) as cursor:
            action_counts = await cursor.fetchall()

        return {
            "total_members": total_members,
            "total_actions": total_actions,
            "action_counts": dict(action_counts)
        }
