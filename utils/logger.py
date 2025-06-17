# utils/logger.py

import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Настраивает и возвращает логгер с файловым хендлером.
    Логи будут писаться в файл bot.log в кодировке UTF-8.
    Формат: 2025-04-24 15:00:00 - INFO - Сообщение
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Если логгер уже настроен (есть хендлеры), не добавляем новые
    if not logger.handlers:
        # Файловый хендлер
        file_handler = logging.FileHandler("bot.log", encoding="utf-8")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Опционально: вывод в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
