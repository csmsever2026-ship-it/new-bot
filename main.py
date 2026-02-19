from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Твои данные из Railway Variables
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

# Список источников — @username через запятую
sources_str = os.getenv('@vedexx_news,@customs_rf,@oVEDinfo')          # например: "@kanal1,@kanal2,@kanal3"
sources_list = [s.strip() for s in sources_str.split(',') if s.strip()]sources_str = os.getenv('SOURCES')
if sources_str is None:
    print("ОШИБКА: переменная SOURCES не задана в Railway Variables!")
    exit(1)  # или просто continue, но лучше выйти
sources_list = [s.strip() for s in sources_str.split(',') if s.strip()]  # ← здесь был ';', но лучше ',' для @username

# Твой канал (куда пересылать)
target_str = os.getenv('@CLR_Group_manager')            # например: "@moy_kanal"

client = TelegramClient('session', api_id, api_hash)

async def main():
    await client.start()   # Если user mode — попросит номер и код один раз

    # Один раз разрешаем все @username (Telethon запомнит их)
    print("Загружаем каналы...")
    sources = []
    for src in sources_list:
        try:
            entity = await client.get_entity(src)   # '@username' → entity
            sources.append(entity)
            print(f"Успешно: {src} → {entity.title if hasattr(entity, 'title') else 'OK'}")
        except Exception as e:
            print(f"Ошибка с {src}: {e} — проверь, подписан ли ты на канал")

    try:
        target = await client.get_entity(target_str)
        print(f"Цель: {target_str} → {target.title if hasattr(target, 'title') else 'OK'}")
    except Exception as e:
        print(f"Ошибка с целью {target_str}: {e}")
        return

    # Теперь мониторим новые сообщения только из этих источников
    @client.on(events.NewMessage(chats=sources))
    async def handler(event):
        try:
            # Пересылаем без "переслано из" (если хочешь — удали .clear() и оставь просто forward_messages)
            msg = event.message
            msg.clear()  # ← это убирает "Forwarded from", если хочешь чистую копию
            await client.forward_messages(target, msg)
            print(f"Переслано из {event.chat.title or event.chat.username}")
        except Exception as e:
            print(f"Ошибка пересылки: {e}")

    print("Всё готово! Ждём новые посты...")
    await client.run_until_disconnected()

# Запускаем

asyncio.run(main())
