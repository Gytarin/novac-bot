import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from bot import dp, bot  # ваш Dispatcher и Bot

# Настройка
TOKEN = os.getenv("BOT_TOKEN")
HOSTNAME = os.getenv("RENDER_EXTERNAL_URL", "https://example.com")  # fallback
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{HOSTNAME}{WEBHOOK_PATH}"

app = FastAPI(title="Telegram Bot Webhook")

# Webhook setup
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    print("Webhook deleted, bot session closed")

# Telegram webhook endpoint
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        update = Update(**data)
        await dp.process_update(update)
    except Exception as e:
        print(f"Error processing update: {e}")
    return {"ok": True}
