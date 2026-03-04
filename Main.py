import asyncio
import logging
import time
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand, ChatMemberUpdated
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# 🔒 Разрешённые группы
ALLOWED_CHATS = {
    -1003717142350,
    -1003022066500,
}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ⏳ Антиспам
user_last_used = {}
group_last_used = {}

USER_COOLDOWN = 300   # 5 минут
GROUP_COOLDOWN = 60   # 1 минута

# ⏰ Время работы
WORK_START = 7
WORK_END = 23


async def set_commands():
    commands = [
        BotCommand(command="tag", description="Позвать администраторов"),
    ]
    await bot.set_my_commands(commands)


async def delete_message_later(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


# 🔥 Выход из чужих групп
@dp.my_chat_member()
async def check_group(event: ChatMemberUpdated):
    if event.chat.type in ["group", "supergroup"]:
        if event.chat.id not in ALLOWED_CHATS:
            await bot.leave_chat(event.chat.id)


@dp.message(Command("tag"))
async def tag_admins(message: Message, command: CommandObject):

    if message.chat.type not in ["group", "supergroup"]:
        return

    if message.chat.id not in ALLOWED_CHATS:
        return

    # ⏰ Проверка времени
    current_hour = datetime.now().hour
    if not (WORK_START <= current_hour < WORK_END):
        await message.answer("🌙 Команда работает только с 07:00 до 23:00.")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    # КД группы
    if chat_id in group_last_used:
        elapsed_group = current_time - group_last_used[chat_id]
        if elapsed_group < GROUP_COOLDOWN:
            remaining = int(GROUP_COOLDOWN - elapsed_group)
            await message.answer(
                f"⏳ В группе можно использовать команду через {remaining} сек."
            )
            return

    # КД пользователя
    if user_id in user_last_used:
        elapsed_user = current_time - user_last_used[user_id]
        if elapsed_user < USER_COOLDOWN:
            remaining = int(USER_COOLDOWN - elapsed_user)
            await message.answer(
                f"⏳ Вы сможете использовать команду через {remaining} сек."
            )
            return

    group_last_used[chat_id] = current_time
    user_last_used[user_id] = current_time

    custom_text = command.args if command.args else ""

    admins = await bot.get_chat_administrators(chat_id)

    mentions = []

    for admin in admins:
        user = admin.user
        if user.is_bot:
            continue

        if user.username:
            mentions.append(f"@{user.username}")
        else:
            mentions.append(
                f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
            )

    chunk_size = 5

    for i in range(0, len(mentions), chunk_size):
        chunk = mentions[i:i + chunk_size]

        text = "📢 Вызов администраторов:\n\n"
        text += "\n".join(chunk)

        if custom_text:
            text += f"\n\n{custom_text}"

        sent_message = await message.answer(text, parse_mode="HTML")

        asyncio.create_task(delete_message_later(sent_message, 300))


async def main():
    await set_commands()
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
