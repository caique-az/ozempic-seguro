"""
Testes completos para UserService - Cobertura máxima.
"""

import pytest
import uuid

from ozempic_seguro.services.user_service import UserService
from ozempic_seguro.core.exceptions import (
    UserNotFoundError,
    InvalidUserDataError,
    WeakPasswordError,
)


class TestUserServiceGetAllUsers:
    """Testes para get_all_users"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_get_all_users_returns_list(self):
        """Testa que retorna lista"""
        users = self.service.get_all_users()

        assert isinstance(users, list)

    def test_get_all_users_has_admin(self):
        """Testa que tem pelo menos admin"""
        users = self.service.get_all_users()

        assert len(users) >= 1


class TestUserServiceCreateUser:
    """Testes para create_user"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_create_user_valid(self):
        """Testa criação de usuário válido"""
        unique_username = f"test_{uuid.uuid4().hex[:8]}"

        success, msg = self.service.create_user(
            name="Test User",
            username=unique_username,
            password="ValidPass123!",
            user_type="vendedor",
        )

        assert success is True

    def test_create_user_empty_username(self):
        """Testa criação com username vazio"""
        with pytest.raises(InvalidUserDataError):
            self.service.create_user(
                name="Test User", username="", password="ValidPass123!", user_type="vendedor"
            )

    def test_create_user_empty_password(self):
        """Testa criação com senha vazia"""
        with pytest.raises((InvalidUserDataError, WeakPasswordError)):
            self.service.create_user(
                name="Test User",
                username=f"test_{uuid.uuid4().hex[:8]}",
                password="",
                user_type="vendedor",
            )

    def test_create_user_invalid_type(self):
        """Testa criação com tipo inválido"""
        with pytest.raises(InvalidUserDataError):
            self.service.create_user(
                name="Test User",
                username=f"test_{uuid.uuid4().hex[:8]}",
                password="ValidPass123!",
                user_type="invalid_type",
            )


class TestUserServiceDeleteUser:
    """Testes para delete_user"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_delete_user_nonexistent(self):
        """Testa exclusão de usuário inexistente"""
        with pytest.raises(UserNotFoundError):
            self.service.delete_user(99999)


class TestUserServiceUpdatePassword:
    """Testes para update_password"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_update_password_nonexistent(self):
        """Testa atualização de senha para usuário inexistente"""
        with pytest.raises(UserNotFoundError):
            self.service.update_password(99999, "NewPass123!")
