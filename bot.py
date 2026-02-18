from telethon import TelegramClient, events
import os

# Получаем api_id и api_hash из переменных окружения
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")

# Создаем клиент Telethon
client = TelegramClient('session_name', api_id, api_hash)

# Подписываемся на каналы
async def join_channels():
    # Перечисляем каналы для подписки
    channels_to_join = [
        "vedexx_news", 
        "customs_rf", 
        "OVEDinfo"
    ]
    
    for channel in channels_to_join:
        # Подписываемся на канал
        await client(JoinChannel(channel))
        print(f"Подписались на канал: {channel}")

# Функция для получения новостей и пересылки в целевой канал
@client.on(events.NewMessage)
async def handler(event):
    # Проверяем, откуда пришло сообщение (по username канала)
    if event.chat.username in ["vedexx_news", "customs_rf", "OVEDinfo"]:
        message = event.message.text
        target_channel = "clr_group_expert"  # Замените на свой канал
        await client.send_message(target_channel, message)
        print(f"Пересылаем сообщение в {target_channel}")

# Запуск подписки и клиента
async def main():
    await client.start()
    await join_channels()
    print("Подписались на каналы и готовы получать новости!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
