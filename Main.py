import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("tagadmins"))
async def tag_admins(message: Message):

    if message.chat.type not in ["group", "supergroup"]:
        return

    admins = await bot.get_chat_administrators(message.chat.id)

    mentions = []

    for admin in admins:
        user = admin.user

        if user.is_bot:
            continue

        # Если есть username — используем его (самый надёжный способ)
        if user.username:
            mentions.append(f"@{user.username}")
        else:
            # Если нет username — пробуем через ID
            mentions.append(
                f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
            )

    if not mentions:
        await message.answer("Админы не найдены")
        return

    text = "📢 Админы, внимание!\n\n" + "\n".join(mentions)

    await message.answer(text, parse_mode="HTML")


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if name == "__main__":
    asyncio.run(main())
