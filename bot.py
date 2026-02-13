import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)

# =========================
# ❗ ВАЖНО: ЗАПОЛНИТЕ СВОИ ДАННЫЕ
# =========================
TOKEN = "8525113234:AAGlmmXn6ZtT_f0wsQReAXIPB3Zwz09H4Hg"
ADMIN_ID = 548463456  # ← Вставьте ваш Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# =========================
# КЛАВИАТУРЫ
# =========================
def currency_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 Доллар", callback_data="currency_usd"),
            InlineKeyboardButton(text="💶 Евро", callback_data="currency_eur"),
            InlineKeyboardButton(text="🇦🇪 Дирхам", callback_data="currency_aed")
        ],
        [InlineKeyboardButton(text="🇨🇳 Юань", callback_data="currency_cny")]
    ])

def post_calc_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Оставить заявку", callback_data="leave_lead")],
        [InlineKeyboardButton(text="↩️ Сделать ещё расчет", callback_data="restart")]
    ])

def restart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Сделать ещё расчет", callback_data="restart")]
    ])

# =========================
# КОМИССИИ
# =========================
commission_rates = {
    "Доллар": [(0, 50000, 0.021), (50001, 100000, 0.018), (100001, 500000, 0.015), (500001, float("inf"), 0.01)],
    "Евро": [(0, 50000, 0.021), (50001, 100000, 0.018), (100001, 500000, 0.015), (500001, float("inf"), 0.01)],
    "Дирхам": [(0, 50000, 0.021), (50001, 100000, 0.018), (100001, 500000, 0.015), (500001, float("inf"), 0.01)],
    "Юань": [(0, 50000, 0.025), (50001, 100000, 0.021), (100001, 500000, 0.018), (500001, float("inf"), 0.015)]
}

def calculate_commission(currency, amount):
    for lower, upper, rate in commission_rates[currency]:
        if lower <= amount <= upper:
            return rate, round(amount * rate, 2)
    return 0, 0

def format_number(n):
    return f"{int(n):,}".replace(",", " ")  # узкий пробел для красоты

# =========================
# START
# =========================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {"step": "currency"}

    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "без username"
        await bot.send_message(
            ADMIN_ID,
            f"🟢 Новый старт бота\n\n"
            f"👤 Имя: {message.from_user.full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🌍 Язык: {message.from_user.language_code}"
        )
    except Exception as e:
        logging.warning(f"Ошибка уведомления администратору: {e}")

    await message.answer(
        "🚀 <b>NovaCPay — международные переводы с минимальной комиссией</b>\n\n"
        "Выберите валюту перевода:",
        reply_markup=currency_keyboard(),
        parse_mode="HTML"
    )

# =========================
# ВЫБОР ВАЛЮТЫ
# =========================
@dp.callback_query(lambda c: c.data.startswith("currency"))
async def process_currency(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    currency_map = {
        "currency_usd": "Доллар",
        "currency_eur": "Евро",
        "currency_aed": "Дирхам",
        "currency_cny": "Юань"
    }
    user_data[user_id] = {"currency": currency_map[callback.data], "step": "amount"}

    await callback.message.edit_text(
        f"💰 Вы выбрали: <b>{user_data[user_id]['currency']}</b>\n\n"
        "Введите сумму перевода в цифрах (например: 1 330 700):",
        parse_mode="HTML"
    )

# =========================
# ПОВТОРНЫЙ РАСЧЕТ
# =========================
@dp.callback_query(lambda c: c.data in ["restart"])
async def restart_calc(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.edit_text(
        "↩️ Выберите валюту для нового расчета:",
        reply_markup=currency_keyboard()
    )
    user_data[user_id]["step"] = "currency"

# =========================
# ОБРАБОТКА КОНТАКТА
# =========================
@dp.message(lambda message: message.contact is not None)
async def get_contact(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    phone = message.contact.phone_number
    username = message.from_user.username or "нет username"

    try:
        await bot.send_message(ADMIN_ID, 
            f"🔥 <b>НОВЫЙ ЛИД!</b>\n\n"
            f"👤 Username: @{username}\n"
            f"📱 Телефон: {phone}\n"
            f"💳 Валюта: {data.get('currency', 'не выбрана')}\n"
            f"💰 Сумма: {format_number(data.get('amount',0))}\n"
            f"📊 Комиссия: {data.get('commission','не рассчитана')}", 
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки заявки администратору: {e}")

    await message.answer(
        "✅ Спасибо! Ваша заявка успешно отправлена.\n"
        "Наши менеджеры свяжутся с вами в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )

    await message.answer(
        "↩️ Вы можете сделать ещё один расчет:",
        reply_markup=restart_keyboard()
    )

    user_data[user_id]["step"] = "done"

# =========================
# ОБРАБОТКА СУММЫ
# =========================
@dp.message(lambda message: message.contact is None)
async def process_amount(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") != "amount":
        return

    try:
        raw_text = message.text.replace(" ", "").replace(",", "")
        amount = float(raw_text)
        if amount < 10000:
            await message.answer("❌ Минимальная сумма должна быть больше 10 000")
            return
    except ValueError:
        await message.answer("❌ Введите корректную сумму числом (например: 1 330 700)")
        return

    user_data[user_id]["amount"] = amount
    currency = user_data[user_id]["currency"]
    rate, commission = calculate_commission(currency, amount)
    user_data[user_id]["commission"] = commission

    await message.answer(
        f"💰 Сумма перевода: {format_number(amount)} {currency}\n"
        f"💳 Комиссия: {format_number(commission)} {currency}\n\n"
        "Что вы хотите сделать дальше?",
        reply_markup=post_calc_keyboard()
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
