from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from loguru import logger
import aiosqlite

from handlers.database import db
from handlers.admin.admin_kb import get_servers_keyboard

router = Router()

class ServerDeleteStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_name = State()

@router.callback_query(F.data == "delete_server")
async def start_server_delete(callback: CallbackQuery, state: FSMContext):
    """Начало процесса удаления сервера"""
    try:
        if not await db.is_admin(callback.from_user.id):
            await callback.answer("У вас нет прав для выполнения этого действия")
            return

        await callback.message.delete()
        
        await callback.message.answer(
            "🗑 Введите URL сервера для удаления:\n"
            "Пример: https://3xui.example.com"
        )
        
        await state.set_state(ServerDeleteStates.waiting_for_url)
        
    except Exception as e:
        logger.error(f"Ошибка при начале удаления сервера: {e}")
        await callback.message.answer(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=get_servers_keyboard()
        )

@router.message(ServerDeleteStates.waiting_for_url)
async def process_delete_url(message: Message, state: FSMContext):
    """Обработка введенного URL и удаление сервера"""
    try:
        url = message.text.strip()
        
        async with aiosqlite.connect(db.db_path) as conn:
            async with conn.execute(
                "SELECT id, url FROM server_settings WHERE url = ?",
                (url,)
            ) as cursor:
                server = await cursor.fetchone()
                
                if not server:
                    await message.answer(
                        "❌ Сервер с таким URL не найден в системе.",
                        reply_markup=get_servers_keyboard()
                    )
                    await state.clear()
                    return

            server_id = server[0]

            await conn.execute(
                "UPDATE tariff SET is_enable = 0 WHERE server_id = ? AND is_enable = 1",
                (server_id,)
            )
            
            await conn.execute(
                "DELETE FROM server_settings WHERE url = ?",
                (url,)
            )
            await conn.commit()
        
        await message.answer(
            f"✅ Сервер {url} успешно удален из системы",
            reply_markup=get_servers_keyboard()
        )
        logger.info(f"Удален сервер: {url}")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении сервера: {e}")
        await message.answer(
            "Произошла ошибка при удалении сервера. Попробуйте позже.",
            reply_markup=get_servers_keyboard()
        )
    finally:
        await state.clear()

@router.message(ServerDeleteStates.waiting_for_name)
async def process_delete_server(message: Message, state: FSMContext):
    """Обработка введенного названия сервера и его удаление"""
    try:
        server_name = message.text.strip()
        
        async with aiosqlite.connect(db.db_path) as conn:
            async with conn.execute(
                "SELECT id, name FROM server_settings WHERE name = ? AND is_enable = 1",
                (server_name,)
            ) as cursor:
                server = await cursor.fetchone()
                
            if not server:
                await message.answer(
                    "❌ Сервер с таким названием не найден.",
                    reply_markup=get_servers_keyboard()
                )
                await state.clear()
                return

            server_id = server[0]
                
            await conn.execute(
                "UPDATE tariff SET is_enable = 0 WHERE server_id = ? AND is_enable = 1",
                (server_id,)
            )
            
            async with conn.execute(
                "SELECT COUNT(*) FROM tariff WHERE server_id = ? AND is_enable = 0",
                (server_id,)
            ) as cursor:
                disabled_tariffs_count = (await cursor.fetchone())[0]

            await conn.execute(
                "UPDATE server_settings SET is_enable = 0 WHERE name = ?",
                (server_name,)
            )
            await conn.commit()
            
        success_message = f"✅ Сервер '{server_name}' успешно удален"
        if disabled_tariffs_count > 0:
            success_message += f"\nТакже отключено {disabled_tariffs_count} связанных тарифных планов"
            
        await message.answer(
            success_message,
            reply_markup=get_servers_keyboard()
        )
        logger.info(f"Удален сервер: {server_name} и {disabled_tariffs_count} связанных тарифов")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении сервера: {e}")
        await message.answer(
            "Произошла ошибка при удалении сервера. Попробуйте позже.",
            reply_markup=get_servers_keyboard()
        )
    finally:
        await state.clear() 