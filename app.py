import os
import logging
import asyncio

from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from bot import dp, bot  # Импортируем ваш Dispatcher и Bot из bot.py

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Создаём FastAPI приложение
app = FastAPI()

# URL для webhook, Telegram будет слать POST сюда
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

# =========================
# Startup / Shutdown
# =========================
@app.on_event("startup")
async def on_startup():
    # Устанавливаем webhook у Telegram
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        logging.error(f"Ошибка установки webhook: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    # Закрываем сессии бота
    await bot.session.close()
    logging.info("Бот завершил работу, сессия закрыта")

# =========================
# FastAPI route для Telegram webhook
# =========================
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        # Передаём обновление в Dispatcher
        update = dp.update_types.get("update")(data)
        await dp.process_update(update)
    except Exception as e:
        logging.error(f"Ошибка обработки update: {e}")
    return Response(status_code=200)

# =========================
# Опциональный route для проверки работы сервера
# =========================
@app.get("/")
async def root():
    return {"status": "ok"}
