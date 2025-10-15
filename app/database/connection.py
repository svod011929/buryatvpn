"""
Управление подключениями к базе данных.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy import text

from config.settings import settings
from config.logging import db_logger
from app.database.models import Base
from app.core.exceptions import DatabaseError

# Глобальные переменные для движка и фабрики сессий
engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker] = None


async def init_database():
    """Инициализация базы данных."""
    global engine, SessionLocal

    try:
        # Создание движка
        engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,  # Проверка соединений
            pool_recycle=3600,   # Пересоздание соединений каждый час
        )

        # Создание фабрики сессий
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Создание таблиц
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Проверка соединения
        await test_connection()

        db_logger.info("Database initialized successfully")

    except Exception as e:
        db_logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(f"Database initialization failed: {e}")


async def test_connection():
    """Тестирование соединения с базой данных."""
    if not engine:
        raise DatabaseError("Database engine not initialized")

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_logger.info("Database connection test successful")
    except Exception as e:
        db_logger.error(f"Database connection test failed: {e}")
        raise DatabaseError(f"Database connection test failed: {e}")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных с автоматическим управлением транзакциями."""
    if not SessionLocal:
        raise DatabaseError("Database not initialized")

    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        db_logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()


class DatabaseManager:
    """Менеджер базы данных для выполнения операций."""

    @staticmethod
    async def execute_query(query: str, params: dict = None) -> list:
        """Выполнение произвольного SQL запроса."""
        async with get_db_session() as session:
            result = await session.execute(text(query), params or {})
            return result.fetchall()

    @staticmethod
    async def get_db_info() -> dict:
        """Получение информации о базе данных."""
        try:
            async with get_db_session() as session:
                # Получение версии SQLite или PostgreSQL
                if "sqlite" in settings.database.url:
                    result = await session.execute(text("SELECT sqlite_version()"))
                    version = result.scalar()
                    db_type = "SQLite"
                elif "postgresql" in settings.database.url:
                    result = await session.execute(text("SELECT version()"))
                    version = result.scalar()
                    db_type = "PostgreSQL"
                else:
                    version = "Unknown"
                    db_type = "Unknown"

                # Подсчет записей в основных таблицах
                users_count = await session.execute(text("SELECT COUNT(*) FROM users"))
                subscriptions_count = await session.execute(text("SELECT COUNT(*) FROM subscriptions"))
                payments_count = await session.execute(text("SELECT COUNT(*) FROM payments"))

                return {
                    "type": db_type,
                    "version": version,
                    "url": settings.database.url.split("@")[-1] if "@" in settings.database.url else settings.database.url,
                    "tables": {
                        "users": users_count.scalar(),
                        "subscriptions": subscriptions_count.scalar(),
                        "payments": payments_count.scalar(),
                    }
                }
        except Exception as e:
            db_logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}

    @staticmethod
    async def backup_database(backup_path: str = None) -> str:
        """Создание резервной копии базы данных."""
        if "sqlite" not in settings.database.url:
            raise DatabaseError("Backup currently supports only SQLite databases")

        import shutil
        from datetime import datetime
        from pathlib import Path

        try:
            # Определение пути к базе данных
            db_path = settings.database.url.replace("sqlite:///", "")

            # Определение пути для резервной копии
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"database_backup_{timestamp}.db"

            # Создание копии
            shutil.copy2(db_path, backup_path)

            db_logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            db_logger.error(f"Failed to create database backup: {e}")
            raise DatabaseError(f"Backup failed: {e}")


async def close_database():
    """Закрытие соединений с базой данных."""
    global engine, SessionLocal

    if engine:
        await engine.dispose()
        engine = None
        SessionLocal = None
        db_logger.info("Database connections closed")


# Утилиты для миграций
async def run_migrations():
    """Запуск миграций базы данных."""
    # Здесь будет интеграция с Alembic при необходимости
    pass


# Экземпляр менеджера базы данных
db_manager = DatabaseManager()
