import os
from telethon import TelegramClient, events
import asyncio

# Получаем данные из переменных окружения
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")  # Получаем токен бота

# Каналы для получения новостей
source_channels = ["@vedexx_news", "@customs_rf", "@OVEDinfo"]

# Целевой канал для пересылки новостей
target_channel = "@clr_group_expert"  # Замените на свой канал

# Создаем клиента с использованием токена бота
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# Подписываемся на каналы и пересылаем сообщения
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        # Пересылаем сообщение в целевой канал
        await client.forward_messages(target_channel, event.message)
        print(f"Новость из {event.chat.username} переслана")
    except Exception as e:
        print(f"Ошибка: {e}")

# Основная асинхронная функция
async def main():
    print("Бот запущен...")
    await client.run_until_disconnected()  # Ожидаем сообщений

# Запуск основного кода через уже существующий цикл событий
if __name__ == '__main__':
    loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
    loop.run_until_complete(main())  # Запускаем main() в этом цикле
