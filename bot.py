import os, httpx, asyncio, re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from telethon import TelegramClient, events

# --- ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = TelegramClient('admin_session', API_ID, API_HASH)

class AuthState(StatesGroup):
    waiting_for_code = State()

# Клавиатура с кнопкой контакта
kb_contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📱 Поделиться номером", request_contact=True)]
], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("Привет! Нажми на кнопку ниже, чтобы авторизовать свой аккаунт в системе.", reply_markup=kb_contact)

@dp.message(F.contact)
async def get_contact(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    await client.connect()
    try:
        await client.send_code_request(phone)
        await message.answer(f"📩 Код подтверждения отправлен на номер {phone}.\nВведите его в ответном сообщении:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(AuthState.waiting_for_code)
    except Exception as e:
        await message.answer(f"❌ Ошибка запроса кода: {e}")

@dp.message(AuthState.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    try:
        await client.sign_in(phone, message.text)
        await message.answer("✅ **Авторизация успешна!**\nТеперь используйте /get_code для перехвата пароля с сайта.", parse_mode="Markdown")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Ошибка входа: {e}. Попробуйте снова /start")

@dp.message(Command("get_code"))
async def cmd_get_code(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    phone = data.get("phone")
    
    if not await client.is_user_authorized():
        await message.answer("⚠️ Сначала нужно авторизоваться через /start")
        return

    async with httpx.AsyncClient() as web:
        await message.answer("🌐 Запрашиваю код на my.telegram.org...")
        await web.post("https://my.telegram.org", data={"phone": phone})

        @client.on(events.NewMessage(from_users=777000))
        async def handler(event):
            match = re.search(r'code:\s*([a-zA-Z0-9]+)', event.raw_text)
            if match:
                code = match.group(1)
                await message.answer(f"🔑 **ВАШ КОД ДЛЯ САЙТА:** `{code}`", parse_mode="Markdown")
                client.remove_event_handler(handler)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
