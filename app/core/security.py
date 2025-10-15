"""
Утилиты для обеспечения безопасности.
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from config.settings import settings
from config.logging import security_logger
from app.core.exceptions import AuthenticationError


# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Менеджер безопасности для управления шифрованием и аутентификацией."""

    def __init__(self):
        self.fernet = settings.security.get_fernet()

    def hash_password(self, password: str) -> str:
        """Хеширование пароля."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля."""
        return pwd_context.verify(plain_password, hashed_password)

    def encrypt_data(self, data: str) -> str:
        """Шифрование данных."""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровка данных."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def generate_token(self, length: int = 32) -> str:
        """Генерация случайного токена."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_referral_code(self, length: int = 8) -> str:
        """Генерация реферального кода."""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.security.jwt_expire_hours)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.security.jwt_secret,
            algorithm=settings.security.jwt_algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Проверка JWT токена."""
        try:
            payload = jwt.decode(
                token,
                settings.security.jwt_secret,
                algorithms=[settings.security.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {e}")

    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """Хеширование чувствительных данных с солью."""
        if salt is None:
            salt = secrets.token_hex(16)

        hash_obj = hashlib.sha256()
        hash_obj.update((data + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"

    def verify_hash(self, data: str, hashed_data: str) -> bool:
        """Проверка хеша."""
        try:
            salt, hash_value = hashed_data.split(":", 1)
            return self.hash_sensitive_data(data, salt) == hashed_data
        except ValueError:
            return False


class RateLimiter:
    """Ограничитель частоты запросов."""

    def __init__(self):
        self.attempts = {}
        self.blocked_ips = {}

    def is_blocked(self, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Проверка блокировки по идентификатору."""
        now = datetime.utcnow()

        # Очистка старых записей
        cutoff = now - timedelta(minutes=window_minutes)
        self.attempts = {
            k: v for k, v in self.attempts.items()
            if v['last_attempt'] > cutoff
        }

        # Проверка количества попыток
        if identifier in self.attempts:
            attempts_data = self.attempts[identifier]
            if attempts_data['count'] >= max_attempts:
                security_logger.warning(f"Rate limit exceeded for {identifier}")
                return True

        return False

    def record_attempt(self, identifier: str, success: bool = False):
        """Запись попытки."""
        now = datetime.utcnow()

        if success:
            # Успешная попытка - сбрасываем счетчик
            if identifier in self.attempts:
                del self.attempts[identifier]
        else:
            # Неуспешная попытка - увеличиваем счетчик
            if identifier in self.attempts:
                self.attempts[identifier]['count'] += 1
                self.attempts[identifier]['last_attempt'] = now
            else:
                self.attempts[identifier] = {
                    'count': 1,
                    'last_attempt': now
                }

            security_logger.warning(f"Failed attempt recorded for {identifier}")


# Глобальные экземпляры
security_manager = SecurityManager()
rate_limiter = RateLimiter()
