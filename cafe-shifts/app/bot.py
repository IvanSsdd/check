
import asyncio
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from .db import Base, engine, SessionLocal
from .service import arrive, leave



BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пришёл"),
            KeyboardButton(text="Ушёл")
        ]
    ],
    resize_keyboard=True
)


async def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            f"BOT_TOKEN не найден. Проверь файл: {ENV_FILE}"
        )

    Base.metadata.create_all(engine)

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message):
        await message.answer(
            "Отметка смен кафе. Выберите действие:",
            reply_markup=keyboard
        )

    @dp.message(F.text.in_({"Пришёл", "Ушёл"}))
    async def mark(message: Message):
        with SessionLocal() as db:
            _, answer = (
                arrive if message.text == "Пришёл" else leave
            )(db, message.from_user.id)

        await message.answer(answer)

    @dp.message()
    async def help_message(message: Message):
        await message.answer(
            "Используйте кнопки «Пришёл» и «Ушёл».",
            reply_markup=keyboard
        )

    try:
        print("Бот запускается...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
