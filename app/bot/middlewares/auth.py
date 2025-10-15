"""
Middleware для аутентификации и авторизации.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config.settings import settings
from app.services.user_service import UserService
from app.core.exceptions import AuthorizationError
from config.logging import security_logger

user_service = UserService()


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки аутентификации и авторизации."""

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

        # Получаем данные пользователя из контекста (установлены UserContextMiddleware)
        user_data = data.get('user_data')

        if not user_data:
            # Пользователь не найден в системе
            if isinstance(event, Message):
                await event.answer(
                    "Пользователь не найден. Начните с команды /start"
                )
            return

        # Проверяем, не заблокирован ли пользователь
        if user_data.get('is_banned', False):
            security_logger.warning(f"Blocked user {user.id} tried to access bot")

            if isinstance(event, Message):
                await event.answer(
                    "❌ Ваш аккаунт заблокирован. Обратитесь в поддержку."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Ваш аккаунт заблокирован.",
                    show_alert=True
                )
            return

        # Проверяем права администратора для admin handlers
        handler_name = handler.__name__
        if handler_name.startswith('admin_') or 'admin' in str(handler):
            if user.id not in settings.telegram.admin_ids:
                security_logger.warning(f"Non-admin user {user.id} tried to access admin function")

                if isinstance(event, Message):
                    await event.answer("❌ Недостаточно прав для выполнения этой команды.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Недостаточно прав.", show_alert=True)
                return

        # Добавляем флаг админа в контекст
        data['is_admin'] = user.id in settings.telegram.admin_ids

        return await handler(event, data)
