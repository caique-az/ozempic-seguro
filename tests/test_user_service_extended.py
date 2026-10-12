"""
Testes estendidos para UserService - Cobertura adicional.
"""

import pytest

from ozempic_seguro.services.user_service import UserService
from ozempic_seguro.core.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    WeakPasswordError,
    InvalidUserDataError,
)


class TestUserServiceAuthentication:
    """Testes de autenticação"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_authenticate_invalid_password(self):
        """Testa autenticação com senha inválida"""
        with pytest.raises(InvalidCredentialsError):
            self.service.authenticate("admin", "wrongpassword")

    def test_authenticate_nonexistent_user(self):
        """Testa autenticação de usuário inexistente"""
        with pytest.raises(InvalidCredentialsError):
            self.service.authenticate("nonexistent_user_xyz", "password")


class TestUserServiceCRUD:
    """Testes de CRUD de usuários"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_get_all_users(self):
        """Testa listagem de todos os usuários"""
        users = self.service.get_all_users()

        assert isinstance(users, list)
        assert len(users) >= 1  # Pelo menos admin

    def test_get_user_via_repository(self):
        """Testa busca de usuário via repository"""
        from ozempic_seguro.repositories.user_repository import UserRepository

        repo = UserRepository()

        user = repo.find_by_id(1)

        # Pode existir ou não
        assert user is None or isinstance(user, dict)


class TestUserServiceValidation:
    """Testes de validação"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_create_user_invalid_data(self):
        """Testa criação com dados inválidos"""
        with pytest.raises(InvalidUserDataError):
            self.service.create_user(
                name="",  # Nome vazio
                username="",  # Username vazio
                password="",  # Senha vazia
                user_type="invalid",  # Tipo inválido
            )

    def test_create_user_weak_password(self):
        """Testa criação com senha fraca"""
        with pytest.raises((InvalidUserDataError, WeakPasswordError)):
            self.service.create_user(
                name="Test User",
                username="testuser_weak",
                password="123",  # Senha muito curta
                user_type="vendedor",
            )

    def test_create_user_valid(self):
        """Testa criação de usuário válido"""
        import uuid

        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"

        # Criação deve funcionar
        success, msg = self.service.create_user(
            name="Test User Valid",
            username=unique_username,
            password="ValidPass123!",
            user_type="vendedor",
        )

        assert success is True
        assert "sucesso" in msg.lower()


class TestUserServicePasswordManagement:
    """Testes de gerenciamento de senha"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        yield

    def test_update_password_nonexistent_user(self):
        """Testa atualização de senha para usuário inexistente"""
        with pytest.raises(UserNotFoundError):
            self.service.update_password(99999, "NewPassword123")

    def test_validate_password_strength(self):
        """Testa validação de força de senha"""
        # Senha forte
        from ozempic_seguro.core.validators import Validators

        result = Validators.validate_password("StrongPass123!")
        assert result.is_valid is True

        # Senha fraca
        result = Validators.validate_password("123")
        assert result.is_valid is False
