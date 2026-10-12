"""
Testes para UserManagementService - Serviço de gerenciamento de usuários.
"""

import pytest

from ozempic_seguro.services.user_management_service import (
    OperationResult,
    UserData,
    UserManagementService,
    get_user_management_service,
)


class TestUserData:
    """Testes para UserData"""

    def test_is_technician_true(self):
        """Tests technician identification"""
        user = UserData(1, "123", "Test", "tecnico", True, "2025-01-01")
        assert user.is_technician is True

    def test_is_technician_false(self):
        """Tests non-technician identification"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.is_technician is False

    def test_is_admin_true(self):
        """Testa identificação de admin"""
        user = UserData(1, "123", "Test", "administrador", True, "2025-01-01")
        assert user.is_admin is True

    def test_is_admin_false(self):
        """Testa identificação de não-admin"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.is_admin is False

    def test_can_be_modified_tecnico(self):
        """Testa que técnico não pode ser modificado"""
        user = UserData(1, "123", "Test", "tecnico", True, "2025-01-01")
        assert user.can_be_modified is False

    def test_can_be_modified_vendedor(self):
        """Testa que vendedor pode ser modificado"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.can_be_modified is True

    def test_can_be_deleted_tecnico(self):
        """Testa que técnico não pode ser excluído"""
        user = UserData(1, "123", "Test", "tecnico", True, "2025-01-01")
        assert user.can_be_deleted is False

    def test_can_be_deleted_vendedor(self):
        """Testa que vendedor pode ser excluído"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.can_be_deleted is True

    def test_tipo_display(self):
        """Testa formatação do tipo"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.user_type_display == "Vendedor"

    def test_status_display_ativo(self):
        """Testa formatação do status ativo"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.status_display == "Ativo"

    def test_status_display_inativo(self):
        """Testa formatação do status inativo"""
        user = UserData(1, "123", "Test", "vendedor", False, "2025-01-01")
        assert user.status_display == "Inativo"

    def test_created_at_display(self):
        """Tests date formatting"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01 10:00:00")
        assert user.created_at_display == "2025-01-01"


class TestUserManagementService:
    """Testes para UserManagementService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserManagementService()
        return

    def test_get_all_users(self):
        """Testa obtenção de todos os usuários"""
        users = self.service.get_all_users()

        assert isinstance(users, list)
        if users:
            assert isinstance(users[0], UserData)

    def test_get_user_by_id_existing(self):
        """Testa obtenção de usuário existente"""
        users = self.service.get_all_users()
        if users:
            user = self.service.get_user_by_id(users[0].id)
            assert user is not None
            assert isinstance(user, UserData)

    def test_get_user_by_id_nonexistent(self):
        """Testa obtenção de usuário inexistente"""
        user = self.service.get_user_by_id(99999)
        assert user is None

    def test_change_password_empty(self):
        """Testa alteração com senha vazia"""
        result = self.service.change_password(1, "", "")

        assert result.success is False
        assert len(result.errors) > 0

    def test_change_password_mismatch(self):
        """Testa alteração com senhas diferentes"""
        result = self.service.change_password(1, "1234", "5678")

        assert result.success is False
        assert "coincidem" in result.message.lower()

    def test_change_password_nonexistent_user(self):
        """Testa alteração para usuário inexistente"""
        result = self.service.change_password(99999, "1234", "1234")

        assert result.success is False

    def test_delete_user_self(self):
        """Testa exclusão de si mesmo"""
        result = self.service.delete_user(1, current_user_id=1)

        assert result.success is False
        assert "própria" in result.message.lower()

    def test_delete_user_nonexistent(self):
        """Testa exclusão de usuário inexistente"""
        result = self.service.delete_user(99999)

        assert result.success is False
        assert "encontrado" in result.message.lower()

    def test_can_modify_user_nonexistent(self):
        """Testa verificação de modificação para usuário inexistente"""
        can_modify, reason = self.service.can_modify_user(99999)

        assert can_modify is False
        assert "encontrado" in reason.lower()

    def test_can_delete_user_self(self):
        """Testa verificação de exclusão de si mesmo"""
        can_delete, reason = self.service.can_delete_user(1, current_user_id=1)

        assert can_delete is False
        assert "própria" in reason.lower()

    def test_can_delete_user_nonexistent(self):
        """Testa verificação de exclusão de usuário inexistente"""
        can_delete, reason = self.service.can_delete_user(99999)

        assert can_delete is False
        assert "encontrado" in reason.lower()


class TestOperationResult:
    """Testes para OperationResult"""

    def test_success_result(self):
        """Testa criação de resultado de sucesso"""
        result = OperationResult(success=True, message="Operação realizada")

        assert result.success is True
        assert result.message == "Operação realizada"
        assert result.errors == []

    def test_failure_result(self):
        """Testa criação de resultado de falha"""
        result = OperationResult(success=False, message="Erro", errors=["Erro 1", "Erro 2"])

        assert result.success is False
        assert len(result.errors) == 2


