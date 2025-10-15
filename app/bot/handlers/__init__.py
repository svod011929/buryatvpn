"""
Инициализация обработчиков бота.
"""

from aiogram import Dispatcher
from app.bot.handlers import commands, user, admin, payments, errors


def setup_handlers(dp: Dispatcher):
    """Настройка всех обработчиков."""

    # Порядок важен! Более специфичные обработчики должны быть первыми

    # Обработчики команд
    commands.setup_handlers(dp)

    # Пользовательские обработчики
    user.setup_handlers(dp)

    # Административные обработчики
    admin.setup_handlers(dp)

    # Обработчики платежей
    payments.setup_handlers(dp)

    # Обработчик ошибок (должен быть последним)
    errors.setup_handlers(dp)
