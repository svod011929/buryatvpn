"""
Система кэширования на основе Redis.
"""

import json
import pickle
from typing import Any, Optional, Union
import aioredis
from config.settings import settings
from config.logging import get_logger

logger = get_logger("cache")


class CacheManager:
    """Менеджер кэширования."""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.connected = False

    async def connect(self):
        """Подключение к Redis."""
        try:
            self.redis = aioredis.from_url(
                settings.redis.url,
                max_connections=settings.redis.max_connections,
                decode_responses=True
            )

            # Проверка соединения
            await self.redis.ping()
            self.connected = True
            logger.info("Connected to Redis")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            raise

    async def disconnect(self):
        """Отключение от Redis."""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Disconnected from Redis")

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Сохранение значения в кэш."""
        if not self.connected:
            logger.warning("Redis not connected, skipping cache set")
            return False

        try:
            if serialize:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                elif not isinstance(value, str):
                    value = pickle.dumps(value)

            ttl = ttl or settings.redis.ttl
            await self.redis.setex(key, ttl, value)
            return True

        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    async def get(self, key: str, deserialize: bool = True) -> Any:
        """Получение значения из кэша."""
        if not self.connected:
            logger.warning("Redis not connected, skipping cache get")
            return None

        try:
            value = await self.redis.get(key)
            if value is None:
                return None

            if deserialize:
                # Пытаемся десериализовать JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Если не JSON, пытаемся pickle
                    try:
                        return pickle.loads(value.encode() if isinstance(value, str) else value)
                    except (pickle.PickleError, TypeError):
                        # Возвращаем как есть
                        return value

            return value

        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Удаление ключа из кэша."""
        if not self.connected:
            return False

        try:
            deleted = await self.redis.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа."""
        if not self.connected:
            return False

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Очистка ключей по шаблону."""
        if not self.connected:
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Инкремент значения."""
        if not self.connected:
            return 0

        try:
            value = await self.redis.incrby(key, amount)
            if ttl:
                await self.redis.expire(key, ttl)
            return value
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {e}")
            return 0

    def cache_key(self, *args) -> str:
        """Генерация ключа кэша."""
        return ":".join(str(arg) for arg in args)


# Глобальный экземпляр кэша
cache = CacheManager()


def cached(ttl: int = None, key_prefix: str = ""):
    """Декоратор для кэширования результатов функций."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Пытаемся получить из кэша
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Выполняем функцию и кэшируем результат
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator
