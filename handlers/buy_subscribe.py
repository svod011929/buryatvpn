import random
import aiosqlite
from loguru import logger
from typing import Optional, Dict
from handlers.x_ui import xui_manager
from handlers.database import db
from datetime import datetime, timedelta
from handlers.admin.admin_kb import get_admin_keyboard
from aiogram.types import Message

class SubscriptionManager:
    @staticmethod
    def generate_user_id() -> str:
        """Генерация уникального ID пользователя"""
        return f"@{random.randint(10000, 99999)}"

    async def create_subscription(self, user_id: int, tariff_id: int, is_trial: bool = False, bot = None, payment_id: str = None) -> Optional[Dict]:
        """Создание подписки для пользователя"""
        try:
            async with aiosqlite.connect(db.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                if is_trial:
                    async with conn.execute("""
                        SELECT t.*, s.* 
                        FROM trial_settings t 
                        JOIN server_settings s ON t.server_id = s.id 
                        WHERE t.id = ? AND t.is_enable = 1
                    """, (tariff_id,)) as cursor:
                        tariff_data = await cursor.fetchone()
                else:
                    async with conn.execute("""
                        SELECT t.*, s.* 
                        FROM tariff t 
                        JOIN server_settings s ON t.server_id = s.id 
                        WHERE t.id = ? AND t.is_enable = 1
                    """, (tariff_id,)) as cursor:
                        tariff_data = await cursor.fetchone()

                if tariff_data:
                    tariff_data = dict(tariff_data)

            if not tariff_data:
                logger.error(f"Тариф {tariff_id} не найден")
                return None

            end_date = datetime.now() + timedelta(days=tariff_data['left_day'])

            vless_link = await xui_manager.create_trial_user(
                server_settings=tariff_data,
                trial_settings={'left_day': tariff_data['left_day']},
                telegram_id=user_id
            )

            if not vless_link:
                logger.error("Ошибка при создании пользователя в X-UI")
                return None

            async with aiosqlite.connect(db.db_path) as conn:
                await conn.execute("""
                    INSERT INTO user_subscription 
                    (user_id, tariff_id, server_id, end_date, vless, is_active, payment_id)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (
                    user_id, 
                    tariff_id, 
                    tariff_data['server_id'], 
                    end_date, 
                    vless_link,
                    payment_id
                ))
                await conn.commit()

                if bot:
                    async with conn.execute(
                        'SELECT pay_notify FROM bot_settings LIMIT 1'
                    ) as cursor:
                        notify_settings = await cursor.fetchone()

                    if notify_settings and notify_settings[0] != 0:
                        async with conn.execute(
                            'SELECT username FROM user WHERE telegram_id = ?',
                            (user_id,)
                        ) as cursor:
                            user_data = await cursor.fetchone()
                            username = user_data[0] if user_data else f"ID: {user_id}"

                        message_text = (
                            "🎉 Новая подписка! 🏆\n"
                            "<blockquote>"
                            f"👤 Пользователь: {username}\n"
                            f"💳 Тариф: {tariff_data['name']}\n"
                            f"📅 Дата активации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            "🚀 Подписка успешно оформлена!</blockquote>"
                        )

                        try:
                            await bot.send_message(
                                chat_id=notify_settings[0],
                                text=message_text,
                                parse_mode="HTML",
                                reply_markup=get_admin_keyboard()
                            )
                        except Exception as e:
                            logger.error(f"Ошибка при отправке уведомления о подписке: {e}")

            return {
                'vless': vless_link,
                'end_date': end_date,
                'tariff': tariff_data
            }

        except Exception as e:
            logger.error(f"Ошибка при создании подписки: {e}")
            return None

subscription_manager = SubscriptionManager()

async def process_successful_payment(message: Message):
    """Обработка успешного платежа"""
    try:
        subscription = await subscription_manager.create_subscription(
            user_id=message.from_user.id,
            tariff_id=tariff_id,
            bot=message.bot,    
            payment_id=payment_id
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке успешного платежа: {e}") 