# bot/handlers/result.py

import os
import json
import logging
from typing import Optional

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.media import generate_image
from bot.services.scoring import calculate_scores, get_top_animal

router = Router()
logger = logging.getLogger("zoo_totem_bot.result")

# Загружаем справочник животных один раз
ANIMALS_PATH = os.path.join("./../data", "animals.json")
with open(ANIMALS_PATH, encoding="utf-8") as f:
    ANIMALS = json.load(f)


async def show_result(message: types.Message, state: FSMContext):
    """
    Формирует и отправляет итоговый результат:
    1) Считывает answers из FSM
    2) Вычисляет очки через scoring
    3) Определяет топ-животное
    4) Генерирует картинку (media)
    5) Отправляет пользователю фото/текст + кнопки
    6) Сброс FSM
    """
    data = await state.get_data()
    answers = data.get("answers", [])

    # 1) Подсчёт очков
    scores = calculate_scores(answers)
    top = get_top_animal(scores)
    if top is None:
        await message.answer("⚠️ Не удалось определить ваш тотем. Попробуйте ещё раз.")
        await state.clear()
        return

    totem_key, totem_score = top
    animal = ANIMALS.get(totem_key)
    if not animal:
        logger.error(f"Totem key '{totem_key}' отсутствует в animals.json")
        await message.answer("⚠️ Произошла ошибка при определении тотема.")
        await state.clear()
        return

    logger.info(f"Пользователь {message.from_user.id} — тотем: {animal['name']} ({totem_score} очков)")

    # 2) Генерация картинки
    image_path: Optional[str]
    try:
        image_path = await generate_image(
            image_path=animal["image"],
            animal_name=animal["name"],
            user_name=message.from_user.first_name
        )
    except Exception:
        logger.exception("Ошибка при генерации итоговой картинки")
        image_path = None

    # 3) Формирование подписи
    caption = (
        f"🎉 *Твоё тотемное животное — {animal['name']}!*\n\n"
        f"_{animal['description']}_\n\n"
        f"[Узнать об опеке]({animal['guardian_link']})"
    )

    # 4) Inline-кнопки
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Ещё раз", callback_data="start_quiz")],
        [InlineKeyboardButton(text="📢 Поделиться", callback_data=f"share_{totem_key}")],
        [InlineKeyboardButton(text="💬 Отзыв", callback_data="feedback")],
        [InlineKeyboardButton(text="📞 Связаться", callback_data=f"contact_{totem_key}")]
    ])

    # 5) Отправка результата
    if image_path:
        await message.answer_photo(
            photo=types.FSInputFile(image_path),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=kb
        )
    else:
        await message.answer(caption, parse_mode="Markdown", reply_markup=kb)

    # 6) Сброс состояния
    await state.clear()
