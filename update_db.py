import asyncio
import aiosqlite
from loguru import logger
import os

async def check_column_exists(db, table: str, column: str) -> bool:
    """Проверка существования колонки в таблице"""
    async with db.execute(f"PRAGMA table_info({table})") as cursor:
        columns = await cursor.fetchall()
        return any(col[1] == column for col in columns)

async def update_database():
    """Обновление структуры базы данных"""
    db_path = 'instance/database.db'
    
    if not os.path.exists(db_path):
        logger.error(f"База данных не найдена: {db_path}")
        return
    
    try:
        async with aiosqlite.connect(db_path) as db:
            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='server_settings'
            """)
            if await table_exists.fetchone():
                if not await check_column_exists(db, 'server_settings', 'inbound_id'):
                    logger.info("Добавление колонки 'inbound_id' в таблицу server_settings")
                    await db.execute("""
                        ALTER TABLE server_settings 
                        ADD COLUMN inbound_id INTEGER DEFAULT 1 NOT NULL
                    """)
                    await db.commit()
                    logger.info("Колонка 'inbound_id' успешно добавлена")
            else:
                logger.info("Создание таблицы server_settings")
                await db.execute('''
                    CREATE TABLE server_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        ip TEXT,
                        url TEXT NOT NULL,
                        port TEXT NOT NULL,
                        secret_path TEXT NOT NULL,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        secretkey TEXT,
                        is_enable BOOLEAN NOT NULL DEFAULT 1
                    )
                ''')
                await db.commit()
                logger.info("Таблица server_settings успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bot_message'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы bot_message")
                await db.execute('''
                    CREATE TABLE bot_message (
                        command TEXT PRIMARY KEY,
                        text TEXT NOT NULL,
                        image_path TEXT,
                        is_enable BOOLEAN NOT NULL DEFAULT 1
                    )
                ''')
                await db.commit()
                logger.info("Таблица bot_message успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tariff'
            """)
            if await table_exists.fetchone():
                if not await check_column_exists(db, 'tariff', 'server_id'):
                    logger.info("Добавление колонки 'server_id' в таблицу tariff")
                    await db.execute("""
                        ALTER TABLE tariff 
                        ADD COLUMN server_id INTEGER REFERENCES server_settings(id)
                    """)
                    await db.commit()
                    logger.info("Колонка 'server_id' успешно добавлена")
            else:
                logger.info("Создание таблицы tariff")
                await db.execute('''
                    CREATE TABLE tariff (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        speed REAL NOT NULL,
                        server_id INTEGER,
                        FOREIGN KEY (server_id) REFERENCES server_settings(id)
                    )
                ''')
                await db.commit()
                logger.info("Таблица tariff успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user_subscription'
            """)
            if await table_exists.fetchone():
                if not await check_column_exists(db, 'user_subscription', 'vless'):
                    logger.info("Добавление колонки 'vless' в таблицу user_subscription")
                    await db.execute("""
                        ALTER TABLE user_subscription 
                        ADD COLUMN vless TEXT
                    """)
                    await db.commit()
                    logger.info("Колонка 'vless' успешно добавлена")
            else:
                logger.info("Создание таблицы user_subscription")
                await db.execute('''
                    CREATE TABLE user_subscription (
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
                await db.commit()
                logger.info("Таблица user_subscription успешно создана")

            if not await check_column_exists(db, 'user_subscription', 'payment_id'):
                logger.info("Добавление колонки 'payment_id' в таблицу user_subscription")
                await db.execute("""
                    ALTER TABLE user_subscription 
                    ADD COLUMN payment_id TEXT
                """)
                await db.commit()
                logger.info("Колонка 'payment_id' успешно добавлена")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='yookassa_settings'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы yookassa_settings")
                await db.execute('''
                    CREATE TABLE yookassa_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        shop_id TEXT NOT NULL,
                        api_key TEXT NOT NULL,
                        description TEXT,
                        is_enable INTEGER DEFAULT 0
                    )
                ''')
                await db.commit()
                logger.info("Таблица yookassa_settings успешно создана")

                await db.execute('''
                    INSERT INTO yookassa_settings (name, shop_id, api_key, description, is_enable)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('Test Shop', 'test_shop_id', 'test_api_key', 'Тестовые настройки YooKassa', 0))
                await db.commit()
                logger.info("Добавлены тестовые настройки YooKassa")

            cursor = await db.execute('SELECT COUNT(*) FROM tariff')
            tariff_count = await cursor.fetchone()
            if tariff_count[0] == 0:
                logger.info("Добавление тестового тарифа")
                cursor = await db.execute('SELECT id FROM server_settings WHERE is_enable = 1 LIMIT 1')
                server = await cursor.fetchone()
                if server:
                    server_id = server[0]
                    await db.execute('''
                        INSERT INTO tariff (name, price, left_day, is_enable, server_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('Базовый', 10.0, 3, 1, server_id))
                    await db.commit()
                    logger.info("Тестовый тариф успешно добавлен")

            async with db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='promocodes'
            """) as cursor:
                if not await cursor.fetchone():
                    await db.execute('''
                        CREATE TABLE promocodes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            promocod TEXT NOT NULL,
                            activation_limit INTEGER DEFAULT 1,
                            activation_total INTEGER DEFAULT 0,
                            percentage DECIMAL(5,2) NOT NULL,
                            is_enable BOOLEAN NOT NULL DEFAULT 1,
                            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    await db.commit()
                    logger.info("Таблица promocodes успешно создана")
                else:
                    logger.info("Таблица promocodes уже существует")

            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tariff_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (tariff_id) REFERENCES tariff (id)
                )
            """)
            await db.commit()
            
            if not await check_column_exists(db, 'server_settings', 'inbound_id_promo'):
                logger.info("Добавление колонки 'inbound_id_promo' в таблицу server_settings")
                await db.execute("""
                    ALTER TABLE server_settings 
                    ADD COLUMN inbound_id_promo INTEGER DEFAULT 2
                """)
                await db.commit()
                logger.info("Колонка 'inbound_id_promo' успешно добавлена")

            await db.execute("""
                CREATE TABLE IF NOT EXISTS tariff_promo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    left_day INTEGER NOT NULL,
                    server_id INTEGER,
                    is_enable BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (server_id) REFERENCES server_settings(id)
                )
            """)
            await db.commit()
            logger.info("Таблица tariff_promo успешно создана или уже существует")
            
            if not await check_column_exists(db, 'bot_settings', 'reg_notify'):
                logger.info("Добавление столбца 'reg_notify' в таблицу bot_settings")
                await db.execute("""
                    ALTER TABLE bot_settings 
                    ADD COLUMN reg_notify INTEGER DEFAULT 0
                """)
                await db.commit()
                logger.info("Столбец 'reg_notify' успешно добавлен")

            if not await check_column_exists(db, 'bot_settings', 'pay_notify'):
                logger.info("Добавление столбца 'pay_notify' в таблицу bot_settings")
                await db.execute("""
                    ALTER TABLE bot_settings 
                    ADD COLUMN pay_notify INTEGER DEFAULT 0
                """)
                await db.commit()
                logger.info("Столбец 'pay_notify' успешно добавлен")

            await db.execute("""
                CREATE TABLE IF NOT EXISTS Reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("Таблица Reviews успешно создана или уже существует")
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS support_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    bot_version TEXT NOT NULL,
                    support_url TEXT NOT NULL
                )
            """)
            await db.commit()
            logger.info("Таблица support_info успешно создана или уже существует")

            cursor = await db.execute('SELECT COUNT(*) FROM support_info')
            support_info_count = await cursor.fetchone()
            if support_info_count[0] == 0:
                logger.info("Добавление начальной информации о поддержке")
                await db.execute('''
                    INSERT INTO support_info (message, bot_version, support_url)
                    VALUES (?, ?, ?)
                ''', ('Подробное описание бота и прием заявок Вы можете найти на сайте', '1.0.3', 'https://webshop.syslab.space/'))
                await db.commit()
                logger.info("Информация о поддержке успешно добавлена")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user'
            """)
            if await table_exists.fetchone():
                if not await check_column_exists(db, 'user', 'referral_code'):
                    logger.info("Добавление колонок для реферальной системы в таблицу user")
                    await db.execute('''
                        CREATE TABLE user_new (
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
                    
                    await db.execute('''
                        INSERT INTO user_new (id, username, telegram_id, trial_period, is_enable, date)
                        SELECT id, username, telegram_id, trial_period, is_enable, date FROM user
                    ''')
                    
                    await db.execute('DROP TABLE user')
                    await db.execute('ALTER TABLE user_new RENAME TO user')
                    
                    await db.commit()
                    logger.info("Колонки для реферальной системы успешно добавлены")
                
                if not await check_column_exists(db, 'user', 'referral_count'):
                    logger.info("Добавление колонки 'referral_count' в таблицу user")
                    await db.execute("ALTER TABLE user ADD COLUMN referral_count INTEGER DEFAULT 0")
                    await db.commit()
                    logger.info("Колонка 'referral_count' успешно добавлена")

                if not await check_column_exists(db, 'user', 'referred_by'):
                    logger.info("Добавление колонки 'referred_by' в таблицу user")
                    await db.execute("ALTER TABLE user ADD COLUMN referred_by TEXT")
                    await db.commit()
                    logger.info("Колонка 'referred_by' успешно добавлена")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='notify_settings'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы notify_settings")
                await db.execute('''
                    CREATE TABLE notify_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        interval INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        is_enable BOOLEAN NOT NULL DEFAULT 1
                    )
                ''')
                await db.commit()
                logger.info("Таблица notify_settings успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='payments_code'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы payments_code")
                await db.execute('''
                    CREATE TABLE payments_code (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pay_code TEXT UNIQUE NOT NULL,
                        sum DECIMAL(10,2) NOT NULL,
                        is_enable BOOLEAN NOT NULL DEFAULT 1,
                        create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                await db.commit()
                logger.info("Таблица payments_code успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='crypto_settings'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы crypto_settings")
                await db.execute('''
                    CREATE TABLE crypto_settings (
                        api_token TEXT NOT NULL,
                        is_enable BOOLEAN DEFAULT 0,
                        min_amount DECIMAL(10,2) DEFAULT 1.00,
                        supported_assets TEXT,
                        webhook_url TEXT,
                        webhook_secret TEXT
                    )
                ''')
                await db.commit()
                logger.info("Таблица crypto_settings успешно создана")

            table_exists = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='crypto_payments'
            """)
            if not await table_exists.fetchone():
                logger.info("Создание таблицы crypto_payments")
                await db.execute('''
                    CREATE TABLE crypto_payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        tariff_id INTEGER NOT NULL,
                        invoice_id TEXT NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        asset TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id),
                        FOREIGN KEY (tariff_id) REFERENCES tariff (id)
                    )
                ''')
                await db.commit()
                logger.info("Таблица crypto_payments успешно создана")

            logger.info("Обновление базы данных завершено успешно")
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении базы данных: {e}")
        raise

if __name__ == "__main__":
    os.makedirs('logs', exist_ok=True)
    logger.add("logs/update_db.log", rotation="1 day", compression="zip", 
               encoding="utf-8", format="{time} | {level} | {message}")
    
    os.makedirs('instance', exist_ok=True)
    
    asyncio.run(update_database())
