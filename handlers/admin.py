import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS, ADMIN_GROUP_ID
from database.db import get_stats, get_all_registrations
from services.excel import generate_excel_report

logger = logging.getLogger(__name__)
admin_router = Router()

def is_admin_or_group(message: Message) -> bool:
    """Foydalanuvchi admin ekanligini yoki xabar admin guruhida yuborilganligini tekshiradi."""
    # Agarda guruhda yozilgan bo'lsa va ADMIN_GROUP_ID ga mos kelsa
    if ADMIN_GROUP_ID and message.chat.id == ADMIN_GROUP_ID:
        return True
    
    # Agarda ADMIN_IDS ro'yxatida bo'lsa
    if ADMIN_IDS and message.from_user and message.from_user.id in ADMIN_IDS:
        return True

    # Agarda hech qanday admin sozlanmagan bo'lsa (testing uchun)
    if not ADMIN_IDS and not ADMIN_GROUP_ID:
        return True

    return False

@admin_router.message(Command("stats"))
async def stats_command(message: Message):
    """Administratorlar va Telegram guruhi uchun umumiy statistika."""
    if not is_admin_or_group(message):
        await message.answer("⛔️ Kechirasiz, siz ushbu buyruqdan foydalanish huquqiga ega emassiz.")
        return

    stats = await get_stats()
    total = stats.get("total", 0)
    by_day = stats.get("by_day", {})
    by_purpose = stats.get("by_purpose", {})

    day_text = "\n".join([f"• {day}: {count} ta" for day, count in by_day.items()]) if by_day else "Ma'lumot yo'q"
    purpose_text = "\n".join([f"• {purpose}: {count} ta" for purpose, count in by_purpose.items()]) if by_purpose else "Ma'lumot yo'q"

    stats_msg = (
        f"📊 **SOF EXPO SAMARKAND B2B — Statistika & Analitika**\n\n"
        f"👥 **Jami arizalar:** {total} ta\n\n"
        f"📅 **Kelish kunlari bo'yicha:**\n{day_text}\n\n"
        f"🎯 **Tashrif maqsadi bo'yicha:**\n{purpose_text}"
    )

    await message.answer(stats_msg, parse_mode="Markdown")

@admin_router.message(Command("export"))
async def export_command(message: Message):
    """Barcha ma'lumotlarni Excel fayl ko'rinishida yuklab olish."""
    if not is_admin_or_group(message):
        await message.answer("⛔️ Kechirasiz, siz ushbu buyruqdan foydalanish huquqiga ega emassiz.")
        return

    wait_msg = await message.answer("⏳ Excel fayli shakllantirilmoqda, iltimos kuting...")

    registrations = await get_all_registrations()
    if not registrations:
        await wait_msg.edit_text("⚠️ Hali hech kim ro'yxatdan o'tmagan.")
        return

    excel_file = generate_excel_report(registrations)
    await message.answer_document(
        document=excel_file,
        caption=f"📊 SOF EXPO SAMARKAND B2B\nJami: {len(registrations)} ta ro'yxatdan o'tganlar bazasi."
    )
    await wait_msg.delete()
