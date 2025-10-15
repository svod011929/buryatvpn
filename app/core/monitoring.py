"""
Мониторинг и метрики приложения.
"""

import time
import psutil
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.core import CollectorRegistry

from config.settings import settings
from config.logging import get_logger

logger = get_logger("monitoring")

# Создаем регистр метрик
registry = CollectorRegistry()

# Метрики запросов
request_count = Counter(
    'buryatvpn_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

request_duration = Histogram(
    'buryatvpn_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Метрики пользователей
user_count = Gauge(
    'buryatvpn_users_total',
    'Total number of users',
    registry=registry
)

active_subscriptions = Gauge(
    'buryatvpn_active_subscriptions',
    'Number of active subscriptions',
    registry=registry
)

# Метрики платежей
payment_count = Counter(
    'buryatvpn_payments_total',
    'Total number of payments',
    ['status', 'method'],
    registry=registry
)

revenue = Counter(
    'buryatvpn_revenue_total',
    'Total revenue',
    ['currency'],
    registry=registry
)

# Системные метрики
system_memory_usage = Gauge(
    'buryatvpn_memory_usage_bytes',
    'Memory usage in bytes',
    registry=registry
)

system_cpu_usage = Gauge(
    'buryatvpn_cpu_usage_percent',
    'CPU usage percentage',
    registry=registry
)

# Метрики базы данных
db_connections = Gauge(
    'buryatvpn_db_connections',
    'Number of database connections',
    registry=registry
)

db_query_duration = Histogram(
    'buryatvpn_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=registry
)


class HealthChecker:
    """Проверка состояния системы."""

    def __init__(self):
        self.last_check = None
        self.status = {}

    async def check_health(self) -> Dict[str, Any]:
        """Комплексная проверка состояния системы."""
        self.last_check = time.time()

        checks = {
            'database': await self._check_database(),
            'redis': await self._check_redis(),
            'disk_space': self._check_disk_space(),
            'memory': self._check_memory(),
            'cpu': self._check_cpu(),
        }

        # Общий статус
        overall_healthy = all(check.get('healthy', False) for check in checks.values())

        self.status = {
            'timestamp': self.last_check,
            'healthy': overall_healthy,
            'checks': checks,
            'version': settings.version,
        }

        return self.status

    async def _check_database(self) -> Dict[str, Any]:
        """Проверка соединения с базой данных."""
        try:
            from app.database.connection import get_db_session

            async with get_db_session() as session:
                await session.execute("SELECT 1")

            return {'healthy': True, 'message': 'Database connection OK'}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {'healthy': False, 'message': str(e)}

    async def _check_redis(self) -> Dict[str, Any]:
        """Проверка соединения с Redis."""
        try:
            from app.core.cache import cache

            await cache.set('health_check', 'ok', ttl=60)
            result = await cache.get('health_check')

            if result == 'ok':
                return {'healthy': True, 'message': 'Redis connection OK'}
            else:
                return {'healthy': False, 'message': 'Redis test failed'}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {'healthy': False, 'message': str(e)}

    def _check_disk_space(self) -> Dict[str, Any]:
        """Проверка свободного места на диске."""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100

            healthy = free_percent > 10  # Минимум 10% свободного места

            return {
                'healthy': healthy,
                'free_percent': round(free_percent, 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'total_gb': round(disk_usage.total / (1024**3), 2),
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {'healthy': False, 'message': str(e)}

    def _check_memory(self) -> Dict[str, Any]:
        """Проверка использования памяти."""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent

            healthy = used_percent < 90  # Максимум 90% использования

            # Обновляем метрику
            system_memory_usage.set(memory.used)

            return {
                'healthy': healthy,
                'used_percent': used_percent,
                'used_gb': round(memory.used / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2),
            }
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {'healthy': False, 'message': str(e)}

    def _check_cpu(self) -> Dict[str, Any]:
        """Проверка загрузки CPU."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            healthy = cpu_percent < 80  # Максимум 80% загрузки

            # Обновляем метрику
            system_cpu_usage.set(cpu_percent)

            return {
                'healthy': healthy,
                'usage_percent': cpu_percent,
                'cores': psutil.cpu_count(),
            }
        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return {'healthy': False, 'message': str(e)}


def setup_monitoring():
    """Настройка системы мониторинга."""
    logger.info("Setting up monitoring system")

    # Здесь можно добавить дополнительную настройку мониторинга
    # например, запуск фоновых задач сбора метрик

    logger.info("Monitoring system setup completed")


def get_metrics() -> str:
    """Получение метрик в формате Prometheus."""
    return generate_latest(registry)


# Глобальный экземпляр health checker
health_checker = HealthChecker()
