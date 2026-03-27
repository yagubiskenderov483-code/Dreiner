import telebot
import json
import httpx
import asyncio
import re
from telebot import types
from telethon import TelegramClient, events

# --- ТВОИ ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com" # Твоя ссылка от Render

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('admin_session', API_ID, API_HASH)

# Команда /start добавляет кнопку Mini App в меню
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    
    # Создаем кнопку Web App для меню (слева внизу)
    web_app = types.WebAppInfo(WEB_APP_URL)
    menu_button = types.MenuButtonWebApp(type="web_app", text="Auth Panel", web_app=web_app)
    bot.set_chat_menu_button(message.chat.id, menu_button)
    
    bot.send_message(message.chat.id, "🚀 **Бот запущен!**\nНажми кнопку «Auth Panel» в меню, чтобы ввести номер.")

# Обработка данных, пришедших из Mini App
@bot.message_handler(content_types=['web_app_data'])
def answer(message):
    if message.from_user.id != ADMIN_ID: return
    
    # Получаем номер из JSON данных Mini App
    data = json.loads(message.web_app_data.data)
    phone = data.get("phone")
    
    bot.send_message(message.chat.id, f"⏳ Номер `{phone}` принят. Запрашиваю код на my.telegram.org...", parse_mode="Markdown")
    
    # Запускаем асинхронную часть через отдельный поток/цикл
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_site_code(message.chat.id, phone))

async def get_site_code(chat_id, phone):
    await client.connect()
    
    # Если юзербот не авторизован (нужно ввести код в КОНСОЛИ хостинга)
    if not await client.is_user_authorized():
        bot.send_message(chat_id, "⚠️ Юзербот не авторизован! Проверь консоль на BotHost и введи код.")
        return

    async with httpx.AsyncClient() as web:
        # Запрос на сайт
        await web.post("https://my.telegram.org", data={"phone": phone})

        # Перехват кода от официального аккаунта Telegram (777000)
        @client.on(events.NewMessage(from_users=777000))
        async def handler(event):
            match = re.search(r'code:\s*([a-zA-Z0-9]+)', event.raw_text)
            if match:
                login_code = match.group(1)
                bot.send_message(chat_id, f"✅ **КОД С САЙТА ПЕРЕХВАЧЕН:**\n`{login_code}`", parse_mode="Markdown")
                client.remove_event_handler(handler)
        
        # Ждем сообщения 2 минуты, потом отключаемся
        try:
            await asyncio.wait_for(client.run_until_disconnected(), timeout=120)
        except asyncio.TimeoutError:
            pass

if __name__ == '__main__':
    print("Бот запущен на telebot! Проверь кнопку в Telegram.")
    bot.infinity_polling()
