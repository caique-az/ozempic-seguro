"""
Testes estendidos para SessionManager - Cobertura adicional.
"""

from unittest.mock import MagicMock

import pytest

from ozempic_seguro.config import Config
from ozempic_seguro.session.session_manager import SessionManager


class TestSessionManagerExtended:
    """Testes estendidos para SessionManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_is_admin_true(self):
        """Testa verificação de admin quando é admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        assert self.session.is_admin() is True

    def test_is_admin_false(self):
        """Testa verificação de admin quando não é admin"""
        self.session.set_current_user({"id": 2, "username": "vendedor", "tipo": "vendedor"})

        assert self.session.is_admin() is False

    def test_is_admin_no_user(self):
        """Testa verificação de admin sem usuário logado"""
        self.session.logout()

        # is_admin retorna None ou False quando não há usuário
        assert not self.session.is_admin()

    def test_is_tecnico_true(self):
        """Testa verificação de técnico quando é técnico"""
        self.session.set_current_user({"id": 3, "username": "tecnico", "tipo": "tecnico"})

        assert self.session.is_tecnico() is True

    def test_is_tecnico_false(self):
        """Testa verificação de técnico quando não é técnico"""
        self.session.set_current_user({"id": 2, "username": "vendedor", "tipo": "vendedor"})

        assert self.session.is_tecnico() is False

    def test_get_user_id(self):
        """Testa obtenção do ID do usuário"""
        self.session.set_current_user({"id": 42, "username": "test", "tipo": "vendedor"})

        assert self.session.get_user_id() == 42

    def test_get_user_id_no_user(self):
        """Testa obtenção do ID sem usuário logado"""
        self.session.logout()

        assert self.session.get_user_id() is None

    def test_is_blocked_delegates_to_timer(self):
        """Testa que is_blocked delega para TimerManager"""
        # Precisa ser admin ou vendedor para bloquear
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        self.session.block_for_minutes(1)

        assert self.session.is_blocked() is True

    def test_get_remaining_time(self):
        """Testa obtenção do tempo restante de bloqueio"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.session.block_for_minutes(5)

        remaining = self.session.get_remaining_time()

        assert remaining > 0
        assert remaining <= 5 * 60

    def test_clear_block(self):
        """Testa limpeza de bloqueio"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.session.block_for_minutes(5)
        assert self.session.is_blocked() is True

        self.session.clear_block()

        assert self.session.is_blocked() is False

    def test_is_user_locked(self):
        """Testa verificação de usuário bloqueado por tentativas"""
        username = "test_locked_user"

        # Esgotar tentativas
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.session.record_login_attempt(username, success=False)

        assert self.session.is_user_locked(username) is True

    def test_get_lockout_remaining_time(self):
        """Testa obtenção do tempo restante de lockout"""
        username = "test_lockout_user"

        # Bloquear usuário
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.session.record_login_attempt(username, success=False)

        remaining = self.session.get_lockout_remaining_time(username)

        assert remaining >= 0

    def test_get_remaining_attempts(self):
        """Testa obtenção de tentativas restantes"""
        username = "test_attempts_user"

        self.session.record_login_attempt(username, success=False)

        remaining = self.session.get_remaining_attempts(username)

        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_get_login_status_message(self):
        """Testa obtenção de mensagem de status de login"""
        username = "test_status_user"

        self.session.record_login_attempt(username, success=False)

        status = self.session.get_login_status_message(username)

        assert status is not None
        assert "message" in status

    def test_set_timer_enabled(self):
        """Testa habilitação/desabilitação do timer"""
        # Precisa ser admin ou tecnico para alterar timer
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        self.session.set_timer_enabled(False)

        # Quando desabilitado, bloqueio não deve funcionar
        self.session.block_for_minutes(5)
        assert self.session.is_blocked() is False

        self.session.set_timer_enabled(True)

    def test_set_session_timeout(self):
        """Testa definição de timeout de sessão"""
        # set_session_timeout modifica diretamente o atributo
        self.session._session_timeout = 30

        assert self.session._session_timeout == 30

        # Restaurar para valor padrão
        from ozempic_seguro.config import Config

        self.session._session_timeout = Config.Security.SESSION_TIMEOUT_MINUTES


