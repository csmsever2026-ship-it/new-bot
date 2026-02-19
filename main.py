# Этот файл запускается на Railway и пересылает новые посты 
# из каналов @vedexx_news, @customs_rf, @oVEDinfo в @clr_group_expert

import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

# Загружаем переменные окружения из Railway (они задаются в разделе Variables)
load_dotenv()

# ────────────────────────────────────────────────
#   Эти значения берутся из Railway → Variables
#   Не пиши их прямо в коде!
# ────────────────────────────────────────────────
# API_ID      → 33887345
# API_HASH    → 27278fe9e005b6a7c4f77c42bef3ea08
# BOT_TOKEN   → 8332360026:AAENXiUqg515om9pTqLfqu1sDA4VScrWh_g
# SOURCES     → @vedexx_news,@customs_rf,@oVEDinfo
# TARGET      → @clr_group_expert
# ────────────────────────────────────────────────

api_id     = os.getenv("API_ID")
api_hash   = os.getenv("API_HASH")
bot_token  = os.getenv("BOT_TOKEN")
sources_str = os.getenv("SOURCES")
target_str  = os.getenv("TARGET")

# Проверяем, что все важные переменные заданы
if not api_id:
    print("ОШИБКА: API_ID не задан в Variables!")
    exit(1)

if not api_hash:
    print("ОШИБКА: API_HASH не задан в Variables!")
    exit(1)

if not bot_token:
    print("ОШИБКА: BOT_TOKEN не задан в Variables! (рекомендуется использовать бота)")
    # exit(1)  # закомментировал, чтобы можно было запустить и в user-режиме

if not sources_str:
    print("ОШИБКА: SOURCES не задан! Пример: @vedexx_news,@customs_rf,@oVEDinfo")
    exit(1)

if not target_str:
    print("ОШИБКА: TARGET не задан! Пример: @clr_group_expert")
    exit(1)

# Преобразуем api_id в число
try:
    api_id = int(api_id)
except ValueError:
    print("ОШИБКА: API_ID должен быть числом!")
    exit(1)

# Разбиваем SOURCES на список
sources_list = [s.strip() for s in sources_str.split(",") if s.strip()]

# Создаём клиента
if bot_token:
    print("Запускаемся в режиме БОТА")
    client = TelegramClient("bot_session", api_id, api_hash)
else:
    print("Запускаемся в режиме USERBOT (личный аккаунт)")
    client = TelegramClient("user_session", api_id, api_hash)

async def main():
    # Запускаем клиент
    if bot_token:
        await client.start(bot_token=bot_token)
    else:
        await client.start()  # здесь может попросить номер и код один раз

    print("\nЗагружаем каналы...")

    # Подключаемся к источникам
    sources_entities = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)
            sources_entities.append(entity)
            title = entity.title if hasattr(entity, "title") else entity.username or src
            print(f"Успешно: {src} → {title}")
        except Exception as e:
            print(f"Ошибка с {src}: {e}")
            print("   • канал приватный? • не подписан? • опечатка в @username?")

    # Подключаемся к целевому каналу
    try:
        target = await client.get_entity(target_str)
        title = target.title if hasattr(target, "title") else target.username or target_str
        print(f"Цель: {target_str} → {title}")
    except Exception as e:
        print(f"Ошибка с целевым каналом {target_str}: {e}")
        print("Проверь: бот — админ в канале с правом отправлять сообщения")
        return

    # Обработчик новых сообщений
    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        try:
            msg = event.message
            msg.clear_forward()          # убираем "Переслано из…"
            await client.forward_messages(target, msg)
            print(f"Переслано из {event.chat.title or event.chat.username}")
        except Exception as e:
            print(f"Ошибка пересылки: {e}")

    print("\n" + "═" * 60)
    print("ВСЁ ГОТОВО! Ожидаю новые посты в источниках…")
    print("Для проверки: опубликуй тестовый пост в одном из каналов")
    print("═" * 60 + "\n")

    await client.run_until_disconnected()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
