"""
Testes completos para SessionManager - Cobertura máxima.
"""

import pytest
from unittest.mock import MagicMock

from ozempic_seguro.session.session_manager import SessionManager
from ozempic_seguro.config import Config


class TestSessionManagerCore:
    """Testes principais do SessionManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_singleton_pattern(self):
        """Testa que SessionManager é singleton"""
        session1 = SessionManager.get_instance()
        session2 = SessionManager.get_instance()

        assert session1 is session2

    def test_set_current_user(self):
        """Testa definição de usuário atual"""
        user = {"id": 1, "username": "test", "tipo": "vendedor"}

        self.session.set_current_user(user)

        assert self.session.get_current_user() == user

    def test_get_current_user_none(self):
        """Testa obtenção de usuário quando não logado"""
        self.session.logout()

        assert self.session.get_current_user() is None

    def test_is_logged_in_true(self):
        """Testa verificação de login quando logado"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        assert self.session.is_logged_in() is True

    def test_is_logged_in_false(self):
        """Testa verificação de login quando não logado"""
        self.session.logout()

        assert self.session.is_logged_in() is False

    def test_logout(self):
        """Testa logout"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        self.session.logout()

        assert self.session.get_current_user() is None

    def test_update_activity(self):
        """Testa atualização de atividade"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        # Não deve lançar exceção
        self.session.update_activity()

    def test_is_session_expired_false(self):
        """Testa que sessão não expirou"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})

        assert self.session.is_session_expired() is False

    def test_is_session_expired_no_user(self):
        """Testa expiração sem usuário"""
        self.session.logout()

        assert self.session.is_session_expired() is False


class TestSessionManagerUserTypes:
    """Testes de tipos de usuário"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_is_admin_true(self):
        """Testa verificação de admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})

        assert self.session.is_admin() is True

    def test_is_admin_false(self):
        """Testa verificação de admin quando não é admin"""
        self.session.set_current_user({"id": 1, "username": "user", "tipo": "vendedor"})
        assert self.session.is_admin() is False

    def test_is_tecnico_true(self):
        """Testa verificação de técnico"""
        self.session.set_current_user({"id": 1, "username": "tec", "tipo": "tecnico"})
        assert self.session.is_tecnico() is True

    def test_is_tecnico_false(self):
        """Testa verificação de técnico quando não é técnico"""
        self.session.set_current_user({"id": 1, "username": "user", "tipo": "vendedor"})
        assert self.session.is_tecnico() is False

    def test_is_tecnico_no_user(self):
        """Testa verificação de técnico sem usuário"""
        self.session.logout()
        assert self.session.is_tecnico() is False

    def test_get_user_id(self):
        """Testa obtenção do ID do usuário"""
        self.session.set_current_user({"id": 42, "username": "test", "tipo": "vendedor"})
        assert self.session.get_user_id() == 42

    def test_get_user_id_no_user(self):
        """Testa obtenção do ID sem usuário"""
        self.session.logout()
        assert self.session.get_user_id() is None


class TestSessionManagerTimer:
    """Testes de timer do sistema"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_is_blocked_initial(self):
        """Testa que sistema não está bloqueado inicialmente"""
        assert isinstance(self.session.is_blocked(), bool)

    def test_get_remaining_time(self):
        """Testa obtenção de tempo restante"""
        result = self.session.get_remaining_time()
        assert isinstance(result, int)
        assert result >= 0

    def test_is_timer_enabled(self):
        """Testa verificação de timer habilitado"""
        result = self.session.is_timer_enabled()
        assert isinstance(result, bool)

    def test_set_timer_enabled_as_admin(self):
        """Testa ativação de timer como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        result = self.session.set_timer_enabled(True)
        assert result is True

    def test_set_timer_enabled_as_tecnico(self):
        """Testa ativação de timer como técnico"""
        self.session.set_current_user({"id": 1, "username": "tec", "tipo": "tecnico"})
        result = self.session.set_timer_enabled(False)
        assert result is True

    def test_set_timer_enabled_as_vendedor(self):
        """Testa que vendedor não pode alterar timer"""
        self.session.set_current_user({"id": 1, "username": "vend", "tipo": "vendedor"})
        result = self.session.set_timer_enabled(True)
        assert result is False

    def test_block_for_minutes_as_admin(self):
        """Testa bloqueio como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        self.session.set_timer_enabled(True)
        result = self.session.block_for_minutes(5)
        assert isinstance(result, bool)

    def test_block_for_minutes_as_vendedor(self):
        """Testa bloqueio como vendedor"""
        self.session.set_current_user({"id": 1, "username": "vend", "tipo": "vendedor"})
        self.session.set_timer_enabled(True)
        result = self.session.block_for_minutes(5)
        assert isinstance(result, bool)

    def test_clear_block_as_admin(self):
        """Testa limpeza de bloqueio como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        result = self.session.clear_block()
        assert result is True

    def test_clear_block_as_vendedor(self):
        """Testa que vendedor não pode limpar bloqueio"""
        self.session.set_current_user({"id": 1, "username": "vend", "tipo": "vendedor"})
        result = self.session.clear_block()
        assert result is False


class TestSessionManagerLogin:
    """Testes de tentativas de login"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_record_login_attempt_success(self):
        """Testa registro de tentativa de login bem sucedida"""
        self.session.record_login_attempt("test_user", success=True)
        # Não deve lançar exceção

    def test_record_login_attempt_failure(self):
        """Testa registro de tentativa de login falha"""
        self.session.record_login_attempt("test_user", success=False)
        # Não deve lançar exceção

    def test_is_user_locked(self):
        """Testa verificação de usuário bloqueado"""
        result = self.session.is_user_locked("test_user")
        assert isinstance(result, bool)

    def test_get_lockout_remaining_time(self):
        """Testa obtenção de tempo restante de bloqueio"""
        result = self.session.get_lockout_remaining_time("test_user")
        assert isinstance(result, int)

    def test_get_lockout_remaining_seconds(self):
        """Testa obtenção de segundos restantes de bloqueio"""
        result = self.session.get_lockout_remaining_seconds("test_user")
        assert isinstance(result, int)

    def test_get_remaining_attempts(self):
        """Testa obtenção de tentativas restantes"""
        result = self.session.get_remaining_attempts("new_user")
        assert isinstance(result, int)
        assert result >= 0

    def test_get_login_status_message(self):
        """Testa obtenção de mensagem de status"""
        result = self.session.get_login_status_message("test_user")
        assert isinstance(result, dict)

    def test_reset_login_attempts(self):
        """Testa reset de tentativas"""
        self.session.reset_login_attempts("test_user")
        # Não deve lançar exceção

    def test_increment_login_attempts_alias(self):
        """Testa alias increment_login_attempts"""
        self.session.increment_login_attempts("test_user")
        # Não deve lançar exceção

    def test_is_user_blocked_alias(self):
        """Testa alias is_user_blocked"""
        result = self.session.is_user_blocked("test_user")
        assert isinstance(result, bool)


