"""
Главный модуль запуска приложения BuryatVPN.
"""

import asyncio
import signal
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging import setup_logging
from config.settings import settings
from app.database.connection import init_database
from app.bot.main import start_bot
from app.api.main import start_web_server
from app.core.monitoring import setup_monitoring

# Настройка логирования
logger = setup_logging()


class Application:
    """Основной класс приложения."""

    def __init__(self):
        self.bot_task = None
        self.web_task = None
        self.running = False

    async def startup(self):
        """Запуск всех компонентов приложения."""
        logger.info(f"Starting {settings.app_name} v{settings.version}")

        try:
            # Инициализация базы данных
            await init_database()
            logger.info("Database initialized")

            # Настройка мониторинга
            if settings.monitoring.metrics_enabled:
                setup_monitoring()
                logger.info("Monitoring setup completed")

            # Запуск бота и веб-сервера
            self.bot_task = asyncio.create_task(start_bot())
            self.web_task = asyncio.create_task(start_web_server())

            self.running = True
            logger.info("All services started successfully")

            # Ожидание завершения задач
            await asyncio.gather(self.bot_task, self.web_task)

        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            await self.shutdown()
            raise

    async def shutdown(self):
        """Корректное завершение работы приложения."""
        if not self.running:
            return

        logger.info("Shutting down application...")
        self.running = False

        # Отмена задач
        if self.bot_task and not self.bot_task.done():
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                pass

        if self.web_task and not self.web_task.done():
            self.web_task.cancel()
            try:
                await self.web_task
            except asyncio.CancelledError:
                pass

        logger.info("Application shutdown completed")


async def main():
    """Главная функция приложения."""
    app = Application()

    # Обработка сигналов завершения
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(app.shutdown())

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        await app.startup()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
