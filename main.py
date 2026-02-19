# Этот файл запускается на Railway и пересылает новые посты из указанных каналов в твой канал

import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

# Загружаем переменные из Railway (они задаются в разделе Variables)
load_dotenv()

# ────────────────────────────────────────────────
#          ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ (в Railway → Variables)
# ────────────────────────────────────────────────
# API_ID          →  твои цифры из my.telegram.org
# API_HASH        →  длинная строка из my.telegram.org
# SOURCES         →  @kanal1,@kanal2,@kanal3   (через запятую, без пробелов!)
# TARGET          →  @твой_канал               (куда пересылать)
# BOT_TOKEN       →  (необязательно) токен от @BotFather, если хочешь использовать бота вместо личного аккаунта
# ────────────────────────────────────────────────

api_id = os.getenv("33887345")
api_hash = os.getenv("27278fe9e005b6a7c4f77c42bef3ea08")
bot_token = os.getenv("8332360026:AAENXiUqg515om9pTqLfqu1sDA4VScrWh_g")          # если используешь бота — укажи, иначе оставь пустым
sources_str = os.getenv("@vedexx_news,@customs_rf,@oVEDinfo")
target_str = os.getenv("@clr_group_expert")

# Проверяем, что всё заполнено
if not api_id or not api_hash:
    print("ОШИБКА: API_ID и API_HASH не заданы в Variables!")
    exit(1)

if not sources_str:
    print("ОШИБКА: SOURCES не задан! Пример: @news,@tech,@sport")
    exit(1)

if not target_str:
    print("ОШИБКА: TARGET не задан! Пример: @moy_kanal")
    exit(1)

# Разбиваем SOURCES на список
sources_list = [s.strip() for s in sources_str.split(",") if s.strip()]

# Создаём клиента
# Если есть BOT_TOKEN — используем бота, иначе — userbot (личный аккаунт)
if bot_token:
    client = TelegramClient("bot_session", int(api_id), api_hash).start(bot_token=bot_token)
    print("Запущен в режиме БОТА")
else:
    client = TelegramClient("user_session", int(api_id), api_hash)
    print("Запущен в режиме USER (личный аккаунт)")

async def main():
    await client.start()

    # Если userbot — может попросить номер телефона и код (один раз)
    # Если нужно два фактора — введи пароль в логи Railway

    print("\nЗагружаем каналы...")

    # Список реальных сущностей (entities) источников
    sources_entities = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)
            sources_entities.append(entity)
            title = entity.title if hasattr(entity, "title") else entity.username
            print(f"Успешно подключён источник: {src} → {title or 'OK'}")
        except Exception as e:
            print(f"Ошибка с источником {src}: {e}")
            print("Возможные причины: канал приватный, не подписан, опечатка в @username")

    # Целевой канал
    try:
        target = await client.get_entity(target_str)
        title = target.title if hasattr(target, "title") else target.username
        print(f"Целевой канал: {target_str} → {title or 'OK'}")
    except Exception as e:
        print(f"Ошибка с целевым каналом {target_str}: {e}")
        print("Проверь: бот/аккаунт — админ в канале с правом постить")
        return

    # Сам обработчик новых сообщений
    @client.on(events.NewMessage(chats=sources_entities))
    async def handler(event):
        try:
            msg = event.message

            # Убираем надпись "Переслано из ..." (если хочешь оставить — закомментируй эту строку)
            msg.clear_forward()

            # Пересылаем сообщение
            await client.forward_messages(target, msg)
            print(f"Переслано сообщение из {event.chat.title or event.chat.username}")

        except Exception as e:
            print(f"Ошибка при пересылке: {e}")

    print("\n" + "="*50)
    print("Всё готово! Ожидаю новые посты...")
    print("Для теста опубликуй что-нибудь в одном из источников")
    print("="*50 + "\n")

    # Держим скрипт запущенным
    await client.run_until_disconnected()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
