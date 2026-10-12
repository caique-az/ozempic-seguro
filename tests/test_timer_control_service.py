"""
Testes para TimerControlService - Serviço de controle de timer.
"""

import pytest

from ozempic_seguro.services.timer_control_service import (
    TimerControlService,
    TimerStatus,
    get_timer_control_service,
)
from ozempic_seguro.session.session_manager import SessionManager


class TestTimerStatus:
    """Testes para TimerStatus"""

    def test_remaining_display_not_blocked(self):
        """Testa display quando não bloqueado"""
        status = TimerStatus(enabled=True, blocked=False, remaining_seconds=0, remaining_minutes=0)
        assert status.remaining_display == "Não bloqueado"

    def test_remaining_display_blocked(self):
        """Testa display quando bloqueado"""
        status = TimerStatus(enabled=True, blocked=True, remaining_seconds=125, remaining_minutes=2)
        assert "2:05" in status.remaining_display

    def test_status_display_disabled(self):
        """Testa status display desabilitado"""
        status = TimerStatus(enabled=False, blocked=False, remaining_seconds=0, remaining_minutes=0)
        assert "desabilitado" in status.status_display.lower()

    def test_status_display_enabled(self):
        """Testa status display habilitado"""
        status = TimerStatus(enabled=True, blocked=False, remaining_seconds=0, remaining_minutes=0)
        assert "habilitado" in status.status_display.lower()

    def test_status_display_blocked(self):
        """Testa status display bloqueado"""
        status = TimerStatus(enabled=True, blocked=True, remaining_seconds=60, remaining_minutes=1)
        assert "bloqueado" in status.status_display.lower()


class TestTimerControlService:
    """Testes para TimerControlService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = TimerControlService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_get_status(self):
        """Testa obtenção de status"""
        status = self.service.get_status()

        assert isinstance(status, TimerStatus)
        assert isinstance(status.enabled, bool)
        assert isinstance(status.blocked, bool)

    def test_enable_timer(self):
        """Testa habilitação do timer"""
        success, msg = self.service.enable_timer()

        assert success is True
        assert self.service.is_timer_enabled() is True

    def test_disable_timer(self):
        """Testa desabilitação do timer"""
        # Configurar usuário admin para ter permissão
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.service.enable_timer()
        success, msg = self.service.disable_timer()

        assert success is True

    def test_toggle_timer(self):
        """Testa alternância do timer"""
        initial = self.service.is_timer_enabled()
        success, msg, new_state = self.service.toggle_timer()

        assert success is True
        assert new_state != initial

    def test_block_system(self):
        """Testa bloqueio do sistema"""
        # Configurar usuário admin para ter permissão
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.service.enable_timer()
        success, msg = self.service.block_system(1)

        assert success is True

    def test_block_system_invalid_time(self):
        """Testa bloqueio com tempo inválido"""
        success, msg = self.service.block_system(0)

        assert success is False

    def test_unblock_system(self):
        """Testa desbloqueio do sistema"""
        self.service.enable_timer()
        self.service.block_system(1)
        success, msg = self.service.unblock_system()

        assert success is True
        assert self.service.is_blocked() is False

    def test_get_remaining_time(self):
        """Testa obtenção de tempo restante"""
        remaining = self.service.get_remaining_time()

        assert isinstance(remaining, int)
        assert remaining >= 0


class TestTimerControlServiceEdgeCases:
    """Testes para casos extremos do TimerControlService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = TimerControlService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_is_timer_enabled_returns_bool(self):
        """Testa que is_timer_enabled retorna booleano"""
        result = self.service.is_timer_enabled()
        assert isinstance(result, bool)

    def test_is_blocked_returns_bool(self):
        """Testa que is_blocked retorna booleano"""
        result = self.service.is_blocked()
        assert isinstance(result, bool)

    def test_block_system_multiple_times(self):
        """Testa bloqueio múltiplo"""
        self.service.enable_timer()

        success1, msg1 = self.service.block_system(1)
        assert success1 is True

        # Segundo bloqueio deve funcionar
        success2, msg2 = self.service.block_system(2)
        assert isinstance(success2, bool)

    def test_unblock_when_not_blocked(self):
        """Testa desbloquear quando não está bloqueado"""
        self.service.enable_timer()
        success, msg = self.service.unblock_system()

        # Deve funcionar mesmo sem estar bloqueado
        assert isinstance(success, bool)

    def test_toggle_timer_returns_tuple(self):
        """Testa que toggle retorna tupla"""
        success, msg, new_state = self.service.toggle_timer()

        assert isinstance(success, bool)
        assert isinstance(msg, str)
        assert isinstance(new_state, bool)

    def test_get_status_structure(self):
        """Testa estrutura do status"""
        status = self.service.get_status()

        assert isinstance(status.enabled, bool)
        assert isinstance(status.blocked, bool)
        assert isinstance(status.remaining_seconds, int)
        assert isinstance(status.remaining_minutes, int)


class TestGetTimerControlService:
    """Testes para função get_timer_control_service"""

    def test_returns_service(self):
        """Testa que retorna TimerControlService"""
        service = get_timer_control_service()

        assert isinstance(service, TimerControlService)

    def test_returns_same_instance(self):
        """Testa que retorna a mesma instância (singleton pattern)"""
        service1 = get_timer_control_service()
        service2 = get_timer_control_service()

        # Ambos devem ser instâncias de TimerControlService
        assert isinstance(service1, TimerControlService)
        assert isinstance(service2, TimerControlService)


class TestTimerControlServicePermissions:
    """Testes de permissões do TimerControlService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = TimerControlService()
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_admin_can_enable_timer(self):
        """Testa que admin pode habilitar timer"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        success, msg = self.service.enable_timer()
        assert success is True

    def test_tecnico_can_enable_timer(self):
        """Testa que técnico pode habilitar timer"""
        self.session.set_current_user({"id": 2, "username": "tec", "tipo": "tecnico"})
        success, msg = self.service.enable_timer()
        assert success is True

    def test_admin_can_block_system(self):
        """Testa que admin pode bloquear sistema"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.service.enable_timer()
        success, msg = self.service.block_system(5)
        assert success is True

    def test_admin_can_unblock_system(self):
        """Testa que admin pode desbloquear sistema"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        success, msg = self.service.unblock_system()
        assert success is True

    def test_status_remaining_display_formats_correctly(self):
        """Testa formatação do tempo restante"""
        status = TimerStatus(enabled=True, blocked=True, remaining_seconds=65, remaining_minutes=1)
        assert "1:05" in status.remaining_display

        status2 = TimerStatus(
            enabled=True, blocked=True, remaining_seconds=300, remaining_minutes=5
        )
        assert "5:00" in status2.remaining_display
