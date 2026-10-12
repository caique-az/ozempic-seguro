"""
Testes de integração para módulo session.
"""

import pytest

from ozempic_seguro.session.session_manager import SessionManager
from ozempic_seguro.session.login_attempts import LoginAttemptsManager
from ozempic_seguro.session.timer_manager import TimerManager
from ozempic_seguro.config import Config


class TestSessionIntegration:
    """Testes de integração do módulo session"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_full_login_flow(self):
        """Testa fluxo completo de login"""
        # Simula login
        user = {"id": 1, "username": "testuser", "tipo": "vendedor"}
        self.session.set_current_user(user)

        assert self.session.is_logged_in() is True
        assert self.session.get_current_user() == user

        # Simula logout
        self.session.logout()

        assert self.session.is_logged_in() is False
        assert self.session.get_current_user() is None

    def test_login_attempts_integration(self):
        """Testa integração com controle de tentativas"""
        username = "integration_test_user"

        # Registra tentativas falhas
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS - 1):
            self.session.record_login_attempt(username, success=False)

        # Ainda não deve estar bloqueado
        assert self.session.is_user_locked(username) is False

        # Mais uma tentativa deve bloquear
        self.session.record_login_attempt(username, success=False)
        assert self.session.is_user_locked(username) is True

        # Reset
        self.session.reset_login_attempts(username)
        assert self.session.is_user_locked(username) is False

    def test_timer_integration(self):
        """Testa integração com timer"""
        # Configurar usuário admin
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        # Habilitar timer
        self.session.set_timer_enabled(True)
        assert self.session.is_timer_enabled() is True

        # Bloquear
        self.session.block_for_minutes(1)
        assert self.session.is_blocked() is True

        # Desbloquear
        self.session.clear_block()
        assert self.session.is_blocked() is False

    def test_session_with_different_user_types(self):
        """Testa sessão com diferentes tipos de usuário"""
        # Admin
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        assert self.session.is_admin() is True
        assert self.session.is_tecnico() is False

        # Técnico
        self.session.set_current_user({"id": 2, "username": "tecnico", "tipo": "tecnico"})
        assert self.session.is_admin() is False
        assert self.session.is_tecnico() is True

        # Vendedor
        self.session.set_current_user({"id": 3, "username": "vendedor", "tipo": "vendedor"})
        assert self.session.is_admin() is False
        assert self.session.is_tecnico() is False


class TestLoginAttemptsManagerDirect:
    """Testes diretos para LoginAttemptsManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.manager = LoginAttemptsManager()
        yield

    def test_record_attempt_success(self):
        """Testa registro de tentativa bem-sucedida"""
        username = "direct_test_success"

        self.manager.record_attempt(username, success=True)

        assert self.manager.is_locked(username) is False

    def test_record_attempt_failure(self):
        """Testa registro de tentativa falha"""
        username = "direct_test_failure"

        self.manager.record_attempt(username, success=False)

        remaining = self.manager.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_get_status_message(self):
        """Testa obtenção de mensagem de status"""
        username = "direct_test_status"

        self.manager.record_attempt(username, success=False)

        status = self.manager.get_status_message(username)

        assert isinstance(status, dict)
        assert "message" in status

    def test_reset(self):
        """Testa reset de tentativas"""
        username = "direct_test_reset"

        self.manager.record_attempt(username, success=False)
        self.manager.reset(username)

        remaining = self.manager.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS


class TestTimerManagerDirect:
    """Testes diretos para TimerManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.manager = TimerManager()
        yield

    def test_is_enabled_default(self):
        """Testa estado padrão do timer"""
        result = self.manager.is_enabled()
        assert isinstance(result, bool)

    def test_set_enabled(self):
        """Testa habilitação/desabilitação"""
        self.manager.set_enabled(True)
        assert self.manager.is_enabled() is True

        self.manager.set_enabled(False)
        assert self.manager.is_enabled() is False

    def test_block_and_unblock(self):
        """Testa bloqueio e desbloqueio"""
        self.manager.set_enabled(True)

        self.manager.block_for_minutes(1)
        assert self.manager.is_blocked() is True

        self.manager.clear_block()
        assert self.manager.is_blocked() is False

    def test_get_remaining_time(self):
        """Testa obtenção de tempo restante"""
        self.manager.set_enabled(True)
        self.manager.block_for_minutes(1)

        remaining = self.manager.get_remaining_time()

        assert isinstance(remaining, int)
        assert remaining >= 0

        self.manager.clear_block()
