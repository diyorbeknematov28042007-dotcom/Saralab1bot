import asyncio
import os
from aiohttp import web
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from database.db import create_pool
from handlers import user, admin

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 8000))

async def health(request):
    return web.Response(text="OK")

async def on_startup(bot: Bot):
    try:
        print("Connecting to database...")
        await create_pool()
        print("Database connected!")
        await bot.set_webhook(WEBHOOK_URL)
        print(f"Webhook set: {WEBHOOK_URL}")
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        raise

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
