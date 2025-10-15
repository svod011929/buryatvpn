"""
Middleware для ограничения частоты запросов.
"""

import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.core.security import rate_limiter
from config.logging import security_logger


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов."""

    def __init__(self, rate_limit: int = 30, window: int = 60):
        """
        Args:
            rate_limit: Максимальное количество запросов
            window: Временное окно в секундах
        """
        self.rate_limit = rate_limit
        self.window = window

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Определяем пользователя
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if not user:
            return await handler(event, data)

        # Создаем идентификатор для rate limiting
        identifier = f"user:{user.id}"

        # Проверяем лимит
        if rate_limiter.is_blocked(
            identifier, 
            max_attempts=self.rate_limit,
            window_minutes=self.window // 60
        ):
            security_logger.warning(f"Rate limit exceeded for user {user.id}")

            if isinstance(event, Message):
                await event.answer(
                    "⚠️ Слишком много запросов. Попробуйте позже.",
                    show_alert=True
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Слишком много запросов. Подождите немного.",
                    show_alert=True
                )
            return

        # Записываем успешную попытку
        rate_limiter.record_attempt(identifier, success=True)

        return await handler(event, data)
