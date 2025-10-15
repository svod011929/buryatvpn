"""
Настройка логирования для приложения BuryatVPN.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """Настройка системы логирования."""

    # Удаляем стандартный обработчик loguru
    logger.remove()

    # Создаем директорию для логов
    log_dir = Path(settings.logging.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Консольный вывод
    logger.add(
        sys.stdout,
        level=settings.logging.level,
        format=settings.logging.format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Файловый вывод с ротацией
    logger.add(
        settings.logging.file,
        level=settings.logging.level,
        format=settings.logging.format,
        rotation=settings.logging.max_size,
        retention=settings.logging.backup_count,
        compression="gz",
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Потокобезопасность
    )

    # Отдельный файл для ошибок
    error_log_file = settings.logging.file.replace('.log', '_errors.log')
    logger.add(
        error_log_file,
        level="ERROR",
        format=settings.logging.format,
        rotation=settings.logging.max_size,
        retention=settings.logging.backup_count,
        compression="gz",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # Логирование безопасности
    security_log_file = settings.logging.file.replace('.log', '_security.log')
    security_logger = logger.bind(security=True)
    logger.add(
        security_log_file,
        level="INFO",
        format=settings.logging.format,
        rotation=settings.logging.max_size,
        retention=settings.logging.backup_count,
        compression="gz",
        filter=lambda record: record["extra"].get("security", False),
        enqueue=True,
    )

    logger.info(f"Logging configured for {settings.app_name} v{settings.version}")
    return logger


# Создаем логгеры для разных компонентов
def get_logger(name: str):
    """Получить логгер для конкретного компонента."""
    return logger.bind(component=name)


# Специальные логгеры
bot_logger = get_logger("bot")
api_logger = get_logger("api")
db_logger = get_logger("database")
security_logger = logger.bind(security=True)
