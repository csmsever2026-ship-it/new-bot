# Этот файл запускается на Railway и пересылает новые посты
# из каналов @vedexx_news, @customs_rf, @oVEDinfo в @clr_group_expert
# Только в рабочее время: 09:00 – 21:00 по Москве (MSK, UTC+3)

import os
import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения из Railway
load_dotenv()

# ────────────────────────────────────────────────
#   Переменные из Railway → Variables
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

# Проверки обязательных переменных
if not api_id or not api_hash:
    print("ОШИБКА: API_ID или API_HASH не заданы")
    exit(1)

if not bot_token:
    print("ОШИБКА: BOT_TOKEN не задан — рекомендуется использовать бота")
    # exit(1)  # можно закомментировать, если хочешь user-режим

if not sources_str or not target_str:
    print("ОШИБКА: SOURCES или TARGET не заданы")
    exit(1)

try:
    api_id = int(api_id)
except ValueError:
    print("ОШИБКА: API_ID должен быть числом")
    exit(1)

sources_list = [s.strip() for s in sources_str.split(",") if s.strip()]

# Создаём клиента (бот-режим)
print("Запускаемся в режиме БОТА")
client = TelegramClient("bot_session", api_id, api_hash)

# Функция проверки времени (09:00–21:00 MSK)
def is_working_time():
    # Текущее время в Москве (UTC+3)
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz)
    hour = now_msk.hour
    
    # 9:00 включительно — 21:00 не включительно (до 20:59:59)
    return 9 <= hour < 21

async def main():
    await client.start(bot_token=bot_token)
    print("Бот авторизован")

    print("\nЗагружаем каналы...")

    # Источники
    sources_entities = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)
            sources_entities.append(entity)
            title = entity.title or entity.username or src
            print(f"Успешно: {src} → {title}")
        except Exception as e:
            print(f"Ошибка с {src}: {e}")

    # Целевой канал
    try:
        target = await client.get_entity(target_str)
        title = target.title or target.username or target_str
        print(f"Цель: {target_str} → {title}")
    except Exception as e:
        print(f"Ошибка с целью {target_str}: {e}")
        return

    # Обработчик новых сообщений
    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        if not is_working_time():
            chat_name = event.chat.title or event.chat.username or "?"
            print(f"Вне рабочего времени (09–21 MSK) — пропущено сообщение из {chat_name}")
            return

        try:
            msg = event.message
            msg.clear_forward()  # убираем "Переслано из…"
            
            await client.forward_messages(target, msg)
            
            chat_name = event.chat.title or event.chat.username or "?"
            print(f"[OK] Переслано из {chat_name} в {datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S MSK')}")
        except Exception as e:
            print(f"Ошибка пересылки: {e}")

    print("\n" + "═" * 60)
    print("БОТ ЗАПУЩЕН")
    print("Пересылка работает только с 09:00 до 21:00 по Москве")
    print("Жду новых сообщений в источниках...")
    print("═" * 60 + "\n")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
