import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, events

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

source_channels = ["@vedexx_news", "@customs_rf", "@OVEDinfo"]
target_channel = "@clr_group_expert"  # замени на свой

client = TelegramClient('session_name', api_id, api_hash)

# Московская зона
moscow_tz = pytz.timezone("Europe/Moscow")

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    now_moscow = datetime.now(moscow_tz)
    hour = now_moscow.hour

    # Проверяем время
    if 9 <= hour < 21:
        try:
            await client.forward_messages(target_channel, event.message)
            print(f"Опубликовано в {hour}:{now_moscow.minute}")
        except Exception as e:
            print(f"Ошибка: {e}")
    else:
        print(f"Новость пропущена (время {hour}:{now_moscow.minute})")

async def main():
    await client.start(bot_token=bot_token)
    print("Бот запущен...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
