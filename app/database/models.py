"""
Модели базы данных для BuryatVPN.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Numeric, BigInteger, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)

    # Статус пользователя
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    trial_used = Column(Boolean, default=False, nullable=False)

    # Реферальная система
    referral_code = Column(String(50), unique=True, nullable=True, index=True)
    referred_by = Column(String(50), nullable=True)
    referral_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Server(Base):
    """Модель VPN сервера."""

    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)

    # X-UI настройки
    xui_url = Column(String(500), nullable=False)
    xui_username = Column(String(255), nullable=False)
    xui_password = Column(Text, nullable=False)  # Зашифрованный пароль
    xui_secret_path = Column(String(255), nullable=False)

    # Inbound настройки
    inbound_id = Column(Integer, default=1, nullable=False)
    inbound_id_trial = Column(Integer, default=2, nullable=False)

    # Статус и лимиты
    is_active = Column(Boolean, default=True, nullable=False)
    max_users = Column(Integer, default=1000, nullable=False)
    current_users = Column(Integer, default=0, nullable=False)

    # Геолокация
    country_code = Column(String(10), nullable=True)
    city = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_health_check = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tariffs = relationship("Tariff", back_populates="server", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="server")

    @validates('port')
    def validate_port(self, key, port):
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return port

    def __repr__(self):
        return f"<Server(id={self.id}, name='{self.name}', host='{self.host}')>"


class Tariff(Base):
    """Модель тарифного плана."""

    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Стоимость и период
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="RUB", nullable=False)
    duration_days = Column(Integer, nullable=False)

    # Лимиты
    speed_limit = Column(Integer, nullable=True)  # Mbit/s
    traffic_limit = Column(BigInteger, nullable=True)  # bytes

    # Привязка к серверу
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)

    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    server = relationship("Server", back_populates="tariffs")
    subscriptions = relationship("Subscription", back_populates="tariff")

    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    @validates('duration_days')
    def validate_duration(self, key, duration):
        if duration <= 0:
            raise ValueError("Duration must be positive")
        return duration

    def __repr__(self):
        return f"<Tariff(id={self.id}, name='{self.name}', price={self.price})>"


class Subscription(Base):
    """Модель подписки пользователя."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), nullable=False)

    # Период подписки
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)

    # VPN конфигурация
    vless_config = Column(Text, nullable=True)
    client_id = Column(String(255), nullable=True)  # UUID клиента в X-UI

    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)

    # Статистика трафика
    traffic_used = Column(BigInteger, default=0, nullable=False)
    last_traffic_update = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    server = relationship("Server", back_populates="subscriptions")
    tariff = relationship("Tariff", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"


class Payment(Base):
    """Модель платежа."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    # Платежная информация
    external_id = Column(String(255), nullable=True, index=True)  # ID во внешней системе
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="RUB", nullable=False)

    # Метод платежа
    payment_method = Column(String(50), nullable=False)  # yookassa, cryptopay, code
    payment_system = Column(String(100), nullable=True)  # конкретная система

    # Статус
    status = Column(String(50), default="pending", nullable=False)  # pending, paid, failed, refunded

    # Метаданные
    metadata = Column(Text, nullable=True)  # JSON с дополнительной информацией

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>"


class PromoCode(Base):
    """Модель промокода."""

    __tablename__ = "promocodes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)

    # Скидка
    discount_percent = Column(Integer, nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=True)

    # Лимиты использования
    usage_limit = Column(Integer, nullable=True)  # None = без ограничений
    usage_count = Column(Integer, default=0, nullable=False)

    # Период действия
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Статус
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @validates('discount_percent')
    def validate_discount_percent(self, key, percent):
        if not 0 <= percent <= 100:
            raise ValueError("Discount percent must be between 0 and 100")
        return percent

    def __repr__(self):
        return f"<PromoCode(id={self.id}, code='{self.code}', discount={self.discount_percent}%)>"


class BotMessage(Base):
    """Модель сообщений бота."""

    __tablename__ = "bot_messages"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)

    # Контент сообщения
    text = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=True)

    # Настройки
    is_active = Column(Boolean, default=True, nullable=False)
    parse_mode = Column(String(20), default="HTML", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<BotMessage(id={self.id}, key='{self.key}')>"


class UserActivity(Base):
    """Модель активности пользователей для аналитики."""

    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Тип активности
    activity_type = Column(String(50), nullable=False, index=True)
    activity_data = Column(Text, nullable=True)  # JSON с деталями

    # Метаданные
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"


# Индексы для оптимизации запросов
Index('idx_users_telegram_id_active', User.telegram_id, User.is_active)
Index('idx_subscriptions_user_active', Subscription.user_id, Subscription.is_active)
Index('idx_subscriptions_end_date', Subscription.end_date)
Index('idx_payments_status_created', Payment.status, Payment.created_at)
Index('idx_user_activity_type_created', UserActivity.activity_type, UserActivity.created_at)
