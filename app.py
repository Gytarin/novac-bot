import os
import logging
import asyncio
from fastapi import FastAPI, Request
from bot import bot, dp  # импортируем существующие bot и dp из bot.py
from aiogram.types import Update

PORT = int(os.getenv("PORT", 10000))
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{HOSTNAME}{WEBHOOK_PATH}"

app = FastAPI()

# Устанавливаем webhook при старте
@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

# Обработка POST-запросов от Telegram
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}