class TestSessionManagerTimeout:
    """Testes de timeout de sessão"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_get_session_remaining_time(self):
        """Testa obtenção de tempo restante de sessão"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})
        result = self.session.get_session_remaining_time()
        assert isinstance(result, int)
        assert result >= 0

    def test_get_session_remaining_time_no_user(self):
        """Testa tempo restante sem usuário"""
        self.session.logout()
        result = self.session.get_session_remaining_time()
        assert result == 0

    def test_set_session_timeout_as_admin(self):
        """Testa definição de timeout como admin"""
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        result = self.session.set_session_timeout(30)
        assert result is True

    def test_set_session_timeout_as_vendedor(self):
        """Testa que vendedor não pode alterar timeout"""
        self.session.set_current_user({"id": 1, "username": "vend", "tipo": "vendedor"})
        result = self.session.set_session_timeout(30)
        assert result is False

    def test_update_last_activity_alias(self):
        """Testa alias update_last_activity"""
        self.session.set_current_user({"id": 1, "username": "test", "tipo": "vendedor"})
        self.session.update_last_activity()
        # Não deve lançar exceção

    def test_is_admin_false(self):
        """Testa verificação de não-admin"""
        self.session.set_current_user({"id": 2, "username": "vendedor", "tipo": "vendedor"})

        assert self.session.is_admin() is False

    def test_is_tecnico_true(self):
        """Testa verificação de técnico"""
        self.session.set_current_user({"id": 3, "username": "tecnico", "tipo": "tecnico"})

        assert self.session.is_tecnico() is True

    def test_is_tecnico_false(self):
        """Testa verificação de não-técnico"""
        self.session.set_current_user({"id": 2, "username": "vendedor", "tipo": "vendedor"})

        assert self.session.is_tecnico() is False

    def test_get_user_id(self):
        """Testa obtenção de ID do usuário"""
        self.session.set_current_user({"id": 42, "username": "test", "tipo": "vendedor"})

        assert self.session.get_user_id() == 42

    def test_get_user_id_none(self):
        """Testa obtenção de ID sem usuário"""
        self.session.logout()

        assert self.session.get_user_id() is None


