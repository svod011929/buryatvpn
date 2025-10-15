"""
Утилиты для работы с сообщениями бота.
"""

from typing import Dict, Optional
from app.database.repositories.base import BaseRepository
from app.database.models import BotMessage
from app.core.cache import cache, cached
from config.logging import bot_logger

# Репозиторий для сообщений бота
bot_message_repo = BaseRepository(BotMessage)


@cached(ttl=3600, key_prefix="bot_message")
async def get_bot_message(key: str) -> Dict[str, str]:
    """Получение сообщения бота по ключу с кэшированием."""
    try:
        message = await bot_message_repo.get_by_field('key', key)

        if message:
            return {
                'text': message.text,
                'image_path': message.image_path,
                'parse_mode': message.parse_mode
            }
        else:
            # Возвращаем сообщение по умолчанию
            return get_default_message(key)

    except Exception as e:
        bot_logger.error(f"Failed to get bot message '{key}': {e}")
        return get_default_message(key)


def get_default_message(key: str) -> Dict[str, str]:
    """Получение сообщения по умолчанию."""

    default_messages = {
        'welcome': {
            'text': """
🎉 <b>Добро пожаловать в BuryatVPN, {name}!</b>

🚀 <b>Ваш надежный VPN сервис</b>

✅ Быстрые и стабильные соединения
✅ Серверы по всему миру  
✅ Максимальная конфиденциальность
✅ Техническая поддержка 24/7

🎁 <b>Специально для новых пользователей:</b>
• Бесплатный пробный период
• Скидки на первую покупку
• Реферальная программа

👇 Выберите действие в меню ниже
""",
            'parse_mode': 'HTML'
        },

        'help': {
            'text': """
📖 <b>Справка по боту BuryatVPN</b>

<b>Команды:</b>
/start - Главное меню
/profile - Ваш профиль
/help - Эта справка

<b>Основные функции:</b>
🌐 <b>Мои подписки</b> - управление VPN подписками
💳 <b>Купить подписку</b> - выбор и покупка тариных планов
🎁 <b>Пробный период</b> - активация бесплатного пробного периода
👥 <b>Рефералы</b> - приглашение друзей и получение бонусов

<b>Поддержка:</b>
📞 Техническая поддержка доступна 24/7
💬 Используйте кнопку "Поддержка" в главном меню

<b>Инструкции по настройке:</b>
📱 Доступны для всех популярных устройств и приложений
""",
            'parse_mode': 'HTML'
        },

        'trial_available': {
            'text': """
🎁 <b>Бесплатный пробный период</b>

✅ Доступен пробный период на 3 дня
✅ Полный доступ ко всем функциям
✅ Без ограничений скорости
✅ Выбор любого сервера

❗️ Пробный период предоставляется только один раз

Хотите активировать пробный период?
""",
            'parse_mode': 'HTML'
        },

        'trial_used': {
            'text': """
ℹ️ <b>Пробный период уже использован</b>

Вы уже воспользовались бесплатным пробным периодом.

💳 Для продолжения использования VPN выберите один из наших тарифных планов:

👇 Нажмите "Купить подписку" в главном меню
""",
            'parse_mode': 'HTML'
        },

        'no_subscriptions': {
            'text': """
📭 <b>У вас пока нет активных подписок</b>

🎁 Вы можете начать с бесплатного пробного периода
💳 Или сразу приобрести подписку

👇 Выберите действие в главном меню
""",
            'parse_mode': 'HTML'
        },

        'error': {
            'text': """
❌ <b>Произошла ошибка</b>

Попробуйте выполнить действие позже или обратитесь в поддержку.

📞 Поддержка работает 24/7
""",
            'parse_mode': 'HTML'
        }
    }

    return default_messages.get(key, {
        'text': f'Сообщение "{key}" не найдено',
        'parse_mode': 'HTML'
    })


async def update_bot_message(key: str, text: str, image_path: str = None, parse_mode: str = 'HTML') -> bool:
    """Обновление сообщения бота."""
    try:
        # Проверяем, существует ли сообщение
        existing = await bot_message_repo.get_by_field('key', key)

        if existing:
            # Обновляем существующее
            await bot_message_repo.update(
                existing.id,
                text=text,
                image_path=image_path,
                parse_mode=parse_mode
            )
        else:
            # Создаем новое
            await bot_message_repo.create(
                key=key,
                text=text,
                image_path=image_path,
                parse_mode=parse_mode
            )

        # Инвалидируем кэш
        await cache.delete(f"bot_message:{key}")

        bot_logger.info(f"Bot message '{key}' updated")
        return True

    except Exception as e:
        bot_logger.error(f"Failed to update bot message '{key}': {e}")
        return False


def format_subscription_info(subscription: Dict) -> str:
    """Форматирование информации о подписке."""
    if not subscription:
        return "Подписка не найдена"

    status_emoji = "✅" if subscription.get('is_active') else "❌"
    trial_text = " (Пробная)" if subscription.get('is_trial') else ""

    return f"""
{status_emoji} <b>{subscription.get('tariff_name', 'Неизвестный тариф')}{trial_text}</b>

🖥 Сервер: {subscription.get('server_name', 'Неизвестно')}
📅 Активна до: {subscription.get('end_date', 'Неизвестно')[:10] if subscription.get('end_date') else 'Неизвестно'}
📊 Трафик: {format_traffic(subscription.get('traffic_used', 0))}
"""


def format_traffic(bytes_count: int) -> str:
    """Форматирование трафика в человекочитаемый вид."""
    if bytes_count == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while bytes_count >= 1024 and unit_index < len(units) - 1:
        bytes_count /= 1024
        unit_index += 1

    return f"{bytes_count:.1f} {units[unit_index]}"


def format_price(amount: float, currency: str = "RUB") -> str:
    """Форматирование цены."""
    currency_symbols = {
        'RUB': '₽',
        'USD': '$',
        'EUR': '€',
        'BTC': '₿',
        'ETH': 'Ξ'
    }

    symbol = currency_symbols.get(currency, currency)
    return f"{amount:.2f} {symbol}"
