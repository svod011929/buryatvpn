"""
Обработчики команд бота.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.services.user_service import UserService
from app.bot.keyboards.user_keyboards import get_main_menu_keyboard
from app.bot.utils.messages import get_bot_message
from app.core.exceptions import UserNotFoundError
from config.logging import bot_logger

router = Router()
user_service = UserService()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    try:
        # Очищаем состояние FSM
        await state.clear()

        # Извлекаем реферальный код из глубокой ссылки
        args = message.text.split(' ', 1)
        referral_code = args[1] if len(args) > 1 else None

        # Получаем или создаем пользователя
        user_data = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            referred_by=referral_code
        )

        # Проверяем, не заблокирован ли пользователь
        if user_data.get('is_banned'):
            await message.answer(
                "❌ Ваш аккаунт заблокирован. Обратитесь в поддержку.",
                reply_markup=None
            )
            return

        # Получаем приветственное сообщение
        welcome_msg = await get_bot_message('welcome')

        # Персонализируем сообщение
        name = user_data.get('first_name') or user_data.get('username') or 'пользователь'
        text = welcome_msg['text'].format(name=name)

        await message.answer(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=welcome_msg.get('parse_mode', 'HTML')
        )

        bot_logger.info(f"User {message.from_user.id} started bot")

    except Exception as e:
        bot_logger.error(f"Error in start command: {e}")
        await message.answer(
            "Произошла ошибка при запуске бота. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    try:
        help_msg = await get_bot_message('help')

        await message.answer(
            help_msg['text'],
            parse_mode=help_msg.get('parse_mode', 'HTML'),
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        bot_logger.error(f"Error in help command: {e}")
        await message.answer(
            "Помощь временно недоступна. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Обработчик команды /profile."""
    try:
        user_profile = await user_service.get_user_profile(message.from_user.id)

        # Формируем информацию о профиле
        profile_text = f"""
👤 <b>Ваш профиль</b>

🆔 ID: {user_profile['telegram_id']}
👤 Имя: {user_profile.get('first_name', 'Не указано')}
🏷 Username: @{user_profile.get('username', 'не указан')}
📧 Email: {user_profile.get('email', 'Не указан')}

📊 <b>Статистика</b>
🎁 Пробный период: {'Использован' if user_profile['trial_used'] else 'Доступен'}
💳 Активных подписок: {1 if user_profile['has_active_subscription'] else 0}
👥 Приглашено друзей: {user_profile['referral_stats']['total_referred']}

🔗 <b>Реферальная ссылка</b>
<code>https://t.me/{(await message.bot.get_me()).username}?start={user_profile['referral_code']}</code>

📅 Регистрация: {user_profile['created_at'][:10] if user_profile['created_at'] else 'Неизвестно'}
"""

        await message.answer(
            profile_text,
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )

    except UserNotFoundError:
        await message.answer(
            "Пользователь не найден. Начните с команды /start",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        bot_logger.error(f"Error in profile command: {e}")
        await message.answer(
            "Ошибка при получении профиля. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработчик команды /cancel для отмены текущего действия."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Нет активных действий для отмены.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "Действие отменено.",
        reply_markup=get_main_menu_keyboard()
    )

    bot_logger.info(f"User {message.from_user.id} cancelled action in state {current_state}")


def setup_handlers(dp):
    """Регистрация обработчиков команд."""
    dp.include_router(router)