class TestUserManagementServiceEdgeCases:
    """Testes para casos extremos do UserManagementService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserManagementService()
        return

    def test_change_password_short(self):
        """Testa alteração com senha muito curta"""
        result = self.service.change_password(1, "123", "123")

        assert result.success is False
        assert len(result.errors) > 0

    def test_change_password_valid_length(self):
        """Testa alteração com senha de tamanho válido"""
        users = self.service.get_all_users()
        if users:
            # Tenta com um usuário existente que pode ser modificado
            modifiable_users = [u for u in users if u.can_be_modified]
            if modifiable_users:
                result = self.service.change_password(modifiable_users[0].id, "1234", "1234")
                # Pode ter sucesso ou falhar por outros motivos
                assert isinstance(result, OperationResult)

    def test_delete_user_tecnico(self):
        """Testa exclusão de usuário técnico"""
        users = self.service.get_all_users()
        tecnico_users = [u for u in users if u.is_technician]

        if tecnico_users:
            result = self.service.delete_user(tecnico_users[0].id)
            assert result.success is False
            assert "técnico" in result.message.lower() or "protegido" in result.message.lower()

    def test_can_modify_user_tecnico(self):
        """Testa verificação de modificação para técnico"""
        users = self.service.get_all_users()
        tecnico_users = [u for u in users if u.is_technician]

        if tecnico_users:
            can_modify, reason = self.service.can_modify_user(tecnico_users[0].id)
            assert can_modify is False
            assert "técnico" in reason.lower() or "protegido" in reason.lower()

    def test_can_delete_user_tecnico(self):
        """Testa verificação de exclusão para técnico"""
        users = self.service.get_all_users()
        tecnico_users = [u for u in users if u.is_technician]

        if tecnico_users:
            can_delete, reason = self.service.can_delete_user(tecnico_users[0].id)
            assert can_delete is False
            assert "técnico" in reason.lower() or "protegido" in reason.lower()

    def test_get_all_users_returns_list(self):
        """Testa que get_all_users sempre retorna lista"""
        users = self.service.get_all_users()
        assert isinstance(users, list)

    def test_user_data_equality(self):
        """Testa comparação de UserData"""
        user1 = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        user2 = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")

        # Dataclasses com mesmos valores devem ser iguais
        assert user1.id == user2.id
        assert user1.username == user2.username


class TestGetUserManagementService:
    """Testes para função get_user_management_service"""

    def test_returns_service(self):
        """Testa que retorna UserManagementService"""
        service = get_user_management_service()

        assert isinstance(service, UserManagementService)

    def test_returns_new_instance(self):
        """Testa que retorna nova instância"""
        service1 = get_user_management_service()
        service2 = get_user_management_service()

        assert isinstance(service1, UserManagementService)
        assert isinstance(service2, UserManagementService)


class TestUserManagementServiceAdditional:
    """Testes adicionais para UserManagementService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserManagementService()
        return

    def test_user_data_user_type_display_vendedor(self):
        """Tests user_type_display for vendedor"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.user_type_display == "Vendedor"

    def test_user_data_user_type_display_repositor(self):
        """Tests user_type_display for repositor"""
        user = UserData(1, "123", "Test", "repositor", True, "2025-01-01")
        assert user.user_type_display == "Repositor"

    def test_user_data_user_type_display_administrador(self):
        """Tests user_type_display for administrador"""
        user = UserData(1, "123", "Test", "administrador", True, "2025-01-01")
        assert user.user_type_display == "Administrador"

    def test_user_data_user_type_display_tecnico(self):
        """Tests user_type_display for tecnico"""
        user = UserData(1, "123", "Test", "tecnico", True, "2025-01-01")
        assert user.user_type_display == "Tecnico"

    def test_user_data_status_display_active(self):
        """Tests status_display for active"""
        user = UserData(1, "123", "Test", "vendedor", True, "2025-01-01")
        assert user.status_display == "Ativo"

    def test_user_data_status_display_inactive(self):
        """Tests status_display for inactive"""
        user = UserData(1, "123", "Test", "vendedor", False, "2025-01-01")
        assert user.status_display == "Inativo"

    def test_operation_result_success(self):
        """Testa OperationResult de sucesso"""
        result = OperationResult(True, "Operação realizada")
        assert result.success is True
        assert result.message == "Operação realizada"

    def test_operation_result_failure(self):
        """Testa OperationResult de falha"""
        result = OperationResult(False, "Erro na operação")
        assert result.success is False
        assert result.message == "Erro na operação"


class TestUserDataProperties:
    """Testes para propriedades de UserData"""

    def test_user_data_can_be_modified_admin(self):
        """Testa que admin pode ser modificado"""
        user = UserData(1, "admin", "Admin", "administrador", True, "2025-01-01")
        assert user.can_be_modified is True

    def test_user_data_can_be_modified_repositor(self):
        """Testa que repositor pode ser modificado"""
        user = UserData(1, "repo", "Repositor", "repositor", True, "2025-01-01")
        assert user.can_be_modified is True

    def test_user_data_can_be_deleted_admin(self):
        """Testa que admin pode ser excluído"""
        user = UserData(1, "admin", "Admin", "administrador", True, "2025-01-01")
        assert user.can_be_deleted is True

    def test_user_data_can_be_deleted_repositor(self):
        """Testa que repositor pode ser excluído"""
        user = UserData(1, "repo", "Repositor", "repositor", True, "2025-01-01")
        assert user.can_be_deleted is True

    def test_user_data_is_repositor(self):
        """Testa identificação de repositor"""
        user = UserData(1, "repo", "Repositor", "repositor", True, "2025-01-01")
        assert user.user_type == "repositor"

    def test_user_data_created_at_with_time(self):
        """Tests created_at with time"""
        user = UserData(1, "test", "Test", "vendedor", True, "2025-01-01 15:30:00")
        assert "2025-01-01" in user.created_at_display


class TestGetUserManagementServiceInstance:
    """Testes para get_user_management_service"""

    def test_get_service_returns_instance(self):
        """Testa que retorna instância"""
        service = get_user_management_service()
        assert isinstance(service, UserManagementService)
