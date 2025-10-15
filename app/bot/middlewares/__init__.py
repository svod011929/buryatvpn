"""
Middleware для Telegram бота.
"""

from aiogram import Dispatcher
from app.bot.middlewares.auth import AuthMiddleware
from app.bot.middlewares.logging import LoggingMiddleware
from app.bot.middlewares.rate_limit import RateLimitMiddleware
from app.bot.middlewares.user_context import UserContextMiddleware


def setup_middlewares(dp: Dispatcher):
    """Настройка всех middleware."""

    # Порядок важен! Middleware выполняются в порядке регистрации

    # Логирование (первым для записи всех событий)
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Rate limiting (проверка лимитов)
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    # Контекст пользователя (загрузка данных пользователя)
    dp.message.middleware(UserContextMiddleware())
    dp.callback_query.middleware(UserContextMiddleware())

    # Аутентификация (проверка доступа)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
