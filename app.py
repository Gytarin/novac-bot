import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from bot import dp, bot  # твой bot и dp

TOKEN = os.getenv("BOT_TOKEN")
HOSTNAME = os.getenv("RENDER_EXTERNAL_URL")  # Render автоматически даёт эту переменную
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{HOSTNAME}{WEBHOOK_PATH}"

app = FastAPI()

# Webhook
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

# Telegram webhook endpoint
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = types.Update(**data)
    await dp.feed_update(update)  # <-- aiogram 3.x
    return {"ok": True}

# Healthcheck для внешнего пинга
@app.get("/")
async def healthcheck():
    return {"status": "ok"}
