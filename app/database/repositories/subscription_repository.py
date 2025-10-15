"""
Репозиторий для работы с подписками.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.database.models import Subscription, User, Server, Tariff
from app.database.repositories.base import BaseRepository
from app.database.connection import get_db_session
from app.core.exceptions import DatabaseError
from config.logging import db_logger


class SubscriptionRepository(BaseRepository[Subscription]):
    """Репозиторий для работы с подписками."""

    def __init__(self):
        super().__init__(Subscription)

    async def create_subscription(
        self,
        user_id: int,
        server_id: int,
        tariff_id: int,
        duration_days: int,
        is_trial: bool = False,
        vless_config: str = None,
        client_id: str = None
    ) -> Subscription:
        """Создание новой подписки."""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_days)

            return await self.create(
                user_id=user_id,
                server_id=server_id,
                tariff_id=tariff_id,
                start_date=start_date,
                end_date=end_date,
                is_trial=is_trial,
                vless_config=vless_config,
                client_id=client_id
            )
        except Exception as e:
            db_logger.error(f"Failed to create subscription: {e}")
            raise DatabaseError(f"Create subscription failed: {e}")

    async def get_user_subscriptions(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[Subscription]:
        """Получение подписок пользователя."""
        try:
            async with get_db_session() as session:
                stmt = (
                    select(Subscription)
                    .options(
                        selectinload(Subscription.server),
                        selectinload(Subscription.tariff)
                    )
                    .where(Subscription.user_id == user_id)
                )

                if active_only:
                    stmt = stmt.where(Subscription.is_active == True)

                stmt = stmt.order_by(Subscription.created_at.desc())

                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            db_logger.error(f"Failed to get user subscriptions {user_id}: {e}")
            raise DatabaseError(f"Get user subscriptions failed: {e}")

    async def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """Получение активной подписки пользователя."""
        try:
            async with get_db_session() as session:
                stmt = (
                    select(Subscription)
                    .options(
                        selectinload(Subscription.server),
                        selectinload(Subscription.tariff)
                    )
                    .where(
                        and_(
                            Subscription.user_id == user_id,
                            Subscription.is_active == True,
                            Subscription.end_date > datetime.utcnow()
                        )
                    )
                    .order_by(Subscription.end_date.desc())
                    .limit(1)
                )

                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            db_logger.error(f"Failed to get active subscription for user {user_id}: {e}")
            raise DatabaseError(f"Get active subscription failed: {e}")

    async def get_expiring_subscriptions(
        self,
        hours_before: int = 24
    ) -> List[Subscription]:
        """Получение подписок, которые скоро истекут."""
        try:
            async with get_db_session() as session:
                expiry_threshold = datetime.utcnow() + timedelta(hours=hours_before)

                stmt = (
                    select(Subscription)
                    .options(
                        selectinload(Subscription.user),
                        selectinload(Subscription.server),
                        selectinload(Subscription.tariff)
                    )
                    .where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.end_date <= expiry_threshold,
                            Subscription.end_date > datetime.utcnow()
                        )
                    )
                )

                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            db_logger.error(f"Failed to get expiring subscriptions: {e}")
            raise DatabaseError(f"Get expiring subscriptions failed: {e}")

    async def get_expired_subscriptions(self) -> List[Subscription]:
        """Получение истекших подписок."""
        try:
            async with get_db_session() as session:
                stmt = (
                    select(Subscription)
                    .options(
                        selectinload(Subscription.user),
                        selectinload(Subscription.server)
                    )
                    .where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.end_date <= datetime.utcnow()
                        )
                    )
                )

                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            db_logger.error(f"Failed to get expired subscriptions: {e}")
            raise DatabaseError(f"Get expired subscriptions failed: {e}")

    async def deactivate_subscription(self, subscription_id: int) -> bool:
        """Деактивация подписки."""
        try:
            updated = await self.update(subscription_id, is_active=False)
            return updated is not None
        except Exception as e:
            db_logger.error(f"Failed to deactivate subscription {subscription_id}: {e}")
            return False

    async def extend_subscription(
        self,
        subscription_id: int,
        additional_days: int
    ) -> bool:
        """Продление подписки."""
        try:
            async with get_db_session() as session:
                subscription = await session.get(Subscription, subscription_id)
                if not subscription:
                    return False

                # Если подписка уже истекла, продлеваем от текущего времени
                if subscription.end_date <= datetime.utcnow():
                    new_end_date = datetime.utcnow() + timedelta(days=additional_days)
                else:
                    new_end_date = subscription.end_date + timedelta(days=additional_days)

                subscription.end_date = new_end_date
                subscription.is_active = True

                await session.flush()
                return True
        except Exception as e:
            db_logger.error(f"Failed to extend subscription {subscription_id}: {e}")
            return False

    async def update_traffic_usage(
        self,
        subscription_id: int,
        traffic_used: int
    ) -> bool:
        """Обновление статистики трафика."""
        try:
            updated = await self.update(
                subscription_id,
                traffic_used=traffic_used,
                last_traffic_update=datetime.utcnow()
            )
            return updated is not None
        except Exception as e:
            db_logger.error(f"Failed to update traffic for subscription {subscription_id}: {e}")
            return False

    async def get_subscriptions_stats(self) -> dict:
        """Получение статистики подписок."""
        try:
            async with get_db_session() as session:
                # Общее количество подписок
                total = await session.execute(select(func.count(Subscription.id)))

                # Активные подписки
                active = await session.execute(
                    select(func.count(Subscription.id)).where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.end_date > datetime.utcnow()
                        )
                    )
                )

                # Пробные подписки
                trial = await session.execute(
                    select(func.count(Subscription.id)).where(
                        Subscription.is_trial == True
                    )
                )

                # Истекшие подписки
                expired = await session.execute(
                    select(func.count(Subscription.id)).where(
                        and_(
                            Subscription.is_active == True,
                            Subscription.end_date <= datetime.utcnow()
                        )
                    )
                )

                return {
                    "total": total.scalar(),
                    "active": active.scalar(),
                    "trial": trial.scalar(),
                    "expired": expired.scalar()
                }
        except Exception as e:
            db_logger.error(f"Failed to get subscriptions stats: {e}")
            return {"total": 0, "active": 0, "trial": 0, "expired": 0}
