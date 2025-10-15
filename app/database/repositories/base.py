"""
Базовый репозиторий для работы с данными.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import get_db_session
from app.database.models import Base
from app.core.exceptions import DatabaseError
from config.logging import db_logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для CRUD операций."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, **kwargs) -> ModelType:
        """Создание новой записи."""
        try:
            async with get_db_session() as session:
                instance = self.model(**kwargs)
                session.add(instance)
                await session.flush()
                await session.refresh(instance)
                return instance
        except Exception as e:
            db_logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise DatabaseError(f"Create operation failed: {e}")

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получение записи по ID."""
        try:
            async with get_db_session() as session:
                result = await session.get(self.model, id)
                return result
        except Exception as e:
            db_logger.error(f"Failed to get {self.model.__name__} by id {id}: {e}")
            raise DatabaseError(f"Get by ID operation failed: {e}")

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Получение записи по полю."""
        try:
            async with get_db_session() as session:
                stmt = select(self.model).where(getattr(self.model, field_name) == value)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            db_logger.error(f"Failed to get {self.model.__name__} by {field_name}: {e}")
            raise DatabaseError(f"Get by field operation failed: {e}")

    async def get_all(
        self, 
        limit: int = 100, 
        offset: int = 0,
        order_by: str = "id",
        filters: Dict[str, Any] = None
    ) -> List[ModelType]:
        """Получение всех записей с фильтрацией и пагинацией."""
        try:
            async with get_db_session() as session:
                stmt = select(self.model)

                # Применяем фильтры
                if filters:
                    for field, value in filters.items():
                        if hasattr(self.model, field):
                            stmt = stmt.where(getattr(self.model, field) == value)

                # Сортировка
                if hasattr(self.model, order_by):
                    stmt = stmt.order_by(getattr(self.model, order_by))

                # Пагинация
                stmt = stmt.limit(limit).offset(offset)

                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            db_logger.error(f"Failed to get all {self.model.__name__}: {e}")
            raise DatabaseError(f"Get all operation failed: {e}")

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Обновление записи."""
        try:
            async with get_db_session() as session:
                stmt = update(self.model).where(self.model.id == id).values(**kwargs)
                await session.execute(stmt)

                # Получаем обновленную запись
                updated = await session.get(self.model, id)
                return updated
        except Exception as e:
            db_logger.error(f"Failed to update {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Update operation failed: {e}")

    async def delete(self, id: int) -> bool:
        """Удаление записи."""
        try:
            async with get_db_session() as session:
                stmt = delete(self.model).where(self.model.id == id)
                result = await session.execute(stmt)
                return result.rowcount > 0
        except Exception as e:
            db_logger.error(f"Failed to delete {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Delete operation failed: {e}")

    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Подсчет количества записей."""
        try:
            async with get_db_session() as session:
                stmt = select(func.count(self.model.id))

                # Применяем фильтры
                if filters:
                    for field, value in filters.items():
                        if hasattr(self.model, field):
                            stmt = stmt.where(getattr(self.model, field) == value)

                result = await session.execute(stmt)
                return result.scalar()
        except Exception as e:
            db_logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise DatabaseError(f"Count operation failed: {e}")

    async def exists(self, **kwargs) -> bool:
        """Проверка существования записи."""
        try:
            async with get_db_session() as session:
                stmt = select(self.model)

                for field, value in kwargs.items():
                    if hasattr(self.model, field):
                        stmt = stmt.where(getattr(self.model, field) == value)

                stmt = stmt.limit(1)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except Exception as e:
            db_logger.error(f"Failed to check existence for {self.model.__name__}: {e}")
            raise DatabaseError(f"Exists operation failed: {e}")
