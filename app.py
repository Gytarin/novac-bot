import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot import dp, bot  # импортируем твой bot и dp из bot.py

# Настройка
TOKEN = os.getenv("BOT_TOKEN")
HOSTNAME = os.getenv("RENDER_EXTERNAL_URL")  # Render автоматически даёт эту переменную
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{HOSTNAME}{WEBHOOK_PATH}"

app = FastAPI()

# Подключаем webhook
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

# Точка входа для Telegram
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}
