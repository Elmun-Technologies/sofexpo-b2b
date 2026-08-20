import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN sozlanmagan! Iltimos environment variable yoki .env faylida BOT_TOKEN ni ko'rsating.")
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # Fly.io health check serverini parallel ishga tushirish
    try:
        await start_web_server()
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash (Admin va User)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    logger.info("Bot muvaffaqiyatli ishga tushdi...")
    
    # Eskirgan webhook va yangilanishlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
