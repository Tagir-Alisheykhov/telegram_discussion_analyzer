import json
from pyrogram import Client
from pyrogram.types import Message
from collections import defaultdict

from settings import *

# Хранилище цепочек
threads = defaultdict(lambda: {"messages": [], "users": set(), "root_text": ""})


async def main():
    async with Client("session", api_id=API_ID, api_hash=API_HASH) as app:
        print("Подключение к Telegram")

        # Сбор сообщений за последние 7 дней
        async for message in app.get_chat_history(GROUP_ID):
            if not message.date:
                continue

            msg_date = message.date.astimezone(tz)
            if msg_date < seven_days_ago:
                break

            # Пропускаем сообщения без отправителя (например, системные)
            if not message.from_user:
                continue

            user_id = message.from_user.id

            # Определяем корневое сообщение цепочки
            if message.reply_to_message_id:
                root_id = message.reply_to_message_id
                # Убеждаемся, что для root_id есть запись (на случай, если корень ещё не обработан)
                if root_id not in threads:
                    # Попытаемся получить корневое сообщение (опционально, но лучше)
                    try:
                        root_msg = await app.get_messages(GROUP_ID, message_ids=root_id)
                        if root_msg and root_msg.text:
                            root_text = (root_msg.text or root_msg.caption or "")[:50].replace("\n", " ").strip()
                        else:
                            root_text = "[Неизвестная тема]"
                    except Exception:
                        root_text = "[Неизвестная тема]"
                    threads[root_id]["root_text"] = root_text
            else:
                root_id = message.id
                text = (message.text or message.caption or "")[:50].replace("\n", " ").strip()
                if not text:
                    text = "[Медиа или пустое сообщение]"
                threads[root_id]["root_text"] = text

            # Теперь безопасно добавляем
            threads[root_id]["messages"].append(message)
            threads[root_id]["users"].add(user_id)

        # Формирование отчета по дням
        days_dict = defaultdict(list)

        for root_id, data in threads.items():
            if len(data["messages"]) < 2:
                continue  # Пропуск одиночных сообщений

            # Дата первого сообщения в цепочке определяет день
            first_msg = min(data["messages"], key=lambda m: m.date)
            first_date_tz = first_msg.date.astimezone(tz)
            date_key = first_date_tz.strftime("%Y-%m-%d")

            thread_info = {
                "topic": data["root_text"],
                "messages": len(data["messages"]),
                "users": len(data["users"])
            }
            days_dict[date_key].append(thread_info)

        # Сортировка дней по возрастанию
        sorted_days = []
        current = seven_days_ago.date()
        for i in range(7):
            day_str = (current + timedelta(days=i)).strftime("%Y-%m-%d")
            if day_str in days_dict:
                sorted_days.append({
                    "date": day_str,
                    "threads": days_dict[day_str]
                })
            else:
                pass

        # Формирование финального Json-файла
        report = {
            "timezone": TIMEZONE,
            "days": sorted_days
        }

        # Сохранение в файл
        with open("data/report.json", "w", encoding="UTF-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

        print("Отчет сохранен в data/report.json")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



