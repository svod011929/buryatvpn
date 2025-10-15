"""
Клавиатуры для пользователей.
"""

from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню пользователя."""
    builder = ReplyKeyboardBuilder()

    # Первый ряд
    builder.row(
        KeyboardButton(text="🌐 Мои подписки"),
        KeyboardButton(text="💳 Купить подписку")
    )

    # Второй ряд
    builder.row(
        KeyboardButton(text="🎁 Пробный период"),
        KeyboardButton(text="👥 Рефералы")
    )

    # Третий ряд
    builder.row(
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="📞 Поддержка")
    )

    return builder.as_markup(resize_keyboard=True)


def get_subscription_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню управления подписками."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="sub:stats"),
        InlineKeyboardButton(text="📋 Конфигурация", callback_data="sub:config")
    )

    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data="sub:refresh"),
        InlineKeyboardButton(text="❌ Удалить", callback_data="sub:delete")
    )

    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="menu:main")
    )

    return builder.as_markup()


def get_tariff_keyboard(tariffs: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифа."""
    builder = InlineKeyboardBuilder()

    for tariff in tariffs:
        builder.row(
            InlineKeyboardButton(
                text=f"{tariff['name']} - {tariff['price']} {tariff['currency']}",
                callback_data=f"tariff:select:{tariff['id']}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="menu:main")
    )

    return builder.as_markup()


def get_payment_method_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💳 Банковская карта", callback_data="pay:yookassa"),
        InlineKeyboardButton(text="🪙 Криптовалюта", callback_data="pay:crypto")
    )

    builder.row(
        InlineKeyboardButton(text="🎫 Код оплаты", callback_data="pay:code"),
        InlineKeyboardButton(text="« Назад", callback_data="menu:tariffs")
    )

    return builder.as_markup()


def get_server_keyboard(servers: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора сервера."""
    builder = InlineKeyboardBuilder()

    for server in servers:
        flag = get_country_flag(server.get('country_code', ''))
        builder.row(
            InlineKeyboardButton(
                text=f"{flag} {server['name']} ({server['city'] or 'Unknown'})",
                callback_data=f"server:select:{server['id']}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="menu:main")
    )

    return builder.as_markup()


def get_referral_keyboard(referral_code: str, bot_username: str) -> InlineKeyboardMarkup:
    """Клавиатура реферальной системы."""
    builder = InlineKeyboardBuilder()

    referral_link = f"https://t.me/{bot_username}?start={referral_code}"

    builder.row(
        InlineKeyboardButton(text="📋 Копировать ссылку", url=referral_link)
    )

    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="referral:stats"),
        InlineKeyboardButton(text="🎁 Бонусы", callback_data="referral:bonuses")
    )

    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="menu:main")
    )

    return builder.as_markup()


def get_support_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура поддержки."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="support:contact"),
        InlineKeyboardButton(text="❓ FAQ", callback_data="support:faq")
    )

    builder.row(
        InlineKeyboardButton(text="📱 Инструкции", callback_data="support:guides"),
        InlineKeyboardButton(text="🔧 Настройка", callback_data="support:setup")
    )

    builder.row(
        InlineKeyboardButton(text="« Назад", callback_data="menu:main")
    )

    return builder.as_markup()


def get_confirmation_keyboard(action: str, item_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия."""
    builder = InlineKeyboardBuilder()

    callback_data = f"confirm:{action}"
    if item_id:
        callback_data += f":{item_id}"

    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=callback_data),
        InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
    )

    return builder.as_markup()


def get_country_flag(country_code: str) -> str:
    """Получение флага страны по коду."""
    flags = {
        'RU': '🇷🇺',
        'US': '🇺🇸',
        'DE': '🇩🇪',
        'NL': '🇳🇱',
        'SG': '🇸🇬',
        'JP': '🇯🇵',
        'GB': '🇬🇧',
        'FR': '🇫🇷',
        'CA': '🇨🇦',
        'AU': '🇦🇺',
    }
    return flags.get(country_code.upper(), '🌍')
