from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from loguru import logger
import os
import aiosqlite

from handlers.database import db
from handlers.user.user_kb import get_start_keyboard, get_unknown_command_keyboard

router = Router()

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
    resize_keyboard=True,
    persistent=True
)

@router.message(F.text == "🏠 Главное меню")
async def main_menu_button(message: Message):
    """Обработчик кнопки Главное меню"""
    await start_command(message)

@router.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT is_enable FROM user WHERE telegram_id = ?",
                (message.from_user.id,)
            ) as cursor:
                user = await cursor.fetchone()
                
                if user and user['is_enable'] == 0:
                    ban_message = await db.get_bot_message("ban_user")
                    if ban_message:
                        if ban_message['image_path'] and os.path.exists(ban_message['image_path']):
                            photo = FSInputFile(ban_message['image_path'])
                            await message.answer_photo(
                                photo=photo,
                                caption=ban_message['text'],
                                parse_mode="HTML",
                                reply_markup=ReplyKeyboardRemove()
                            )
                        else:
                            await message.answer(
                                ban_message['text'],
                                parse_mode="HTML",
                                reply_markup=ReplyKeyboardRemove()
                            )
                    else:
                        await message.answer(
                            "Ваш аккаунт заблокирован.",
                            reply_markup=ReplyKeyboardRemove()
                        )
                    return

        start_message = await db.get_bot_message("start")
        if not start_message:
            text = "Добро пожаловать!"
        else:
            text = start_message['text']

        inline_keyboard = get_start_keyboard()
            
        await db.register_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            bot=message.bot
        )

        if start_message and start_message['image_path'] and os.path.exists(start_message['image_path']):
            photo = FSInputFile(start_message['image_path'])
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=inline_keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text=text,
                reply_markup=inline_keyboard,
                parse_mode="HTML"
            )
        await message.answer(
            "Главное меню ⤴️",
            reply_markup=main_menu_keyboard
        )
        logger.info(f"Отправлено стартовое сообщение пользователю: {message.from_user.id}")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке команды start: {e}")
        await message.answer("Произошла ошибка при выполнении команды")
