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

# Загружаем переменные окружения из Railway
load_dotenv()

# ────────────────────────────────────────────────
# Переменные из Railway → Variables
# ────────────────────────────────────────────────
api_id      = os.getenv("API_ID")     # 33887345
api_hash    = os.getenv("API_HASH")   # 27278fe9e005b6a7c4f77c42bef3ea08
sources_str = os.getenv("SOURCES")    # @vedexx_news,@customs_rf,@oVEDinfo
target_str  = os.getenv("TARGET")     # @clr_group_expert

# Проверки обязательных переменных
if not api_id or not api_hash:
    print("ОШИБКА: API_ID или API_HASH не заданы")
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

# Клиент в user-режиме (сессия user_session.session уже в репозитории)
client = TelegramClient("user_session", api_id, api_hash)

# Проверка времени 09:00–21:00 MSK
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
            print(f"Успешно: {src} → {title}")
        except Exception as e:
            print(f"Ошибка с {src}: {e}")

    try:
        target = await client.get_entity(target_str)
        title = target.title or target.username or target_str
        print(f"Цель: {target_str} → {title}")
    except Exception as e:
        print(f"Ошибка с целью {target_str}: {e}")
        return

    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        chat_name = event.chat.title or event.chat.username or "?"
        msg_time = event.date.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[DEBUG] Получено сообщение из {chat_name} в {msg_time}")
        print(f"[DEBUG] Текст: {event.message.text[:100]}..." if event.message.text else "[DEBUG] Без текста (медиа)")

        if not is_working_time():
            print(f"Вне времени 09–21 МСК — пропущено из {chat_name}")
            return

        try:
            msg = event.message
            msg.clear_forward()  # убираем "Переслано из…"
            await client.forward_messages(target, msg)
            print(f"[OK] Переслано из {chat_name} в {datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S МСК')}")
        except Exception as e:
            print(f"[ERROR] При пересылке: {e}")

    print("\n" + "═" * 60)
    print("БОТ ЗАПУЩЕН В USER-РЕЖИМЕ")
    print("Пересылка только с 09:00 до 21:00 по Москве")
    print("Жду новых сообщений...")
    print("═" * 60 + "\n")

    await client.run_until_disconnected()

# Фейковый веб-сервер, чтобы Railway не убивал контейнер
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "bot is running", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Запуск бота в отдельном потоке + веб-сервер
# Фейковый веб-сервер + healthcheck для Railway
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "bot alive", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    def run_bot():
        asyncio.run(bot_main())

    threading.Thread(target=run_bot, daemon=True).start()

    print("Запускаем веб-сервер + healthcheck на порту 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

