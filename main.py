# Этот файл запускается на Railway и пересылает новые посты
# из каналов @vedexx_news, @customs_rf, @oVEDinfo в @clr_group_expert
# Только в рабочее время: 09:00 – 21:00 по Москве (MSK, UTC+3)

import os
import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# Загружаем переменные окружения из Railway
load_dotenv()

# ────────────────────────────────────────────────
# Переменные из Railway → Variables (обязательно!)
# ────────────────────────────────────────────────
api_id      = os.getenv("API_ID")      # 33887345
api_hash    = os.getenv("API_HASH")    # 27278fe9e005b6a7c4f77c42bef3ea08
sources_str = os.getenv("SOURCES")     # @vedexx_news,@customs_rf,@oVEDinfo
target_str  = os.getenv("TARGET")      # @clr_group_expert

# Проверки
if not api_id or not api_hash:
    print("ОШИБКА: API_ID или API_HASH не заданы в Variables")
    exit(1)

if not sources_str or not target_str:
    print("ОШИБКА: SOURCES или TARGET не заданы")
    exit(1)

try:
    api_id = int(api_id)
except ValueError:
    print("ОШИБКА: API_ID должен быть числом")
    exit(1)

sources_list = [s.strip() for s in sources_str.split(",") if s.strip()]

# Клиент в user-режиме (сессия user_session.session должна быть в репозитории)
client = TelegramClient("user_session", api_id, api_hash)

# Проверка времени 09:00–21:00 МСК (UTC+3)
def is_working_time():
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz)
    hour = now_msk.hour
    return 9 <= hour < 21

async def bot_main():
    print("Подключаемся к Telegram в user-режиме...")
    await client.start()

    print("\nЗагружаем каналы...")
    sources_entities = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)
            sources_entities.append(entity)
            title = entity.title or entity.username or src
            print(f"Успешно подключён источник: {src} → {title}")
        except Exception as e:
            print(f"Ошибка с источником {src}: {e}")

    try:
        target = await client.get_entity(target_str)
        title = target.title or target.username or target_str
        print(f"Целевой канал: {target_str} → {title}")
    except Exception as e:
        print(f"Ошибка с целевым каналом {target_str}: {e}")
        return

    # ────────────────────────────────────────────────
    # Обработчик новых сообщений (handler) с максимальной отладкой
    # ────────────────────────────────────────────────
    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        chat_name = event.chat.title or event.chat.username or "?"
        msg_time = event.date.strftime('%Y-%m-%d %H:%M:%S МСК')
        text_preview = event.message.text[:120] if event.message.text else "[медиа или без текста]"

        print(f"[EVENT] Получено новое сообщение из {chat_name} в {msg_time}")
        print(f"[EVENT] Текст: {text_preview}")
        print(f"[EVENT] ID сообщения: {event.message.id}")
        print(f"[EVENT] Текущее время МСК: {datetime.now(msk_tz).strftime('%H:%M:%S')}")

        if not is_working_time():
            print("Пропущено — вне рабочего времени 09:00–21:00 МСК")
            return

        try:
            msg = event.message
            msg.clear_forward()  # убираем надпись "Переслано из"
            await client.forward_messages(target, msg)
            print(f"[SUCCESS] Переслано из {chat_name} в {datetime.now(msk_tz).strftime('%H:%M:%S МСК')}")
        except Exception as e:
            print(f"[ERROR] Ошибка при пересылке: {e}")

    print("\n" + "═" * 70)
    print("БОТ ЗАПУЩЕН В USER-РЕЖИМЕ")
    print("Пересылка работает только с 09:00 до 21:00 по Москве")
    print("Жду новых сообщений...")
    print("═" * 70 + "\n")

    await client.run_until_disconnected()

# ────────────────────────────────────────────────
# Фейковый веб-сервер (FastAPI + uvicorn) — чтобы Railway не убивал контейнер
# ────────────────────────────────────────────────
app = FastAPI(title="Telegram Forward Bot", version="1.0")

@app.get("/")
def root():
    return {"status": "bot is running", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S МСК")}

@app.get("/health")
def health_check():
    return {"status": "healthy", "uptime": "alive"}

# ────────────────────────────────────────────────
# Запуск бота и веб-сервера в одном asyncio-цикле
# ────────────────────────────────────────────────
async def combined_main():
    # Запускаем Telegram-бота как задачу
    bot_task = asyncio.create_task(bot_main
