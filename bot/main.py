# bot/main.py

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.router import router
from utils.logger import setup_logger

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Пропишите BOT_TOKEN в файле .env")

# Настраиваем логгер
logger = setup_logger("zoo_totem_bot")

async def main():
    # Инициализируем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    try:
        logger.info("🚀 Запуск ZooTotemBot…")
        # Запускаем polling — бот будет опрашивать Telegram
        await dp.start_polling(bot)
    finally:
        # При остановке закроем бот (и HTTP-сессию внутри него)
        await bot.session.close()
        logger.info("🛑 Бот остановлен")

if __name__ == "__main__":
    # Запускаем главный корутин
    asyncio.run(main())
