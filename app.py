from fastapi import FastAPI, Request
from bot import dp, bot  # импорт диспетчера и бота из bot.py
import asyncio

app = FastAPI()

WEBHOOK_PATH = f"/webhook/{bot.token}"
WEBHOOK_URL = f"https://YOUR-RENDER-URL.com{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    # Устанавливаем webhook
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

# Заливка по GET для Render или проверки
@app.get("/")
async def root():
    return {"status": "Bot is running"}
