import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError

from config import BOT_TOKEN
from database.db import init_db
from handlers.user import user_router
from handlers.admin import admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def handle_health_check(request):
    """Fly.io health check va status sahifasi."""
    return web.Response(text="SOF EXPO SAMARKAND B2B Bot is running 🚀", status=200)

async def start_web_server():
    """Fly.io port checks (8080) uchun kichik HTTP server yaratish."""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP server {port}-portda ishga tushdi.")

async def setup_bot_commands(bot: Bot):
    """Telegram tugmasida buyruqlar menyusini (Bot Commands) o'rnatish."""
    commands = [
        BotCommand(command="start", description="🔄 Botni ishga tushirish / Перезапустить / Restart"),
        BotCommand(command="cancel", description="❌ Anketani bekor qilish / Отмена / Cancel"),
        BotCommand(command="stats", description="📊 Statistika va analitika (Admin & Group)"),
        BotCommand(command="excel", description="📥 Excel bazasini yuklab olish (.xlsx)"),
        BotCommand(command="help", description="ℹ️ Admin yordam menyusi")
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot buyruqlar menyusi (set_my_commands) muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.error(f"Bot buyruqlarini o'rnatishda xatolik: {e}")

async def main():
    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # Fly.io health check serverini parallel ishga tushirish
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN sozlanmagan! Iltimos Fly.io secrets da BOT_TOKEN ni o'rnating (`fly secrets set BOT_TOKEN=...`).")
        while True:
            await asyncio.sleep(3600)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash (Admin va User)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Telegram menyu buyruqlarini o'rnatish
    await setup_bot_commands(bot)

    logger.info("Bot muvaffaqiyatli ishga tushmoqda...")

    while True:
        try:
            # Eskirgan webhook va pending updates ni tozalash
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Polling boshlandi.")
            await dp.start_polling(bot, handle_signals=False)
        except (TelegramNetworkError, TelegramAPIError) as e:
            logger.error(f"Telegram API xatoligi: {e}. 5 sekunddan so'ng qayta ulaniladi...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Kutilmagan bot xatosi: {e}. 5 sekunddan so'ng qayta ishga tushiriladi...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
