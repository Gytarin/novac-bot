import os
import logging
from fastapi import FastAPI, Request
from aiogram.types import Update
from bot import dp, bot

logging.basicConfig(level=logging.INFO)

app = FastAPI()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    logging.info("Бот завершил работу, сессия закрыта")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}
