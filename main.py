import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers.tasks import router


async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("Бот запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())