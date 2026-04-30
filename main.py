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
    await create_pool()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Bot started, webhook: {WEBHOOK_URL}")
