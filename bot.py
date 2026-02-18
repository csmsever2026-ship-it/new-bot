import os
from telethon import TelegramClient, events

# Берем данные из переменных окружения
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

# Каналы-источники
source_channels = [
    "vedexx_news",
    "customs_rf",
    "OVEDinfo"
]

# Куда пересылать (твой канал)
target_channel = "clr_group_expert"

# Создаем клиента
client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        await client.forward_messages(
            target_channel,
            event.message
        )
        print("Новость переслана")
    except Exception as e:
        print("Ошибка:", e)

print("Бот запущен...")
client.start()
client.run_until_disconnected()
