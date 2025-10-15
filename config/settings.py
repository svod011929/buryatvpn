"""
Настройки приложения BuryatVPN.

Все конфигурационные параметры загружаются из переменных окружения
с использованием pydantic-settings для валидации и типизации.
"""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""

    url: str = Field(default="sqlite:///data/database.db", alias="DATABASE_URL")
    echo: bool = Field(default=False, alias="DATABASE_ECHO")
    pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="DATABASE_MAX_OVERFLOW")


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    ttl: int = Field(default=3600, alias="REDIS_TTL")
    max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")


class TelegramSettings(BaseSettings):
    """Настройки Telegram бота."""

    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_ids: List[int] = Field(default=[], alias="ADMIN_IDS")
    webhook_url: Optional[str] = Field(default=None, alias="TELEGRAM_WEBHOOK_URL")
    webhook_secret: Optional[str] = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")

    @validator("admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(id.strip()) for id in v.split(",") if id.strip()]
        return v


class SecuritySettings(BaseSettings):
    """Настройки безопасности."""

    secret_key: str = Field(..., alias="SECRET_KEY")
    encryption_key: str = Field(..., alias="ENCRYPTION_KEY")
    jwt_secret: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_hours: int = Field(default=24, alias="JWT_EXPIRE_HOURS")

    @validator("encryption_key")
    def validate_encryption_key(cls, v):
        try:
            Fernet(v.encode())
            return v
        except Exception:
            raise ValueError("Invalid encryption key format")

    def get_fernet(self) -> Fernet:
        """Получить объект Fernet для шифрования."""
        return Fernet(self.encryption_key.encode())


class WebSettings(BaseSettings):
    """Настройки веб-сервера."""

    host: str = Field(default="0.0.0.0", alias="WEB_HOST")
    port: int = Field(default=8000, alias="WEB_PORT")
    debug: bool = Field(default=False, alias="WEB_DEBUG")
    admin_email: str = Field(..., alias="WEB_ADMIN_EMAIL")
    admin_password_hash: str = Field(..., alias="WEB_ADMIN_PASSWORD_HASH")


class PaymentSettings(BaseSettings):
    """Настройки платежных систем."""

    # YooKassa
    yookassa_shop_id: Optional[str] = Field(default=None, alias="YOOKASSA_SHOP_ID")
    yookassa_api_key: Optional[str] = Field(default=None, alias="YOOKASSA_API_KEY")
    yookassa_webhook_secret: Optional[str] = Field(default=None, alias="YOOKASSA_WEBHOOK_SECRET")

    # CryptoPay
    cryptopay_token: Optional[str] = Field(default=None, alias="CRYPTOPAY_API_TOKEN")
    cryptopay_webhook_secret: Optional[str] = Field(default=None, alias="CRYPTOPAY_WEBHOOK_SECRET")


class XUISettings(BaseSettings):
    """Настройки X-UI панели."""

    ssl_verify: bool = Field(default=True, alias="XUI_SSL_VERIFY")
    timeout: int = Field(default=30, alias="XUI_TIMEOUT")
    retry_attempts: int = Field(default=3, alias="XUI_RETRY_ATTEMPTS")


class LoggingSettings(BaseSettings):
    """Настройки логирования."""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    file: str = Field(default="logs/app.log", alias="LOG_FILE")
    max_size: int = Field(default=10485760, alias="LOG_MAX_SIZE")  # 10MB
    backup_count: int = Field(default=10, alias="LOG_BACKUP_COUNT")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        alias="LOG_FORMAT"
    )


class MonitoringSettings(BaseSettings):
    """Настройки мониторинга."""

    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    health_check_interval: int = Field(default=60, alias="HEALTH_CHECK_INTERVAL")


class Settings(BaseSettings):
    """Главный класс настроек приложения."""

    # Общие настройки
    app_name: str = Field(default="BuryatVPN", alias="APP_NAME")
    version: str = Field(default="2.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    testing: bool = Field(default=False, alias="TESTING")

    # Поднастройки
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    telegram: TelegramSettings = TelegramSettings()
    security: SecuritySettings = SecuritySettings()
    web: WebSettings = WebSettings()
    payments: PaymentSettings = PaymentSettings()
    xui: XUISettings = XUISettings()
    logging: LoggingSettings = LoggingSettings()
    monitoring: MonitoringSettings = MonitoringSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()
