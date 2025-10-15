"""
Кастомные исключения для приложения BuryatVPN.
"""


class BuryatVPNException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DatabaseError(BuryatVPNException):
    """Ошибки работы с базой данных."""
    pass


class ValidationError(BuryatVPNException):
    """Ошибки валидации данных."""
    pass


class AuthenticationError(BuryatVPNException):
    """Ошибки аутентификации."""
    pass


class AuthorizationError(BuryatVPNException):
    """Ошибки авторизации."""
    pass


class PaymentError(BuryatVPNException):
    """Ошибки обработки платежей."""
    pass


class VPNServerError(BuryatVPNException):
    """Ошибки работы с VPN сервером."""
    pass


class UserNotFoundError(BuryatVPNException):
    """Пользователь не найден."""
    pass


class SubscriptionError(BuryatVPNException):
    """Ошибки работы с подписками."""
    pass


class ConfigurationError(BuryatVPNException):
    """Ошибки конфигурации."""
    pass


class ExternalServiceError(BuryatVPNException):
    """Ошибки внешних сервисов."""
    pass
