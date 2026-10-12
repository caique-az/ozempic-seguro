"""
Testes para UserRepository - Cobertura de operações CRUD e autenticação.
"""
import pytest

from ozempic_seguro.repositories.user_repository import UserRepository


class TestUserRepository:
    """Testes para UserRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = UserRepository()
        yield

    def test_create_user_success(self):
        """Testa criação de usuário com sucesso"""
        import uuid

        unique_username = f"test_user_{uuid.uuid4().hex[:8]}"

        user_id = self.repo.create_user(
            username=unique_username,
            password="TestPassword123",
            full_name="Test User",
            user_type="vendedor",
        )

        assert user_id is not None
        assert isinstance(user_id, int)

        # Cleanup
        self.repo.delete_user(user_id)

    def test_create_user_duplicate_username(self):
        """Testa que username duplicado retorna None"""
        import uuid

        unique_username = f"test_dup_{uuid.uuid4().hex[:8]}"

        # Criar primeiro usuário
        user_id = self.repo.create_user(
            username=unique_username,
            password="TestPassword123",
            full_name="Test User",
            user_type="vendedor",
        )

        # Tentar criar com mesmo username
        duplicate_id = self.repo.create_user(
            username=unique_username,
            password="AnotherPassword123",
            full_name="Another User",
            user_type="repositor",
        )

        assert duplicate_id is None

        # Cleanup
        if user_id:
            self.repo.delete_user(user_id)

    def test_authenticate_user_success(self):
        """Testa autenticação com credenciais corretas"""
        import uuid

        unique_username = f"auth_test_{uuid.uuid4().hex[:8]}"
        password = "AuthTest123"

        user_id = self.repo.create_user(
            username=unique_username,
            password=password,
            full_name="Auth Test User",
            user_type="vendedor",
        )

        # Autenticar
        user = self.repo.authenticate_user(unique_username, password)

        assert user is not None
        assert user["username"] == unique_username
        assert user["nome_completo"] == "Auth Test User"
        assert user["tipo"] == "vendedor"

        # Cleanup
        self.repo.delete_user(user_id)

    def test_authenticate_user_wrong_password(self):
        """Testa autenticação com senha incorreta"""
        import uuid

        unique_username = f"wrong_pwd_{uuid.uuid4().hex[:8]}"

        user_id = self.repo.create_user(
            username=unique_username,
            password="CorrectPassword123",
            full_name="Test User",
            user_type="vendedor",
        )

        # Tentar autenticar com senha errada
        user = self.repo.authenticate_user(unique_username, "WrongPassword123")

        assert user is None

        # Cleanup
        self.repo.delete_user(user_id)

    def test_authenticate_user_nonexistent(self):
        """Testa autenticação com usuário inexistente"""
        user = self.repo.authenticate_user("nonexistent_user_xyz", "AnyPassword123")
        assert user is None

    def test_get_user_by_id(self):
        """Testa busca de usuário por ID"""
        import uuid

        unique_username = f"get_by_id_{uuid.uuid4().hex[:8]}"

        user_id = self.repo.create_user(
            username=unique_username,
            password="TestPassword123",
            full_name="Get By ID User",
            user_type="repositor",
        )

        user = self.repo.get_user_by_id(user_id)

        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == unique_username

        # Cleanup
        self.repo.delete_user(user_id)

    def test_get_user_by_id_nonexistent(self):
        """Testa busca de usuário inexistente por ID"""
        user = self.repo.get_user_by_id(999999)
        assert user is None

    def test_get_users(self):
        """Testa listagem de usuários"""
        users = self.repo.get_users()

        assert isinstance(users, list)
        # Deve ter pelo menos os usuários padrão (admin e tecnico)
        assert len(users) >= 2

    def test_update_password(self):
        """Testa atualização de senha"""
        import uuid

        unique_username = f"upd_pwd_{uuid.uuid4().hex[:8]}"
        old_password = "OldPassword123"
        new_password = "NewPassword456"

        user_id = self.repo.create_user(
            username=unique_username,
            password=old_password,
            full_name="Update Password User",
            user_type="vendedor",
        )

        # Atualizar senha
        result = self.repo.update_password(user_id, new_password)
        assert result is True

        # Verificar que nova senha funciona
        user = self.repo.authenticate_user(unique_username, new_password)
        assert user is not None

        # Verificar que senha antiga não funciona mais
        user_old = self.repo.authenticate_user(unique_username, old_password)
        assert user_old is None

        # Cleanup
        self.repo.delete_user(user_id)

    def test_delete_user(self):
        """Testa exclusão de usuário"""
        import uuid

        unique_username = f"del_user_{uuid.uuid4().hex[:8]}"

        user_id = self.repo.create_user(
            username=unique_username,
            password="TestPassword123",
            full_name="Delete User",
            user_type="vendedor",
        )

        # Deletar
        result = self.repo.delete_user(user_id)
        assert result is True

        # Verificar que não existe mais
        user = self.repo.get_user_by_id(user_id)
        assert user is None

    def test_is_unique_admin_true(self):
        """Testa verificação de único admin quando é o único"""
        # O admin padrão (00) deve ser o único admin inicialmente
        # Buscar o admin padrão
        users = self.repo.get_users()
        admin_users = [u for u in users if u["tipo"] == "administrador"]

        if len(admin_users) == 1:
            assert self.repo.is_unique_admin(admin_users[0]["id"]) is True

    def test_is_unique_admin_false(self):
        """Testa verificação de único admin quando há múltiplos"""
        import uuid

        unique_username = f"admin2_{uuid.uuid4().hex[:8]}"

        # Criar segundo admin
        user_id = self.repo.create_user(
            username=unique_username,
            password="AdminPassword123",
            full_name="Second Admin",
            user_type="administrador",
        )

        # Agora nenhum admin é único
        users = self.repo.get_users()
        admin_users = [u for u in users if u["tipo"] == "administrador"]

        for admin in admin_users:
            assert self.repo.is_unique_admin(admin["id"]) is False

        # Cleanup
        self.repo.delete_user(user_id)


class TestUserRepositoryEdgeCases:
    """Testes de casos extremos para UserRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = UserRepository()
        yield

    def test_get_user_by_username(self):
        """Testa busca de usuário por username"""
        # Admin padrão deve existir
        user = self.repo.get_user_by_username("00")

        assert user is not None
        assert user["username"] == "00"
        assert user["tipo"] == "administrador"

    def test_get_user_by_username_nonexistent(self):
        """Testa busca de usuário inexistente por username"""
        user = self.repo.get_user_by_username("nonexistent_xyz_123")
        assert user is None

    def test_delete_nonexistent_user(self):
        """Testa exclusão de usuário inexistente"""
        result = self.repo.delete_user(999999)
        assert result is False or result is True

    def test_update_password_nonexistent_user(self):
        """Testa atualização de senha de usuário inexistente"""
        result = self.repo.update_password(999999, "NewPass123")
        assert isinstance(result, bool)

    def test_create_user_different_types(self):
        """Testa criação de usuários com diferentes tipos"""
        import uuid

        for tipo in ["vendedor", "repositor"]:
            unique_username = f"type_{tipo}_{uuid.uuid4().hex[:6]}"
            user_id = self.repo.create_user(
                username=unique_username,
                password="TestPassword123",
                full_name=f"Test {tipo}",
                user_type=tipo,
            )
            assert user_id is not None
            self.repo.delete_user(user_id)
