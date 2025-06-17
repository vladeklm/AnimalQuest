# bot/services/sharing.py

import logging
from aiogram import types

logger = logging.getLogger("zoo_totem_bot.sharing")

async def share_result(message: types.Message, totem_key: str, user_name: str):
    # безопасно получаем username бота
    bot_username = None
    if hasattr(message, "bot") and message.bot:
        bot_username = message.bot.username
    if not bot_username:
        bot_username = "ZooTotemBot"
    bot_mention = f"@{bot_username.lstrip('@')}"

    text = (
        f"🐾 Привет, {user_name}! Я прошёл викторину от Московского зоопарка "
        f"и узнал, что моё тотемное животное — *{totem_key}*!\n\n"
        f"Хочешь узнать, кто ты? → {bot_mention}\n\n"
        f"Пройди и ты 👉 {bot_mention}"
    )

    logger.info(f"share_result: user_id={message.from_user.id}, totem={totem_key}")
    await message.answer(text, parse_mode="Markdown")