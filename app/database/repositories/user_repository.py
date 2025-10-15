"""
Репозиторий для работы с пользователями.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.database.models import User, Subscription
from app.database.repositories.base import BaseRepository
from app.database.connection import get_db_session
from app.core.exceptions import DatabaseError
from config.logging import db_logger


class UserRepository(BaseRepository[User]):
    """Репозиторий для работе с пользователями."""

    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID."""
        try:
            async with get_db_session() as session:
                stmt = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            db_logger.error(f"Failed to get user by telegram_id {telegram_id}: {e}")
            raise DatabaseError(f"Get user by telegram_id failed: {e}")

    async def create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        referral_code: str = None
    ) -> User:
        """Создание нового пользователя."""
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = await self.get_by_telegram_id(telegram_id)
            if existing_user:
                return existing_user

            return await self.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                referral_code=referral_code
            )
        except Exception as e:
            db_logger.error(f"Failed to create user {telegram_id}: {e}")
            raise DatabaseError(f"Create user failed: {e}")

    async def get_with_subscriptions(self, user_id: int) -> Optional[User]:
        """Получение пользователя с подписками."""
        try:
            async with get_db_session() as session:
                stmt = (
                    select(User)
                    .options(selectinload(User.subscriptions))
                    .where(User.id == user_id)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            db_logger.error(f"Failed to get user with subscriptions {user_id}: {e}")
            raise DatabaseError(f"Get user with subscriptions failed: {e}")

    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получение активных пользователей."""
        return await self.get_all(
            limit=limit,
            offset=offset,
            filters={"is_active": True, "is_banned": False}
        )

    async def search_users(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """Поиск пользователей по имени/username."""
        try:
            async with get_db_session() as session:
                stmt = (
                    select(User)
                    .where(
                        or_(
                            User.username.ilike(f"%{query}%"),
                            User.first_name.ilike(f"%{query}%"),
                            User.last_name.ilike(f"%{query}%")
                        )
                    )
                    .limit(limit)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            db_logger.error(f"Failed to search users with query '{query}': {e}")
            raise DatabaseError(f"Search users failed: {e}")

    async def update_last_activity(self, user_id: int) -> bool:
        """Обновление времени последней активности."""
        try:
            updated_user = await self.update(user_id, last_activity=datetime.utcnow())
            return updated_user is not None
        except Exception as e:
            db_logger.error(f"Failed to update last activity for user {user_id}: {e}")
            return False

    async def ban_user(self, user_id: int, banned: bool = True) -> bool:
        """Блокировка/разблокировка пользователя."""
        try:
            updated_user = await self.update(user_id, is_banned=banned)
            return updated_user is not None
        except Exception as e:
            db_logger.error(f"Failed to ban/unban user {user_id}: {e}")
            return False

    async def set_trial_used(self, user_id: int) -> bool:
        """Отметка об использовании пробного периода."""
        try:
            updated_user = await self.update(user_id, trial_used=True)
            return updated_user is not None
        except Exception as e:
            db_logger.error(f"Failed to set trial used for user {user_id}: {e}")
            return False

    async def get_referral_stats(self, referral_code: str) -> dict:
        """Получение статистики по рефералам."""
        try:
            async with get_db_session() as session:
                # Количество привлеченных пользователей
                referred_count = await session.execute(
                    select(func.count(User.id)).where(User.referred_by == referral_code)
                )

                # Количество активных рефералов
                active_referred = await session.execute(
                    select(func.count(User.id)).where(
                        and_(
                            User.referred_by == referral_code,
                            User.is_active == True,
                            User.is_banned == False
                        )
                    )
                )

                return {
                    "total_referred": referred_count.scalar(),
                    "active_referred": active_referred.scalar()
                }
        except Exception as e:
            db_logger.error(f"Failed to get referral stats for {referral_code}: {e}")
            return {"total_referred": 0, "active_referred": 0}

    async def get_users_stats(self) -> dict:
        """Получение общей статистики пользователей."""
        try:
            async with get_db_session() as session:
                # Общее количество пользователей
                total_users = await session.execute(select(func.count(User.id)))

                # Активные пользователи
                active_users = await session.execute(
                    select(func.count(User.id)).where(
                        and_(User.is_active == True, User.is_banned == False)
                    )
                )

                # Заблокированные пользователи
                banned_users = await session.execute(
                    select(func.count(User.id)).where(User.is_banned == True)
                )

                # Новые пользователи за последние 30 дней
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                new_users = await session.execute(
                    select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
                )

                return {
                    "total": total_users.scalar(),
                    "active": active_users.scalar(),
                    "banned": banned_users.scalar(),
                    "new_last_30_days": new_users.scalar()
                }
        except Exception as e:
            db_logger.error(f"Failed to get users stats: {e}")
            return {"total": 0, "active": 0, "banned": 0, "new_last_30_days": 0}
