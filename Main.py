import asyncio
import logging
import time
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand, ChatMemberUpdated
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

TOKEN = os.getenv("8211838214:AAHmfcsxfbpaUOb32dnTB_JPysI8MoLz-Ko")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# 🔒 Разрешённые группы
ALLOWED_CHATS = {
    -1001234567890,  # вставь свой ID
}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

last_used = {}
COOLDOWN = 60


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

    current_time = time.time()

    if message.chat.id in last_used:
        elapsed = current_time - last_used[message.chat.id]
        if elapsed < COOLDOWN:
            remaining = int(COOLDOWN - elapsed)
            await message.answer(
                f"⏳ Команду можно использовать через {remaining} сек."
            )
            return

    last_used[message.chat.id] = current_time

    custom_text = command.args if command.args else ""

    admins = await bot.get_chat_administrators(message.chat.id)

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