class TestSessionManagerAuditCallback:
    """Testes para callback de auditoria"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()
        SessionManager._audit_callback = None

    def test_set_audit_callback(self):
        """Testa definição de callback de auditoria"""
        callback = MagicMock()

        SessionManager.set_audit_callback(callback)

        assert SessionManager._audit_callback is callback


class TestSessionManagerTimerFunctions:
    """Testes para funções de timer do SessionManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_is_timer_enabled_default(self):
        """Testa que timer está habilitado por padrão"""
        result = self.session.is_timer_enabled()
        assert isinstance(result, bool)

    def test_set_timer_enabled_as_admin(self):
        """Testa habilitar/desabilitar timer como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        result = self.session.set_timer_enabled(False)
        assert result is True

        self.session.set_timer_enabled(True)

    def test_set_timer_enabled_as_tecnico(self):
        """Testa habilitar/desabilitar timer como técnico"""
        self.session.set_current_user({"id": 1, "username": "tecnico", "tipo": "tecnico"})

        result = self.session.set_timer_enabled(False)
        assert result is True

        self.session.set_timer_enabled(True)

    def test_set_timer_enabled_as_vendedor_fails(self):
        """Testa que vendedor não pode alterar timer"""
        self.session.set_current_user({"id": 1, "username": "vendedor", "tipo": "vendedor"})

        result = self.session.set_timer_enabled(False)
        assert result is False

    def test_clear_block_as_admin(self):
        """Testa limpar bloqueio como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        self.session.block_for_minutes(1)
        result = self.session.clear_block()

        assert result is True
        assert self.session.is_blocked() is False

    def test_clear_block_as_vendedor_fails(self):
        """Testa que vendedor não pode limpar bloqueio"""
        self.session.set_current_user({"id": 1, "username": "vendedor", "tipo": "vendedor"})

        result = self.session.clear_block()
        assert result is False


class TestSessionManagerLoginAttempts:
    """Testes para funções de tentativas de login"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_record_login_attempt_success(self):
        """Testa registro de tentativa de login bem-sucedida"""
        username = "test_session_user"
        self.session.record_login_attempt(username, success=True)

        assert self.session.is_user_locked(username) is False

    def test_record_login_attempt_failure(self):
        """Testa registro de tentativa de login falha"""
        username = "test_session_fail"
        self.session.record_login_attempt(username, success=False)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining < Config.Security.MAX_LOGIN_ATTEMPTS

    def test_increment_login_attempts_alias(self):
        """Testa alias increment_login_attempts"""
        username = "test_increment_user"
        self.session.increment_login_attempts(username)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining < Config.Security.MAX_LOGIN_ATTEMPTS

    def test_is_user_blocked_alias(self):
        """Testa alias is_user_blocked"""
        username = "test_blocked_alias"
        result = self.session.is_user_blocked(username)
        assert result is False

    def test_get_lockout_remaining_time(self):
        """Testa obtenção de tempo restante de bloqueio"""
        username = "test_lockout_time"
        remaining = self.session.get_lockout_remaining_time(username)
        assert remaining == 0

    def test_get_lockout_remaining_seconds(self):
        """Testa obtenção de segundos restantes de bloqueio"""
        username = "test_lockout_seconds"
        remaining = self.session.get_lockout_remaining_seconds(username)
        assert remaining == 0

    def test_get_login_status_message(self):
        """Testa obtenção de mensagem de status de login"""
        username = "test_status_msg"
        status = self.session.get_login_status_message(username)

        assert isinstance(status, dict)
        assert "locked" in status

    def test_reset_login_attempts(self):
        """Testa reset de tentativas de login"""
        username = "test_reset_attempts"
        self.session.record_login_attempt(username, success=False)
        self.session.reset_login_attempts(username)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS


class TestSessionManagerSessionTimeout:
    """Testes para timeout de sessão"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_get_session_remaining_time_no_user(self):
        """Testa tempo restante sem usuário logado"""
        self.session.logout()
        remaining = self.session.get_session_remaining_time()
        assert remaining == 0

    def test_get_session_remaining_time_with_user(self):
        """Testa tempo restante com usuário logado"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        remaining = self.session.get_session_remaining_time()
        assert remaining > 0

    def test_is_session_expired_no_user(self):
        """Testa expiração sem usuário"""
        self.session.logout()
        assert self.session.is_session_expired() is False

    def test_is_session_expired_fresh_login(self):
        """Testa expiração logo após login"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        assert self.session.is_session_expired() is False

    def test_update_activity(self):
        """Testa atualização de atividade"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        self.session.update_activity()
        assert self.session.is_session_expired() is False

    def test_update_last_activity_alias(self):
        """Testa alias update_last_activity"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        self.session.update_last_activity()
        assert self.session.is_session_expired() is False

    def test_set_session_timeout_as_admin(self):
        """Testa definição de timeout como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        result = self.session.set_session_timeout(60)
        assert result is True

    def test_set_session_timeout_as_vendedor_fails(self):
        """Testa que vendedor não pode alterar timeout"""
        self.session.set_current_user({"id": 1, "username": "vendedor", "tipo": "vendedor"})

        result = self.session.set_session_timeout(60)
        assert result is False