class TestSessionManagerTimer:
    """Testes de timer do sistema"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        yield
        self.session.cleanup()

    def test_block_for_minutes(self):
        """Testa bloqueio por minutos"""
        result = self.session.block_for_minutes(1)

        assert result is True
        assert self.session.is_blocked() is True

        self.session.clear_block()

    def test_clear_block(self):
        """Testa limpeza de bloqueio"""
        self.session.block_for_minutes(1)

        result = self.session.clear_block()

        assert result is True
        assert self.session.is_blocked() is False

    def test_get_remaining_time(self):
        """Testa obtenção de tempo restante"""
        self.session.block_for_minutes(1)

        remaining = self.session.get_remaining_time()

        assert remaining >= 0

        self.session.clear_block()

    def test_is_timer_enabled(self):
        """Testa verificação de timer habilitado"""
        result = self.session.is_timer_enabled()

        assert isinstance(result, bool)

    def test_set_timer_enabled(self):
        """Testa habilitação/desabilitação do timer"""
        self.session.set_timer_enabled(False)

        # Quando desabilitado, bloqueio não funciona
        self.session.block_for_minutes(1)
        assert self.session.is_blocked() is False

        self.session.set_timer_enabled(True)


class TestSessionManagerLoginAttempts:
    """Testes de tentativas de login"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()

    def test_record_login_attempt_success(self):
        """Testa registro de tentativa bem-sucedida"""
        username = "test_success_user"

        self.session.record_login_attempt(username, success=True)

        assert self.session.is_user_locked(username) is False

    def test_record_login_attempt_failure(self):
        """Testa registro de tentativa falha"""
        username = "test_failure_user"

        self.session.record_login_attempt(username, success=False)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_user_locked_after_max_attempts(self):
        """Testa bloqueio após máximo de tentativas"""
        username = "test_locked_user"

        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.session.record_login_attempt(username, success=False)

        assert self.session.is_user_locked(username) is True

    def test_get_lockout_remaining_time(self):
        """Testa obtenção de tempo restante de lockout"""
        username = "test_lockout_time"

        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.session.record_login_attempt(username, success=False)

        remaining = self.session.get_lockout_remaining_time(username)

        assert remaining >= 0

    def test_get_login_status_message(self):
        """Testa obtenção de mensagem de status"""
        username = "test_status_msg"

        self.session.record_login_attempt(username, success=False)

        status = self.session.get_login_status_message(username)

        assert status is not None
        assert "message" in status

    def test_reset_login_attempts(self):
        """Testa reset de tentativas"""
        username = "test_reset_attempts"

        self.session.record_login_attempt(username, success=False)
        self.session.reset_login_attempts(username)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_increment_login_attempts_alias(self):
        """Testa alias increment_login_attempts"""
        username = "test_increment_alias"

        self.session.increment_login_attempts(username)

        remaining = self.session.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_is_user_blocked_alias(self):
        """Testa alias is_user_blocked"""
        username = "test_blocked_alias"

        assert self.session.is_user_blocked(username) is False


class TestSessionManagerAuditCallback:
    """Testes de callback de auditoria"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        yield
        self.session.cleanup()
        SessionManager._audit_callback = None

    def test_set_audit_callback(self):
        """Testa definição de callback"""
        callback = MagicMock()

        SessionManager.set_audit_callback(callback)

        assert SessionManager._audit_callback is callback
