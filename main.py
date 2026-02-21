# Этот файл запускается на Railway и пересылает новые посты
# из каналов @vedexx_news, @customs_rf, @oVEDinfo в @clr_group_expert
# Только в рабочее время: 09:00 – 21:00 по Москве (MSK, UTC+3)

import os
import asyncio
import threading
from telethon import TelegramClient, events
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

load_dotenv()

# ────────────────────────────────────────────────
# Переменные из Railway → Variables
# ────────────────────────────────────────────────
api_id      = os.getenv("API_ID")
api_hash    = os.getenv("API_HASH")
sources_str = os.getenv("SOURCES")
target_str  = os.getenv("TARGET")

if not api_id or not api_hash:
    print("ОШИБКА: API_ID или API_HASH не заданы")
    exit(1)

if not sources_str or not target_str:
    print("ОШИБКА: SOURCES или TARGET не заданы")
    exit(1)

api_id = int(api_id)
sources_list = [s.strip() for s in sources_str.split(",") if s.strip()]

client = TelegramClient("user_session", api_id, api_hash)

def is_working_time():
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz)
    return 9 <= now_msk.hour < 21

async def bot_main():
    print("Начало подключения к Telegram...")
    try:
        await client.start()
        print("Успешно подключены к Telegram в user-режиме!")
    except Exception as e:
        print(f"Ошибка подключения к Telegram: {e}")
        return

    print("\nЗагружаем каналы...")
    sources_entities = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)
            sources_entities.append(entity)
            print(f"Успешно: {src} → {entity.title or entity.username or src}")
        except Exception as e:
            print(f"Ошибка с {src}: {e}")

    try:
        target = await client.get_entity(target_str)
        print(f"Цель: {target_str} → {target.title or target.username or target_str}")
    except Exception as e:
        print(f"Ошибка с целью {target_str}: {e}")
        return

    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        chat_name = event.chat.title or event.chat.username or "?"
        msg_time = event.date.strftime('%Y-%m-%d %H:%M:%S МСК')
        text = event.message.text[:120] if event.message.text else "[медиа]"

        print(f"[EVENT] Новое сообщение из {chat_name} в {msg_time}")
        print(f"[EVENT] Текст: {text}")
        print(f"[EVENT] ID: {event.message.id}")

        if not is_working_time():
            print("Пропущено — вне 09:00–21:00 МСК")
            return

        try:
            msg = event.message
            msg.clear_forward()
            await client.forward_messages(target, msg)
            print(f"[SUCCESS] Переслано из {chat_name} в {datetime.now(msk_tz).strftime('%H:%M:%S МСК')}")
        except Exception as e:
            print(f"[ERROR] Пересылка не удалась: {e}")

    print("\n" + "═" * 70)
    print("БОТ ПОЛНОСТЬЮ ЗАПУЩЕН")
    print("Пересылка только с 09:00 до 21:00 МСК")
    print("Жду новых постов...")
    print("═" * 70 + "\n")

    await client.run_until_disconnected()

# Веб-сервер для Railway
app = FastAPI()

@app.get("/")
def root():
    return {"status": "bot running", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S МСК")}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Запуск
async def start_all():
    bot_task = asyncio.create_task(bot_main())
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    web_task = asyncio.create_task(server.serve())
    await asyncio.gather(bot_task, web_task)

if __name__ == "__main__":
    print("Стартуем всё...")
    asyncio.run(start_all())
