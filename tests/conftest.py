"""
Конфигурация pytest.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
from app.database.connection import init_database, close_database
from app.core.cache import cache
from config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Настройка тестовой базы данных."""
    # Используем отдельную БД для тестов
    settings.database.url = "sqlite:///test_database.db"

    await init_database()
    yield
    await close_database()


@pytest.fixture(scope="session")
async def setup_cache():
    """Настройка тестового кэша."""
    # Используем отдельную БД Redis для тестов
    settings.redis.url = "redis://localhost:6379/15"

    await cache.connect()
    yield cache
    await cache.disconnect()


@pytest.fixture
async def mock_user_data():
    """Мок данных пользователя для тестов."""
    return {
        'id': 1,
        'telegram_id': 123456789,
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True,
        'is_banned': False,
        'trial_used': False,
        'referral_code': 'TESTCODE'
    }


@pytest.fixture
def mock_bot():
    """Мок Telegram бота."""
    bot = AsyncMock()
    bot.get_me.return_value = AsyncMock(username='testbot')
    return bot
