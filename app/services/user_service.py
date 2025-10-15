"""
Сервис для работы с пользователями.
"""

from typing import Optional, List
from datetime import datetime

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.subscription_repository import SubscriptionRepository
from app.core.security import security_manager
from app.core.cache import cache, cached
from app.core.exceptions import UserNotFoundError, ValidationError
from config.logging import get_logger

logger = get_logger("user_service")


class UserService:
    """Сервис для управления пользователями."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.subscription_repo = SubscriptionRepository()

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        referred_by: str = None
    ) -> dict:
        """Получение или создание пользователя."""
        try:
            # Проверяем существующего пользователя
            user = await self.user_repo.get_by_telegram_id(telegram_id)

            if user:
                # Обновляем последнюю активность
                await self.user_repo.update_last_activity(user.id)

                # Инвалидируем кэш
                await cache.delete(f"user:{telegram_id}")

                logger.info(f"User {telegram_id} found and activity updated")
                return self._user_to_dict(user)

            # Создаем нового пользователя
            referral_code = security_manager.generate_referral_code()

            user = await self.user_repo.create_user(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                referral_code=referral_code
            )

            # Обработка реферала
            if referred_by and referred_by != referral_code:
                await self._process_referral(user.id, referred_by)

            logger.info(f"New user created: {telegram_id}")
            return self._user_to_dict(user)

        except Exception as e:
            logger.error(f"Failed to get or create user {telegram_id}: {e}")
            raise

    @cached(ttl=300, key_prefix="user")
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """Получение пользователя по Telegram ID с кэшированием."""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return None

            return self._user_to_dict(user)
        except Exception as e:
            logger.error(f"Failed to get user by telegram_id {telegram_id}: {e}")
            raise

    async def get_user_profile(self, telegram_id: int) -> dict:
        """Получение полного профиля пользователя."""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

            # Получаем подписки пользователя
            subscriptions = await self.subscription_repo.get_user_subscriptions(user.id)
            active_subscription = await self.subscription_repo.get_active_subscription(user.id)

            # Статистика рефералов
            referral_stats = await self.user_repo.get_referral_stats(user.referral_code)

            profile = self._user_to_dict(user)
            profile.update({
                "subscriptions_count": len(subscriptions),
                "has_active_subscription": active_subscription is not None,
                "active_subscription": self._subscription_to_dict(active_subscription) if active_subscription else None,
                "referral_stats": referral_stats
            })

            return profile
        except Exception as e:
            logger.error(f"Failed to get user profile {telegram_id}: {e}")
            raise

    async def update_user_info(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        email: str = None
    ) -> bool:
        """Обновление информации о пользователе."""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

            update_data = {}
            if username is not None:
                update_data["username"] = username
            if first_name is not None:
                update_data["first_name"] = first_name
            if last_name is not None:
                update_data["last_name"] = last_name
            if email is not None:
                # Здесь можно добавить валидацию email
                update_data["email"] = email

            if update_data:
                await self.user_repo.update(user.id, **update_data)

                # Инвалидируем кэш
                await cache.delete(f"user:{telegram_id}")

                logger.info(f"User {telegram_id} info updated")
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to update user info {telegram_id}: {e}")
            raise

    async def ban_user(self, telegram_id: int, banned: bool = True) -> bool:
        """Блокировка/разблокировка пользователя."""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

            success = await self.user_repo.ban_user(user.id, banned)

            if success:
                # Инвалидируем кэш
                await cache.delete(f"user:{telegram_id}")

                # Если пользователь заблокирован, деактивируем его подписки
                if banned:
                    subscriptions = await self.subscription_repo.get_user_subscriptions(user.id)
                    for subscription in subscriptions:
                        await self.subscription_repo.deactivate_subscription(subscription.id)

                logger.info(f"User {telegram_id} {'banned' if banned else 'unbanned'}")

            return success
        except Exception as e:
            logger.error(f"Failed to ban/unban user {telegram_id}: {e}")
            raise

    async def use_trial(self, telegram_id: int) -> bool:
        """Отметка об использовании пробного периода."""
        try:
            user = await self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                raise UserNotFoundError(f"User with telegram_id {telegram_id} not found")

            if user.trial_used:
                raise ValidationError("User has already used trial period")

            success = await self.user_repo.set_trial_used(user.id)

            if success:
                # Инвалидируем кэш
                await cache.delete(f"user:{telegram_id}")
                logger.info(f"Trial marked as used for user {telegram_id}")

            return success
        except Exception as e:
            logger.error(f"Failed to mark trial as used for user {telegram_id}: {e}")
            raise

    async def get_users_list(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str = None,
        active_only: bool = True
    ) -> List[dict]:
        """Получение списка пользователей для админ панели."""
        try:
            if search:
                users = await self.user_repo.search_users(search, limit, offset)
            else:
                filters = {}
                if active_only:
                    filters.update({"is_active": True, "is_banned": False})

                users = await self.user_repo.get_all(
                    limit=limit,
                    offset=offset,
                    order_by="created_at",
                    filters=filters
                )

            return [self._user_to_dict(user) for user in users]
        except Exception as e:
            logger.error(f"Failed to get users list: {e}")
            raise

    async def get_users_statistics(self) -> dict:
        """Получение статистики пользователей."""
        try:
            return await self.user_repo.get_users_stats()
        except Exception as e:
            logger.error(f"Failed to get users statistics: {e}")
            raise

    async def _process_referral(self, user_id: int, referral_code: str):
        """Обработка реферала."""
        try:
            # Находим пользователя, который пригласил
            referrer = await self.user_repo.get_by_field("referral_code", referral_code)
            if referrer:
                # Увеличиваем счетчик рефералов
                await self.user_repo.update(
                    referrer.id,
                    referral_count=referrer.referral_count + 1
                )

                # Отмечаем у нового пользователя, кто его пригласил
                await self.user_repo.update(
                    user_id,
                    referred_by=referral_code
                )

                logger.info(f"Referral processed: {referral_code} -> user {user_id}")
        except Exception as e:
            logger.error(f"Failed to process referral {referral_code}: {e}")

    def _user_to_dict(self, user) -> dict:
        """Преобразование пользователя в словарь."""
        if not user:
            return None

        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_active": user.is_active,
            "is_banned": user.is_banned,
            "trial_used": user.trial_used,
            "referral_code": user.referral_code,
            "referred_by": user.referred_by,
            "referral_count": user.referral_count,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_activity": user.last_activity.isoformat() if user.last_activity else None
        }

    def _subscription_to_dict(self, subscription) -> dict:
        """Преобразование подписки в словарь."""
        if not subscription:
            return None

        return {
            "id": subscription.id,
            "server_name": subscription.server.name if subscription.server else None,
            "tariff_name": subscription.tariff.name if subscription.tariff else None,
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "is_active": subscription.is_active,
            "is_trial": subscription.is_trial,
            "traffic_used": subscription.traffic_used
        }
