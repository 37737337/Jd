import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

TOKEN = "fidas"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# антиспам (1 раз в минуту на чат)
last_used = {}
COOLDOWN = 60


# регистрация команды
async def set_commands():
    commands = [
        BotCommand(command="tag", description="Позвать администраторов"),
    ]
    await bot.set_my_commands(commands)


# автоудаление сообщений
async def delete_message_later(msg: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


@dp.message(Command("tag"))
async def tag_admins(message: Message, command: CommandObject):

    if message.chat.type not in ["group", "supergroup"]:
        return

    # ⏳ антиспам
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

    if not mentions:
        return

    chunk_size = 5

    for i in range(0, len(mentions), chunk_size):
        chunk = mentions[i:i + chunk_size]

        text = "📢 Вызов администраторов:\n\n"
        text += "\n".join(chunk)

        if custom_text:
            text += f"\n\n{custom_text}"

        sent_message = await message.answer(text, parse_mode="HTML")

        # автоудаление через 5 минут
        asyncio.create_task(delete_message_later(sent_message, 300))


async def main():
    await set_commands()
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
