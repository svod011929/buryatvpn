from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Создание стартовой клавиатуры"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 Личный кабинет", callback_data="start_lk"),
        InlineKeyboardButton(text="🎁 Пробный период", callback_data="start_trial"),
        InlineKeyboardButton(text="💳 Тарифы", callback_data="start_tariffs"),
        InlineKeyboardButton(text="📞 Техподдержка", callback_data="help_support"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:])
    builder.row(InlineKeyboardButton(text="📢 Наши новости", url="https://t.me/buryatvpn"))
    return builder.as_markup()

def get_lk_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры личного кабинета"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="📋 Мои подписки", callback_data="lk_my_subscriptions"),
        InlineKeyboardButton(text="💰 Мои платежи", callback_data="lk_my_payments"),
        InlineKeyboardButton(text="📢 Инструкции", callback_data="lk_instructions"),
        InlineKeyboardButton(text="💬 Помощь", callback_data="start_help"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="lk_back_to_start"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    builder.row(buttons[4])  
    
    return builder.as_markup()

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_trial_keyboard(show_connect: bool = True) -> InlineKeyboardMarkup:
    """Создание клавиатуры для пробного периода"""
    builder = InlineKeyboardBuilder()
    
    if show_connect:
        buttons = [
            InlineKeyboardButton(text="🔗 Подключить", callback_data="trial_connect"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="trial_back"),
        ]
    else:
        buttons = [
            InlineKeyboardButton(text="💳 Тарифы", callback_data="start_tariffs"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="trial_back"),
        ]
    
    builder.row(*buttons)
    
    return builder.as_markup()

def get_trial_vless_keyboard(show_connect: bool = True) -> InlineKeyboardMarkup:
    """Создание клавиатуры для сообщения с ключом vless"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="💳 Тарифы", callback_data="start_tariffs"),
        InlineKeyboardButton(text="🚀 VPN Клиент", callback_data="show_vpn_client"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="show_settings"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="trial_back"),
    ]
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    return builder.as_markup()

def get_subscriptions_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для отображения подписок"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 Вернуться в кабинет", callback_data="start_lk"),
        InlineKeyboardButton(text="🤝 Объеденить подписки", callback_data="merge_subscriptions"),
        InlineKeyboardButton(text="💳 Тарифы", callback_data="start_tariffs"),
        InlineKeyboardButton(text="💬 Помощь", callback_data="start_help"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:])    
    return builder.as_markup()

def get_continue_merge_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для продолжения объединения подписок"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 Вернуться в кабинет", callback_data="start_lk"),
        InlineKeyboardButton(text="✅ Продолжить", callback_data="continue_merge"),
    ]
    
    builder.row(*buttons[:2])
    return builder.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для кнопки назад"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 Вернуться в кабинет", callback_data="start_lk"),
    ]
    
    builder.row(*buttons[:2])
    return builder.as_markup()

def get_success_by_keyboard(show_connect: bool = True) -> InlineKeyboardMarkup:
    """Создание клавиатуры для сообщения с ключом vless"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 Личный кабинет", callback_data="start_lk"),
        InlineKeyboardButton(text="📋 Мои подписки", callback_data="lk_my_subscriptions"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="lk_back_to_start"),
    ]
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    return builder.as_markup()

def get_help_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для раздела помощи"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="🤝 Объеденить подписки", callback_data="merge_subscriptions"),
        InlineKeyboardButton(text="📞 Техподдержка", callback_data="help_support"),
        InlineKeyboardButton(text="👤 Вернуться в кабинет", callback_data="start_lk"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    return builder.as_markup()

def get_no_subscriptions_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для сообщения о том что нет активных подписок"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="👤 В личный кабинет", callback_data="start_lk"),
        InlineKeyboardButton(text="💳 Тарифы", callback_data="start_tariffs"),
        InlineKeyboardButton(text="📞 Техподдержка", callback_data="help_support"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    return builder.as_markup()

def get_user_instructions_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для раздела инструкций"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="📱 Android", callback_data="instructions_android"),
        InlineKeyboardButton(text="📱 IOS", callback_data="instructions_ios"),
        InlineKeyboardButton(text="💻 Windows", callback_data="instructions_windows"),
        InlineKeyboardButton(text="💻 MacOS", callback_data="instructions_macos"),
    ]
    
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    return builder.as_markup()

def get_unknown_command_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры для неизвестной команды"""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="📞 Техподдержка", callback_data="help_support"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="lk_back_to_start"),
    ]
    
    builder.row(*buttons[:2])
    return builder.as_markup()