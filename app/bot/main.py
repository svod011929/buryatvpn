"""
Главный модуль Telegram бота.
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import aioredis

from config.settings import settings
from config.logging import bot_logger
from app.core.cache import cache
from app.bot.handlers import setup_handlers
from app.bot.middlewares import setup_middlewares
from app.core.exceptions import ConfigurationError


class TelegramBot:
    """Класс для управления Telegram ботом."""

    def __init__(self):
        self.bot: Bot = None
        self.dp: Dispatcher = None
        self.storage: RedisStorage = None
        self.app: web.Application = None

    async def setup(self):
        """Настройка бота."""
        try:
            # Создание бота
            self.bot = Bot(token=settings.telegram.bot_token)

            # Настройка Redis storage для FSM
            redis = aioredis.from_url(settings.redis.url)
            self.storage = RedisStorage(redis)

            # Создание диспетчера
            self.dp = Dispatcher(storage=self.storage)

            # Настройка middleware
            setup_middlewares(self.dp)

            # Настройка обработчиков
            setup_handlers(self.dp)

            # Подключение к кэшу
            await cache.connect()

            bot_logger.info("Telegram bot setup completed")

        except Exception as e:
            bot_logger.error(f"Failed to setup bot: {e}")
            raise ConfigurationError(f"Bot setup failed: {e}")

    async def start_polling(self):
        """Запуск бота в режиме polling."""
        try:
            bot_logger.info("Starting bot in polling mode")
            await self.dp.start_polling(self.bot, skip_updates=True)
        except Exception as e:
            bot_logger.error(f"Polling error: {e}")
            raise
        finally:
            await self.cleanup()

    async def start_webhook(self):
        """Запуск бота в режиме webhook."""
        if not settings.telegram.webhook_url:
            raise ConfigurationError("Webhook URL not configured")

        try:
            # Настройка webhook
            await self.bot.set_webhook(
                url=settings.telegram.webhook_url,
                secret_token=settings.telegram.webhook_secret
            )

            # Создание web приложения
            app = web.Application()

            # Настройка webhook handler
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=self.dp,
                bot=self.bot,
                secret_token=settings.telegram.webhook_secret
            )

            webhook_requests_handler.register(app, path="/webhook")
            setup_application(app, self.dp, bot=self.bot)

            self.app = app

            bot_logger.info("Bot webhook configured")
            return app

        except Exception as e:
            bot_logger.error(f"Webhook setup error: {e}")
            raise

    async def cleanup(self):
        """Очистка ресурсов."""
        if self.bot:
            await self.bot.session.close()

        if self.storage:
            await self.storage.close()

        await cache.disconnect()

        bot_logger.info("Bot cleanup completed")


async def start_bot():
    """Запуск Telegram бота."""
    telegram_bot = TelegramBot()

    try:
        await telegram_bot.setup()

        # Выбор режима запуска
        if settings.telegram.webhook_url:
            # Webhook режим (для продакшена)
            app = await telegram_bot.start_webhook()
            runner = web.AppRunner(app)
            await runner.setup()

            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()

            bot_logger.info("Bot started in webhook mode on port 8080")

            # Ожидание завершения
            while True:
                await asyncio.sleep(1)
        else:
            # Polling режим (для разработки)
            await telegram_bot.start_polling()

    except Exception as e:
        bot_logger.error(f"Bot startup failed: {e}")
        raise
