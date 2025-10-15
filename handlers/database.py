import os
import aiosqlite
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List
from loguru import logger
from aiogram import Bot
from handlers.admin.admin_kb import get_admin_keyboard
import random
import string

os.makedirs('instance', exist_ok=True)
os.makedirs('handlers', exist_ok=True)

class Database:
    def __init__(self, db_path: str = 'instance/database.db'):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    bot_token TEXT NOT NULL,
                    admin_id TEXT NOT NULL,
                    chat_id TEXT,
                    chanel_id TEXT,
                    is_enable BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS server_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ip TEXT,
                    url TEXT NOT NULL,
                    port TEXT NOT NULL,
                    secret_path TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    secretkey TEXT,
                    inbound_id INTEGER,
                    is_enable BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_message (
                    command TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    image_path TEXT,
                    is_enable BOOLEAN NOT NULL DEFAULT 1
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    trial_period BOOLEAN DEFAULT 0,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    referral_code TEXT UNIQUE,
                    referral_count INTEGER DEFAULT 0,
                    referred_by TEXT
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tariff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    left_day INTEGER NOT NULL,
                    server_id INTEGER NOT NULL,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (server_id) REFERENCES server_settings(id)
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trial_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    left_day INTEGER NOT NULL,
                    server_id INTEGER NOT NULL,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (server_id) REFERENCES server_settings(id)
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_subscription (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tariff_id INTEGER NOT NULL,
                    server_id INTEGER NOT NULL,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP NOT NULL,
                    vless TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user(id),
                    FOREIGN KEY (tariff_id) REFERENCES tariff(id),
                    FOREIGN KEY (server_id) REFERENCES server_settings(id)
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS yookassa_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    shop_id TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    description TEXT,
                    is_enable INTEGER DEFAULT 0
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS promocodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    promocod TEXT NOT NULL,
                    activation_limit INTEGER DEFAULT 1,
                    activation_total INTEGER DEFAULT 0,
                    percentage DECIMAL(5,2) NOT NULL,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tariff_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (tariff_id) REFERENCES tariff (id)
                )
            """)
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS support_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    bot_version TEXT NOT NULL,
                    support_url TEXT NOT NULL
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notify_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    interval INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    is_enable BOOLEAN NOT NULL DEFAULT 1
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS payments_code (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pay_code TEXT UNIQUE NOT NULL,
                    sum DECIMAL(10,2) NOT NULL,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS crypto_settings (
                    api_token TEXT NOT NULL,
                    is_enable BOOLEAN DEFAULT 0,
                    min_amount DECIMAL(10,2) DEFAULT 1.00,
                    supported_assets TEXT,  -- JSON строка с поддерживаемыми криптовалютами
                    webhook_url TEXT,
                    webhook_secret TEXT
                )
            ''')
            
            await conn.commit()
            logger.info("База данных инициализирована")

    async def get_bot_settings(self) -> Optional[Dict]:
        """Получение настроек бота из базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM bot_settings LIMIT 1') as cursor:
                settings = await cursor.fetchone()
                if settings:
                    return {
                        'bot_token': settings[0],
                        'admin_id': settings[1].split(','),
                        'chat_id': settings[2],
                        'chanel_id': settings[3],
                        'is_enable': bool(settings[4])
                    }
                return None

    async def get_bot_message(self, command: str) -> Optional[Dict]:
        """Получение сообщения бота по команде"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT * FROM bot_message WHERE command = ? AND is_enable = 1', 
                (command,)
            ) as cursor:
                message = await cursor.fetchone()
                if message:
                    return {
                        'command': message[0],
                        'text': message[1],
                        'image_path': message[2],
                        'is_enable': bool(message[3])
                    }
                return None

    async def get_all_servers(self) -> List[Dict]:
        """Получение списка всех серверов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM server_settings') as cursor:
                servers = await cursor.fetchall()
                return [dict(server) for server in servers]

    async def register_user(self, telegram_id: int, username: str = None, bot = None) -> bool:
        """Регистрация нового пользователя"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT id FROM user WHERE telegram_id = ?',
                    (telegram_id,)
                ) as cursor:
                    if await cursor.fetchone():
                        return True
                
                while True:
                    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    
                    async with db.execute(
                        'SELECT id FROM user WHERE referral_code = ?',
                        (referral_code,)
                    ) as cursor:
                        if not await cursor.fetchone():
                            break
                
                await db.execute(
                    'INSERT INTO user (telegram_id, username, referral_code) VALUES (?, ?, ?)',
                    (telegram_id, username, referral_code)
                )
                await db.commit()
                
                async with db.execute(
                    'SELECT reg_notify FROM bot_settings LIMIT 1'
                ) as cursor:
                    notify_settings = await cursor.fetchone()
                
                if notify_settings and notify_settings[0] != 0 and bot:
                    message_text = (
                        "🔔 Новая регистрация! 👤\n\n"
                        "🚀 Пользователь успешно зарегистрирован!\n"
                        "<blockquote>"
                        f"📌 ID: {telegram_id}\n"
                        f"👤 Username: {username or 'Не указан'}\n"
                        f"📅 Дата: {current_date}\n"
                        "</blockquote>"
                    )
                    
                    try:
                        await bot.send_message(
                            chat_id=notify_settings[0],
                            text=message_text,
                            parse_mode="HTML",
                            reply_markup=get_admin_keyboard()
                        )
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления о регистрации: {e}")
            
            logger.info(f"Зарегистрирован новый пользователь: {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя {telegram_id}: {e}")
            return False

    async def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM user WHERE telegram_id = ?',
                (telegram_id,)
            ) as cursor:
                user = await cursor.fetchone()
                return dict(user) if user else None

    async def get_active_trial_settings(self) -> Optional[Dict]:
        """Получение активных настроек пробного периода"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT t.*, s.name as server_name 
                    FROM trial_settings t 
                    JOIN server_settings s ON t.server_id = s.id
                    WHERE t.is_enable = 1 
                    LIMIT 1
                ''') as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении настроек пробного периода: {e}")
            return None

    async def update_user_trial_status(self, telegram_id: int, used: bool = True) -> bool:
        """Обновление статуса использования пробного периода"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE user SET trial_period = ? WHERE telegram_id = ?',
                    (used, telegram_id)
                )
                await db.commit()
                logger.info(f"Обновлен статус пробного периода для пользователя {telegram_id}: {used}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса пробного периода для пользователя {telegram_id}: {e}")
            return False

    async def is_admin(self, user_id: int) -> bool:
        """Проверка является ли пользователь администратором"""
        settings = await self.get_bot_settings()
        if settings and settings['admin_id']:
            return str(user_id) in settings['admin_id']
        return False

    async def get_server_settings(self, server_id: int) -> Optional[Dict]:
        """Получение настроек сервера по ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM server_settings WHERE id = ?',
                    (server_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении настроек сервера {server_id}: {e}")
            return None

    async def get_connection(self):
        """Получение соединения с базой данных"""
        return await aiosqlite.connect(self.db_path)

    async def get_active_tariffs(self) -> List[Dict]:
        """Получение активных тарифов с информацией о серверах"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT t.*, s.name as server_name 
                    FROM tariff t 
                    INNER JOIN server_settings s ON t.server_id = s.id 
                    WHERE t.is_enable = 1 AND s.is_enable = 1
                """) as cursor:
                    tariffs = await cursor.fetchall()
                    return [dict(row) for row in tariffs] if tariffs else []
        except Exception as e:
            logger.error(f"Ошибка при получении тарифов: {e}")
            return []

    async def get_yookassa_settings(self):
        """Получение настроек YooKassa"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM yookassa_settings LIMIT 1") as cursor:
                settings = await cursor.fetchone()
                return settings if settings else None

    async def update_yookassa_settings(self, name, shop_id, api_key, description, is_enable):
        """Обновление настроек YooKassa"""
        async with await self.get_connection() as db:
            await db.execute('''
                INSERT OR REPLACE INTO yookassa_settings (id, name, shop_id, api_key, description, is_enable)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (name, shop_id, api_key, description, is_enable))
            await db.commit()

    async def enable_yookassa(self, enable: bool):
        """Включение/выключение YooKassa"""
        async with await self.get_connection() as db:
            await db.execute("UPDATE yookassa_settings SET is_enable = ?", (int(enable),))
            await db.commit()

    async def add_promo_tariff(self, name: str, description: str, left_day: int, server_id: int) -> bool:
        """Добавление нового промо-тарифа"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO tariff_promo (name, description, left_day, server_id, is_enable)
                    VALUES (?, ?, ?, ?, 1)
                """, (name, description, left_day, server_id))
                await conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении промо-тарифа: {e}")
            return False

    async def get_promo_tariffs(self) -> list:
        """Получение списка активных промо-тарифов"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("""
                    SELECT tp.*, ss.name as server_name
                    FROM tariff_promo tp
                    JOIN server_settings ss ON tp.server_id = ss.id
                    WHERE tp.is_enable = 1
                """) as cursor:
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении списка промо-тарифов: {e}")
            return []

    async def delete_promo_tariff(self, tariff_id: int) -> bool:
        """Деактивация промо-тарифа"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE tariff_promo 
                    SET is_enable = 0 
                    WHERE id = ?
                """, (tariff_id,))
                await conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении промо-тарифа: {e}")
            return False

    async def get_server_promo_inbound(self, server_id: int) -> int:
        """Получение promo inbound_id для сервера"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                async with conn.execute("""
                    SELECT inbound_id_promo 
                    FROM server_settings 
                    WHERE id = ?
                """, (server_id,)) as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении promo inbound_id: {e}")
            return None

    async def set_reg_notify(self, chat_id: int) -> bool:
        """Установка ID чата для уведомлений о регистрации"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE bot_settings 
                    SET reg_notify = ?
                """, (chat_id,))
                await conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при установке ID чата для уведомлений о регистрации: {e}")
            return False

    async def set_pay_notify(self, chat_id: int) -> bool:
        """Установка ID чата для уведомлений о платежах"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE bot_settings 
                    SET pay_notify = ?
                """, (chat_id,))
                await conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при установке ID чата для уведомлений о платежах: {e}")
            return False

    async def get_notify_settings(self) -> dict:
        """Получение настроек уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("""
                    SELECT reg_notify, pay_notify 
                    FROM bot_settings 
                    LIMIT 1
                """) as cursor:
                    return dict(await cursor.fetchone())
        except Exception as e:
            logger.error(f"Ошибка при получении настроек уведомлений: {e}")
            return {}

    async def add_review(self, username: str, message: str) -> bool:
        """Добавление нового отзыва"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO Reviews (username, message)
                    VALUES (?, ?)
                """, (username, message))
                await conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении отзыва: {e}")
            return False

    async def get_reviews(self, limit: int = 10) -> list:
        """Получение последних отзывов"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("""
                    SELECT * FROM Reviews 
                    ORDER BY date DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении отзывов: {e}")
            return []

    async def get_support_info(self) -> Optional[Dict]:
        """Получение информации о поддержке"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM support_info ORDER BY id DESC LIMIT 1') as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о поддержке: {e}")
            return None

    async def update_support_info(self, message: str, bot_version: str, support_url: str) -> bool:
        """Обновление информации о поддержке"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO support_info (message, bot_version, support_url)
                    VALUES (?, ?, ?)
                ''', (message, bot_version, support_url))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении информации о поддержке: {e}")
            return False

    async def add_notify_setting(self, name: str, interval: int, type: str) -> bool:
        """Добавление новой настройки уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE notify_settings 
                    SET is_enable = 0 
                    WHERE type = ? AND is_enable = 1
                """, (type,))
                
                await db.execute("""
                    INSERT INTO notify_settings (name, interval, type)
                    VALUES (?, ?, ?)
                """, (name, interval, type))
                
                await db.commit()
                logger.info(f"Добавлена новая настройка уведомлений: {name} (тип: {type})")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении настройки уведомлений: {e}")
            return False

    async def get_notify_setting(self, setting_id: int) -> Optional[Dict]:
        """Получение настройки уведомлений по ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM notify_settings WHERE id = ?',
                    (setting_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении настройки уведомлений: {e}")
            return None

    async def get_all_notify_settings(self) -> List[Dict]:
        """Получение всех настроек уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM notify_settings') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении всех настроек уведомлений: {e}")
            return []

    async def get_active_notify_settings(self) -> List[Dict]:
        """Получение активных настроек уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM notify_settings WHERE is_enable = 1'
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении активных настроек уведомлений: {e}")
            return []

    async def update_notify_setting(self, setting_id: int, name: str = None, 
                                  interval: int = None, type: str = None, 
                                  is_enable: bool = None) -> bool:
        """Обновление настройки уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT * FROM notify_settings WHERE id = ?',
                    (setting_id,)
                ) as cursor:
                    current = await cursor.fetchone()
                    if not current:
                        return False

                update_values = []
                update_fields = []
                if name is not None:
                    update_fields.append("name = ?")
                    update_values.append(name)
                if interval is not None:
                    update_fields.append("interval = ?")
                    update_values.append(interval)
                if type is not None:
                    update_fields.append("type = ?")
                    update_values.append(type)
                if is_enable is not None:
                    update_fields.append("is_enable = ?")
                    update_values.append(is_enable)

                if update_fields:
                    update_values.append(setting_id)
                    query = f"""
                        UPDATE notify_settings 
                        SET {', '.join(update_fields)}
                        WHERE id = ?
                    """
                    await db.execute(query, update_values)
                    await db.commit()
                    logger.info(f"Обновлена настройка уведомлений ID: {setting_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении настройки уведомлений: {e}")
            return False

    async def delete_notify_setting(self, setting_id: int) -> bool:
        """Удаление настройки уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM notify_settings WHERE id = ?',
                    (setting_id,)
                )
                await db.commit()
                logger.info(f"Удалена настройка уведомлений ID: {setting_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении настройки уведомлений: {e}")
            return False

    async def enable_notify_setting(self, setting_id: int, enable: bool) -> bool:
        """Включение/выключение настройки уведомлений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE notify_settings SET is_enable = ? WHERE id = ?',
                    (enable, setting_id)
                )
                await db.commit()
                status = "включена" if enable else "выключена"
                logger.info(f"Настройка уведомлений ID: {setting_id} {status}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при изменении статуса настройки уведомлений: {e}")
            return False

    async def update_notify_setting_by_name(self, name: str, is_enable: bool = None) -> bool:
        """Обновление настройки уведомлений по имени"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT id FROM notify_settings WHERE name = ? AND is_enable = 1',
                    (name,)
                ) as cursor:
                    setting = await cursor.fetchone()
                    if not setting:
                        return False

                if is_enable is not None:
                    await db.execute(
                        'UPDATE notify_settings SET is_enable = ? WHERE name = ?',
                        (is_enable, name)
                    )
                    await db.commit()
                    status = "включена" if is_enable else "выключена"
                    logger.info(f"Настройка уведомлений '{name}' {status}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка при обновлении настройки уведомлений по имени: {e}")
            return False

    async def get_expiring_subscriptions(self) -> List[Dict]:
        """Получение подписок, которые заканчиваются в течение 24 часов"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                now = datetime.now(timezone.utc)
                end_time = now + timedelta(hours=24)
                
                now_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                
                logger.debug(f"Проверка подписок между {now_str} и {end_time_str}")
                
                async with db.execute("""
                    SELECT * FROM user_subscription 
                    WHERE datetime(end_date) BETWEEN datetime(?) AND datetime(?)
                    AND is_active = 1
                """, (now_str, end_time_str)) as cursor:
                    rows = await cursor.fetchall()
                    subscriptions = [dict(row) for row in rows]
                    logger.debug(f"Найдено подписок: {len(subscriptions)}")
                    return subscriptions
        except Exception as e:
            logger.error(f"Ошибка при получении истекающих подписок: {e}")
            return []

    async def get_tariff(self, tariff_id: int) -> Optional[Dict]:
        """Получение информации о тарифе"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM tariff WHERE id = ?',
                    (tariff_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении тарифа: {e}")
            return None

    async def get_server(self, server_id: int) -> Optional[Dict]:
        """Получение информации о сервере"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM server_settings WHERE id = ?',
                    (server_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении сервера: {e}")
            return None

    async def add_payment_code(self, pay_code: str, sum: float) -> bool:
        """Добавление нового кода оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO payments_code (pay_code, sum)
                    VALUES (?, ?)
                """, (pay_code, sum))
                await db.commit()
                logger.info(f"Добавлен новый код оплаты: {pay_code}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении кода оплаты: {e}")
            return False

    async def get_payment_code(self, pay_code: str) -> Optional[Dict]:
        """Получение информации о коде оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM payments_code WHERE pay_code = ? AND is_enable = 1',
                    (pay_code,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении кода оплаты: {e}")
            return None

    async def disable_payment_code(self, pay_code: str) -> bool:
        """Деактивация кода оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE payments_code SET is_enable = 0 WHERE pay_code = ?',
                    (pay_code,)
                )
                await db.commit()
                logger.info(f"Код оплаты деактивирован: {pay_code}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при деактивации кода оплаты: {e}")
            return False

    async def get_all_payment_codes(self) -> List[Dict]:
        """Получение списка всех кодов оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM payments_code') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении списка кодов оплаты: {e}")
            return []

    async def enable_payment_code(self, pay_code: str) -> bool:
        """Активация кода оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE payments_code SET is_enable = 1 WHERE pay_code = ?',
                    (pay_code,)
                )
                await db.commit()
                logger.info(f"Код оплаты активирован: {pay_code}")
                return True
        except Exception as e:
            logger.error(f"Ошибка при активации кода оплаты: {e}")
            return False

    async def get_active_codes_sum(self) -> float:
        """Получение суммы всех активных кодов оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT SUM(sum) FROM payments_code WHERE is_enable = 1'
                ) as cursor:
                    result = await cursor.fetchone()
                    return float(result[0]) if result[0] is not None else 0.0
        except Exception as e:
            logger.error(f"Ошибка при получении суммы активных кодов: {e}")
            return 0.0

    async def get_used_codes_sum(self) -> float:
        """Получение суммы всех использованных кодов оплаты"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT SUM(sum) FROM payments_code WHERE is_enable = 0'
                ) as cursor:
                    result = await cursor.fetchone()
                    return float(result[0]) if result[0] is not None else 0.0
        except Exception as e:
            logger.error(f"Ошибка при получении суммы использованных кодов: {e}")
            return 0.0

    async def is_yookassa_enabled(self) -> bool:
        """Проверка активности Юкассы"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT is_enable FROM yookassa_settings WHERE is_enable = 1 LIMIT 1'
                ) as cursor:
                    result = await cursor.fetchone()
                    return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса Юкассы: {e}")
            return False

    async def is_crypto_enabled(self) -> bool:
        """Проверка активности Crypto Pay"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    'SELECT is_enable FROM crypto_settings WHERE is_enable = 1 LIMIT 1'
                ) as cursor:
                    result = await cursor.fetchone()
                    return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса Crypto Pay: {e}")
            return False        

    async def get_crypto_settings(self) -> Optional[Dict]:
        """Получение настроек Crypto Pay"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM crypto_settings WHERE is_enable = 1 LIMIT 1'
                ) as cursor:
                    settings = await cursor.fetchone()
                    if settings:
                        return dict(settings)
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении настроек Crypto Pay: {e}")
            return None

    async def execute_fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Выполнение запроса с получением одной строки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    result = await cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Database error in execute_fetchone: {e}")
            return None

db = Database()
