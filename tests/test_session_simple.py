"""
Testes simplificados para SessionManager.
"""

import pytest
from ozempic_seguro.session.session_manager import SessionManager


class TestSessionSimple:
    """Testes básicos para SessionManager"""

    @pytest.fixture(autouse=True)
    def reset_session(self):
        """Reset singleton antes e depois de cada teste"""
        SessionManager._instance = None
        yield
        if SessionManager._instance:
            if hasattr(SessionManager._instance, "_timeout_timer"):
                timer = SessionManager._instance._timeout_timer
                if timer:
                    timer.cancel()
        SessionManager._instance = None

    def test_singleton(self):
        """Testa padrão singleton"""
        session1 = SessionManager.get_instance()
        session2 = SessionManager.get_instance()
        assert session1 is session2

    def test_user_management(self):
        """Testa gerenciamento de usuário"""
        session = SessionManager.get_instance()

        # Inicialmente sem usuário
        assert session.get_current_user() is None
        assert session.is_logged_in() is False

        # Define usuário
        user = {"id": 1, "username": "test", "tipo": "vendedor"}
        session.set_current_user(user)

        assert session.get_current_user() == user
        assert session.is_logged_in() is True

        # Logout
        session.logout()
        assert session.get_current_user() is None
        assert session.is_logged_in() is False

    def test_admin_check(self):
        """Testa verificação de admin"""
        session = SessionManager.get_instance()

        # Usuário vendedor
        user_vendedor = {"id": 1, "username": "test", "tipo": "vendedor"}
        session.set_current_user(user_vendedor)
        assert session.is_admin() is False

        # Usuário admin
        user_admin = {"id": 2, "username": "admin", "tipo": "administrador"}
        session.set_current_user(user_admin)
        assert session.is_admin() is True

    def test_login_attempts(self):
        """Testa controle de tentativas de login"""
        session = SessionManager.get_instance()
        username = "test_user"

        # Incrementa tentativas
        session.increment_login_attempts(username)
        session.increment_login_attempts(username)

        # Verifica que foi registrado via método público
        assert session.get_remaining_attempts(username) == 1  # 3 - 2 = 1

        # Reset tentativas
        session.reset_login_attempts(username)
        assert session.get_remaining_attempts(username) == 3

    def test_user_blocking(self):
        """Testa bloqueio de usuário"""
        session = SessionManager.get_instance()
        username = "blocked_user"

        # Inicialmente não bloqueado
        assert session.is_user_blocked(username) is False

        # Simula 5 tentativas falhas
        for _ in range(5):
            session.increment_login_attempts(username)

        # Deve estar bloqueado após 5 tentativas
        assert session.is_user_blocked(username) is True

    def test_activity_update(self):
        """Testa atualização de atividade"""
        session = SessionManager.get_instance()

        user = {"id": 1, "username": "test"}
        session.set_current_user(user)

        # Captura atividade inicial
        initial_activity = session._last_activity

        # Espera um pouco e atualiza
        import time

        time.sleep(0.01)
        session.update_activity()

        # Atividade deve ter sido atualizada
        assert session._last_activity > initial_activity

    def test_cleanup(self):
        """Testa cleanup da sessão"""
        session = SessionManager.get_instance()

        user = {"id": 1, "username": "test"}
        session.set_current_user(user)

        # Cleanup
        session.cleanup()

        # Tudo deve estar limpo
        assert session._current_user is None
        assert session._last_activity is None
        assert session._timeout_timer is None
