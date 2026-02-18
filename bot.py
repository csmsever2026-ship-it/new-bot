import os
from telethon import TelegramClient, events

# Получаем данные из переменных окружения
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
phone_number = os.environ.get("PHONE_NUMBER")  # Получаем номер телефона

# Каналы для получения новостей
source_channels = ["@vedexx_news", "@customs_rf", "@OVEDinfo"]

# Целевой канал для пересылки новостей
target_channel = "clr_group_expert"  # Замените на свой канал

# Создаем клиента
client = TelegramClient('session_name', api_id, api_hash)

# Функция для авторизации
async def start_client():
    if phone_number:  # Если используется номер телефона
        await client.start(phone_number)
    else:
        await client.start()  # Если используется Bot API (например, через токен)

# Подписываемся на каналы и пересылаем сообщения
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        # Пересылаем сообщение в целевой канал
        await client.forward_messages(target_channel, event.message)
        print(f"Новость из {event.chat.username} переслана")
    except Exception as e:
        print(f"Ошибка: {e}")

# Запуск клиента
print("Бот запущен...")
client.start()
client.run_until_disconnected()
