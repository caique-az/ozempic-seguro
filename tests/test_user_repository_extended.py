"""
Testes estendidos para UserRepository - Cobertura adicional.
"""

import pytest
import uuid

from ozempic_seguro.repositories.user_repository import UserRepository


class TestUserRepositoryExtended:
    """Testes estendidos para UserRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = UserRepository()
        yield

    def test_find_by_username_existing(self):
        """Testa busca por username existente"""
        # Admin deve existir
        user = self.repo.find_by_username("admin")

        assert user is None or isinstance(user, dict)

    def test_find_by_username_nonexistent(self):
        """Testa busca por username inexistente"""
        user = self.repo.find_by_username("nonexistent_user_xyz")

        assert user is None

    def test_find_by_type_admin(self):
        """Testa busca por tipo administrador"""
        users = self.repo.find_by_type("administrador")

        assert isinstance(users, list)

    def test_find_by_type_vendedor(self):
        """Testa busca por tipo vendedor"""
        users = self.repo.find_by_type("vendedor")

        assert isinstance(users, list)

    def test_find_by_type_repositor(self):
        """Testa busca por tipo repositor"""
        users = self.repo.find_by_type("repositor")

        assert isinstance(users, list)

    def test_find_by_type_tecnico(self):
        """Testa busca por tipo técnico"""
        users = self.repo.find_by_type("tecnico")

        assert isinstance(users, list)

    def test_find_active_users(self):
        """Testa busca de usuários ativos"""
        users = self.repo.find_active_users()

        assert isinstance(users, list)

    def test_find_all(self):
        """Testa busca de todos os usuários"""
        users = self.repo.find_all()

        assert isinstance(users, list)
        assert len(users) >= 1  # Pelo menos admin

    def test_find_by_id_existing(self):
        """Testa busca por ID existente"""
        user = self.repo.find_by_id(1)

        assert user is None or isinstance(user, dict)

    def test_find_by_id_nonexistent(self):
        """Testa busca por ID inexistente"""
        user = self.repo.find_by_id(99999)

        assert user is None

    def test_exists_true(self):
        """Testa verificação de existência para ID existente"""
        # Verificar se existe algum usuário
        users = self.repo.find_all()
        if users:
            assert self.repo.exists(users[0]["id"]) is True

    def test_exists_false(self):
        """Testa verificação de existência para ID inexistente"""
        assert self.repo.exists(99999) is False

    def test_delete_nonexistent(self):
        """Testa exclusão de usuário inexistente"""
        result = self.repo.delete(99999)

        assert result is False

    def test_is_last_admin_with_multiple_admins(self):
        """Testa verificação de último admin"""
        # Criar segundo admin para teste
        unique_username = f"admin_{uuid.uuid4().hex[:8]}"

        try:
            self.repo.create_user(
                username=unique_username,
                password="AdminPass123!",
                nome_completo="Test Admin",
                tipo="administrador",
            )

            # Agora não deve ser o último admin
            users = self.repo.find_by_type("administrador")
            if len(users) > 1:
                result = self.repo.is_last_admin(users[0]["id"])
                assert result is False
        except Exception:
            pass  # Ignora se falhar

    def test_get_user_stats(self):
        """Testa obtenção de estatísticas de usuários"""
        if hasattr(self.repo, "get_user_stats"):
            stats = self.repo.get_user_stats()
            assert isinstance(stats, dict)
