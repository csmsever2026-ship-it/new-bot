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

# Клиент в user-режиме (user_session.session в репозитории)
client = TelegramClient("user_session", api_id, api_hash)

# Проверка времени 09:00
