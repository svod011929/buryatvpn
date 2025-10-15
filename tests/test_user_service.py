"""
Тесты сервиса пользователей.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService
from app.core.exceptions import UserNotFoundError


@pytest.mark.asyncio
class TestUserService:
    """Тесты UserService."""

    def setup_method(self):
        self.user_service = UserService()

    @patch('app.services.user_service.UserRepository')
    async def test_get_or_create_user_existing(self, mock_repo):
        """Тест получения существующего пользователя."""
        # Arrange
        mock_user = AsyncMock()
        mock_user.id = 1
        mock_user.telegram_id = 123456789
        mock_user.username = 'testuser'

        mock_repo.return_value.get_by_telegram_id.return_value = mock_user
        mock_repo.return_value.update_last_activity.return_value = True

        # Act
        result = await self.user_service.get_or_create_user(123456789, 'testuser')

        # Assert
        assert result is not None
        mock_repo.return_value.get_by_telegram_id.assert_called_once_with(123456789)
        mock_repo.return_value.update_last_activity.assert_called_once_with(1)

    @patch('app.services.user_service.UserRepository')
    async def test_get_or_create_user_new(self, mock_repo):
        """Тест создания нового пользователя."""
        # Arrange
        mock_repo.return_value.get_by_telegram_id.return_value = None

        mock_new_user = AsyncMock()
        mock_new_user.id = 2
        mock_new_user.telegram_id = 987654321
        mock_new_user.referral_code = 'NEWCODE'

        mock_repo.return_value.create_user.return_value = mock_new_user

        # Act
        result = await self.user_service.get_or_create_user(987654321, 'newuser')

        # Assert
        assert result is not None
        mock_repo.return_value.create_user.assert_called_once()

    @patch('app.services.user_service.UserRepository')
    async def test_get_user_profile_not_found(self, mock_repo):
        """Тест получения профиля несуществующего пользователя."""
        # Arrange
        mock_repo.return_value.get_by_telegram_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await self.user_service.get_user_profile(999999999)

    @patch('app.services.user_service.UserRepository')
    async def test_ban_user_success(self, mock_repo):
        """Тест блокировки пользователя."""
        # Arrange
        mock_user = AsyncMock()
        mock_user.id = 1
        mock_repo.return_value.get_by_telegram_id.return_value = mock_user
        mock_repo.return_value.ban_user.return_value = True

        # Act
        result = await self.user_service.ban_user(123456789, True)

        # Assert
        assert result is True
        mock_repo.return_value.ban_user.assert_called_once_with(1, True)
