import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import start
from src.bot.handlers import company
from src.middlewares import helper_attributes_middleware
from src.config import settings

logging.basicConfig(level=logging.INFO)

API_TOKEN = settings.TELEGRAM_BOT_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start.router)
dp.include_router(company.router)
dp.message.middleware(helper_attributes_middleware)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("Bot is Starting")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
