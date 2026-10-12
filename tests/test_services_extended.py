"""
Testes estendidos para serviços - Cobertura adicional.
"""

import pytest

from ozempic_seguro.services.auth_service import AuthService
from ozempic_seguro.services.user_registration_service import (
    UserRegistrationService,
)
from ozempic_seguro.services.user_management_service import (
    UserManagementService,
    UserData,
)
from ozempic_seguro.services.gaveta_service import DrawerState, PaginatedResult
from ozempic_seguro.services.timer_control_service import TimerControlService, TimerStatus
from ozempic_seguro.services.audit_view_service import AuditViewService, AuditFilter
from ozempic_seguro.session.session_manager import SessionManager


class TestAuthServiceExtended:
    """Testes estendidos para AuthService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = AuthService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_login_empty_username(self):
        """Testa login com username vazio"""
        result = self.service.login("", "password")
        assert result.success is False

    def test_login_empty_password(self):
        """Testa login com senha vazia"""
        result = self.service.login("user", "")
        assert result.success is False

    def test_login_whitespace_username(self):
        """Testa login com username apenas espaços"""
        result = self.service.login("   ", "password")
        assert result.success is False

    def test_get_login_status_empty_user(self):
        """Testa status para usuário vazio"""
        status = self.service.get_login_status("")
        assert isinstance(status, dict)


class TestUserRegistrationServiceExtended:
    """Testes estendidos para UserRegistrationService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserRegistrationService()
        yield

    def test_validate_name_empty(self):
        """Testa validação de nome vazio"""
        result = self.service.validate_name("")
        assert result is True  # Nome vazio tem 0 caracteres, menor que 26

    def test_validate_name_max_length(self):
        """Testa validação de nome no limite"""
        result = self.service.validate_name("A" * 26)
        assert result is True

    def test_validate_username_empty(self):
        """Testa validação de username vazio"""
        result = self.service.validate_username("")
        assert result is False  # Vazio não é numérico

    def test_validate_password_boundary(self):
        """Testa validação de senha no limite"""
        result = self.service.validate_password("1234")  # Exatamente 4 dígitos
        assert result is True

        result = self.service.validate_password("12345678")  # Exatamente 8 dígitos
        assert result is True


class TestUserManagementServiceExtended:
    """Testes estendidos para UserManagementService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserManagementService()
        yield

    def test_change_password_empty_confirm(self):
        """Testa alteração com confirmação vazia"""
        result = self.service.change_password(1, "1234", "")
        assert result.success is False

    def test_delete_user_zero_id(self):
        """Testa exclusão com ID zero"""
        result = self.service.delete_user(0)
        assert result.success is False


class TestTimerControlServiceExtended:
    """Testes estendidos para TimerControlService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = TimerControlService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_block_system_negative_time(self):
        """Testa bloqueio com tempo negativo"""
        success, msg = self.service.block_system(-1)
        assert success is False

    def test_get_status_structure(self):
        """Testa estrutura do status"""
        status = self.service.get_status()

        assert hasattr(status, "enabled")
        assert hasattr(status, "blocked")
        assert hasattr(status, "remaining_seconds")
        assert hasattr(status, "remaining_minutes")


class TestAuditViewServiceExtended:
    """Testes estendidos para AuditViewService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = AuditViewService()
        yield

    def test_get_logs_with_todas_filter(self):
        """Testa logs com filtro 'Todas'"""
        filter = AuditFilter(action="Todas")
        result = self.service.get_logs(filter=filter)
        assert isinstance(result.items, list)

    def test_get_logs_page_2(self):
        """Testa logs página 2"""
        result = self.service.get_logs(page=2)
        assert result.page == 2

    def test_get_available_actions_contains_all(self):
        """Testa que ações contém todas as opções"""
        actions = self.service.get_available_actions()

        assert "Todas" in actions
        assert "LOGIN" in actions
        assert "LOGOUT" in actions
        assert "CRIAR" in actions


class TestDataclassProperties:
    """Testes para propriedades de dataclasses"""

    def test_user_data_all_properties(self):
        """Testa todas as propriedades de UserData"""
        user = UserData(1, "123", "Test User", "vendedor", True, "2025-01-01 10:00:00")

        assert user.is_technician is False
        assert user.is_admin is False
        assert user.can_be_modified is True
        assert user.can_be_deleted is True
        assert user.user_type_display == "Vendedor"
        assert user.status_display == "Ativo"
        assert "2025-01-01" in user.created_at_display

    def test_user_data_tecnico(self):
        """Testa UserData para técnico"""
        user = UserData(1, "123", "Tech User", "tecnico", True, "2025-01-01")

        assert user.is_technician is True
        assert user.can_be_modified is False
        assert user.can_be_deleted is False

    def test_user_data_admin(self):
        """Testa UserData para admin"""
        user = UserData(1, "123", "Admin User", "administrador", True, "2025-01-01")

        assert user.is_admin is True
        assert user.can_be_modified is True

    def test_drawer_state_properties(self):
        """Testa propriedades de DrawerState"""
        state_open = DrawerState(numero=1, is_open=True)
        state_closed = DrawerState(numero=2, is_open=False)

        assert state_open.status_display == "Aberta"
        assert state_closed.status_display == "Fechada"

    def test_timer_status_properties(self):
        """Testa propriedades de TimerStatus"""
        status = TimerStatus(enabled=True, blocked=True, remaining_seconds=90, remaining_minutes=1)

        assert "1:30" in status.remaining_display
        assert "bloqueado" in status.status_display.lower()

    def test_paginated_result_edge_cases(self):
        """Testa casos limite de PaginatedResult"""
        # Página única
        result = PaginatedResult(items=[], total=5, page=1, per_page=10)
        assert result.total_pages == 1
        assert result.has_next is False
        assert result.has_previous is False

        # Zero itens
        result = PaginatedResult(items=[], total=0, page=1, per_page=10)
        assert result.total_pages == 0
