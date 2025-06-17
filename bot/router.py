# bot/router.py

from aiogram import Router
from bot.handlers import start, quiz, result, feedback, contact, sharing

# Создаём главный роутер
router = Router()

# Регистрируем в нём все модули-обработчики
router.include_router(start.router)
router.include_router(quiz.router)
router.include_router(result.router)
router.include_router(feedback.router)
router.include_router(contact.router)
router.include_router(sharing.router)
