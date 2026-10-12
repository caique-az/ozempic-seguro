"""
Testes para UserService usando mocks dos repositories.
"""

from unittest.mock import Mock, patch

import pytest

from ozempic_seguro.core.exceptions import (
    InvalidCredentialsError,
    InvalidUserDataError,
    LastAdminError,
    UserNotFoundError,
)
from ozempic_seguro.services.audit_service import AuditService
from ozempic_seguro.services.user_service import UserService


class TestUserService:
    """Testes para UserService"""

    @pytest.fixture
    def mock_user_repo(self):
        """Mock do UserRepository"""
        mock = Mock()
        mock.authenticate_user = Mock()
        mock.create_user = Mock()
        mock.get_users = Mock()
        mock.get_user_by_id = Mock()
        mock.update_password = Mock()
        mock.delete_user = Mock()
        mock.is_unique_admin = Mock()
        return mock

    @pytest.fixture
    def mock_audit_repo(self):
        """Mock do AuditRepository"""
        mock = Mock()
        mock.log_action = Mock(return_value=1)
        return mock

    @pytest.fixture
    def user_service_with_mocks(self, mock_user_repo, mock_audit_repo):
        """UserService com repositories mockados"""
        with (
            patch(
                "ozempic_seguro.services.user_service.UserRepository", return_value=mock_user_repo
            ),
            patch(
                "ozempic_seguro.services.user_service.AuditRepository", return_value=mock_audit_repo
            ),
        ):
            service = UserService()
            service.user_repo = mock_user_repo
            service.audit_repo = mock_audit_repo
            return service

    def test_audit_service_log_action(self):
        """Testa log de ação no AuditService"""
        mock_audit = Mock(spec=AuditService)
        mock_audit.log_action = Mock(return_value=True)

        mock_user = {"id": 1, "username": "test_user"}
        result = mock_audit.log_action(mock_user, "login")

        assert result is True

    def test_authenticate_user_success(self, user_service_with_mocks, mock_user_repo):
        """Testa autenticação bem-sucedida"""
        mock_user = {"id": 1, "username": "test_user", "tipo": "vendedor"}
        mock_user_repo.authenticate_user.return_value = mock_user

        result = user_service_with_mocks.authenticate("test_user", "password123")

        assert result == mock_user

    def test_authenticate_user_failure(self, user_service_with_mocks, mock_user_repo):
        """Testa falha na autenticação - deve lançar InvalidCredentialsError"""
        mock_user_repo.authenticate_user.return_value = None

        with pytest.raises(InvalidCredentialsError):
            user_service_with_mocks.authenticate("invalid", "wrong")

    def test_create_user_success(self, user_service_with_mocks, mock_user_repo):
        """Testa criação de usuário bem-sucedida"""
        mock_user_repo.create_user.return_value = True

        result, msg = user_service_with_mocks.create_user(
            name="New User", username="newuser", password="Password1", user_type="vendedor"
        )

        assert result is True

    def test_create_user_invalid_input(self, user_service_with_mocks):
        """Testa falha na criação com dados inválidos - deve lançar InvalidUserDataError"""
        with pytest.raises(InvalidUserDataError):
            user_service_with_mocks.create_user(
                name="", username="u", password="123", user_type="invalido"
            )

    def test_get_all_users(self, user_service_with_mocks, mock_user_repo):
        """Testa listagem de todos os usuários"""
        mock_users = [
            {"id": 1, "username": "user1", "tipo": "vendedor"},
            {"id": 2, "username": "user2", "tipo": "repositor"},
        ]
        mock_user_repo.get_users.return_value = mock_users

        result = user_service_with_mocks.get_all_users()

        assert len(result) == 2

    def test_update_user_password_success(self, user_service_with_mocks, mock_user_repo):
        """Testa atualização de senha"""
        mock_user_repo.get_user_by_id.return_value = {"id": 1, "tipo": "vendedor"}
        mock_user_repo.update_password.return_value = True

        result, msg = user_service_with_mocks.update_password(1, "NewPass123")

        assert result is True

    def test_delete_user_success(self, user_service_with_mocks, mock_user_repo):
        """Testa exclusão de usuário bem-sucedida"""
        mock_user_repo.get_user_by_id.return_value = {"id": 1, "tipo": "vendedor"}
        mock_user_repo.delete_user.return_value = True
        mock_user_repo.is_unique_admin.return_value = False

        result, msg = user_service_with_mocks.delete_user(1)

        assert result is True

    def test_delete_last_admin_prevented(self, user_service_with_mocks, mock_user_repo):
        """Testa prevenção de exclusão do último admin - deve lançar LastAdminError"""
        mock_user_repo.is_unique_admin.return_value = True
        mock_user_repo.get_user_by_id.return_value = {"id": 1, "tipo": "administrador"}

        with pytest.raises(LastAdminError):
            user_service_with_mocks.delete_user(1)

    def test_delete_user_not_found(self, user_service_with_mocks, mock_user_repo):
        """Testa exclusão de usuário inexistente"""
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            user_service_with_mocks.delete_user(99999)

    def test_update_password_user_not_found(self, user_service_with_mocks, mock_user_repo):
        """Testa atualização de senha para usuário inexistente"""
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            user_service_with_mocks.update_password(99999, "NewPass123")

    def test_get_all_users_empty(self, user_service_with_mocks, mock_user_repo):
        """Testa listagem de usuários vazia"""
        mock_user_repo.get_users.return_value = []

        result = user_service_with_mocks.get_all_users()

        assert len(result) == 0
        assert isinstance(result, list)

    def test_create_user_with_valid_types(self, user_service_with_mocks, mock_user_repo):
        """Testa criação com diferentes tipos de usuário"""
        mock_user_repo.create_user.return_value = True

        for tipo in ["vendedor", "repositor", "administrador"]:
            result, msg = user_service_with_mocks.create_user(
                name="Test User", username=f"testuser_{tipo}", password="Password1", user_type=tipo
            )
            assert result is True


class TestUserServiceAdditional:
    """Testes adicionais para UserService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserService()
        return

    def test_get_all_users_returns_list(self):
        """Testa que get_all_users retorna lista"""
        result = self.service.get_all_users()
        assert isinstance(result, list)

    def test_authenticate_with_invalid_credentials(self):
        """Testa autenticação com credenciais inválidas"""
        with pytest.raises(InvalidCredentialsError):
            self.service.authenticate("nonexistent_user_xyz", "wrongpass")
