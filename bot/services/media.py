# bot/services/media.py

import os
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("zoo_totem_bot.media")

async def generate_image(
    image_path: str,
    animal_name: str,
    user_name: str
) -> str:
    """
    Открывает исходную картинку, рисует:
      – заголовок animal_name шрифтом Bold,
      – подпись user_name шрифтом Regular,
      – вставляет логотип.
    Сохраняет результат в media/generated/<user>_<animal>.png и возвращает путь.
    """
    # 1) Загрузка исходного изображения
    try:
        base = Image.open(image_path).convert("RGBA")
    except Exception:
        logger.exception(f"Не удалось открыть изображение {image_path}")
        raise

    draw = ImageDraw.Draw(base)
    margin = 20

    # 2) Пути к шрифтам
    fonts_dir       = "media/fonts"
    bold_path       = os.path.join(fonts_dir, "ALS_Story_2.0_B.otf")
    regular_path    = os.path.join(fonts_dir, "ALS_Story_2.0_R.otf")

    # 3) Загрузка шрифтов с fallback
    try:
        font_bold = ImageFont.truetype(bold_path, 48)
    except Exception:
        logger.warning(f"Не удалось загрузить шрифт {bold_path}, используем дефолт")
        font_bold = ImageFont.load_default()

    try:
        font_regular = ImageFont.truetype(regular_path, 36)
    except Exception:
        logger.warning(f"Не удалось загрузить шрифт {regular_path}, используем дефолт")
        font_regular = ImageFont.load_default()

    # 4) Рисуем заголовок (имя животного) в левом верхнем углу
    draw.text((margin, margin), animal_name, font=font_bold, fill="white")

    # 5) Рисуем подпись (имя пользователя) внизу слева
    caption = f"{user_name}, это ты!"
    text_width, text_height = draw.textsize(caption, font=font_regular)
    x = margin
    y = base.height - margin - text_height
    draw.text((x, y), caption, font=font_regular, fill="white")

    # 6) Вставляем логотип в правый нижний угол
    logo_path = "media/logo/MZoo-logo-circle-mono-black.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_width = base.width // 5
            logo = logo.resize(
                (logo_width, int(logo_width * logo.height / logo.width)),
                Image.ANTIALIAS
            )
            pos = (base.width - logo.width - margin, base.height - logo.height - margin)
            base.alpha_composite(logo, dest=pos)
        except Exception:
            logger.exception(f"Не удалось вставить логотип {logo_path}")
    else:
        logger.warning(f"Логотип не найден по пути {logo_path}")

    # 7) Сохранение итоговой картинки
    out_dir = "media/generated"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{user_name}_{animal_name}.png"
    output_path = os.path.join(out_dir, filename)
    try:
        base.save(output_path)
        logger.info(f"Сгенерирована картинка результата: {output_path}")
    except Exception:
        logger.exception(f"Не удалось сохранить изображение {output_path}")
        raise

    return output_path
