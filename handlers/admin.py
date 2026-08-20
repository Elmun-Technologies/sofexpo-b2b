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
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id

    # 1. Agarda xabar ADMIN_GROUP_ID da yuborilgan bo'lsa
    if ADMIN_GROUP_ID and chat_id == ADMIN_GROUP_ID:
        return True

    # 2. Agarda foydalanuvchi ADMIN_IDS ro'yxatida bo'lsa
    if ADMIN_IDS and user_id in ADMIN_IDS:
        return True

    # 3. Agarda guruhda yozilgan bo'lib, ADMIN_GROUP_ID sozlanmagan bo'lsa
    if message.chat.type in ["group", "supergroup"]:
        return True

    # 4. Agarda hech qanday admin sozlanmagan bo'lsa
    if not ADMIN_IDS and not ADMIN_GROUP_ID:
        return True

    return False

@admin_router.message(Command("stats", "analytics", "analitika"))
async def stats_command(message: Message):
    """Administratorlar va Telegram guruhi uchun to'liq analitika va statistika."""
    if not is_admin_or_group(message):
        await message.answer("⛔️ Kechirasiz, siz ushbu buyruqdan foydalanish huquqiga ega emassiz.")
        return

    stats = await get_stats()
    total = stats.get("total", 0)
    today = stats.get("today", 0)
    by_industry = stats.get("by_industry", {})
    by_day = stats.get("by_day", {})
    by_purpose = stats.get("by_purpose", {})
    by_country = stats.get("by_country", {})

    industry_text = "\n".join([f"  • {ind}: **{count} ta**" for ind, count in by_industry.items()]) if by_industry else "  • Ma'lumot yo'q"
    day_text = "\n".join([f"  • {day}: **{count} ta**" for day, count in by_day.items()]) if by_day else "  • Ma'lumot yo'q"
    purpose_text = "\n".join([f"  • {purpose}: **{count} ta**" for purpose, count in by_purpose.items()]) if by_purpose else "  • Ma'lumot yo'q"
    country_text = "\n".join([f"  • {country}: **{count} ta**" for country, count in by_country.items()]) if by_country else "  • Ma'lumot yo'q"

    stats_msg = (
        f"📊 **SOF EXPO SAMARKAND B2B — Analitika & Statistika**\n\n"
        f"👥 **Jami arizalar:** **{total} ta**\n"
        f"📅 **Bugungi arizalar:** **{today} ta**\n\n"
        f"🏭 **Faoliyat sohalari (Kategoriyalar) bo'yicha:**\n{industry_text}\n\n"
        f"📅 **Kelish kunlari bo'yicha:**\n{day_text}\n\n"
        f"🎯 **Tashrif maqsadi bo'yicha:**\n{purpose_text}\n\n"
        f"🌍 **Mamlakatlar bo'yicha:**\n{country_text}\n\n"
        f"💡 *Excel hisobotni yuklash uchun `/excel` yoki `/export` buyrug'ini yuboring.*"
    )

    await message.answer(stats_msg, parse_mode="Markdown")

@admin_router.message(Command("excel", "export"))
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
        caption=f"📊 **SOF EXPO SAMARKAND B2B**\nJami: **{len(registrations)} ta** ro'yxatdan o'tganlar bazasi.",
        parse_mode="Markdown"
    )
    await wait_msg.delete()

@admin_router.message(Command("help", "admin"))
async def admin_help_command(message: Message):
    """Admin va guruh buyruqlari ro'yxati."""
    if not is_admin_or_group(message):
        return

    help_text = (
        "🛠 **Admin & Guruh buyruqlari:**\n\n"
        "📊 `/stats` yoki `/analytics` - Kategoriyalar va umumiy analitikani ko'rish\n"
        "📥 `/excel` yoki `/export` - Barcha foydalanuvchilar bazasini Excel `.xlsx` faylda yuklab olish\n"
        "ℹ️ `/help` - Ushbu yordam oynasi"
    )
    await message.answer(help_text, parse_mode="Markdown")
