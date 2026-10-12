"""
Testes para LoginAttemptsManager - Controle de tentativas de login.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from ozempic_seguro.config import Config
from ozempic_seguro.session.login_attempts import LoginAttemptsManager


class TestLoginAttemptsManager:
    """Testes para LoginAttemptsManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.manager = LoginAttemptsManager()
        return

    def test_initial_attempts_count(self):
        """Testa que usuário novo tem todas as tentativas disponíveis"""
        remaining = self.manager.get_remaining_attempts("new_user")
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_record_failed_attempt(self):
        """Testa registro de tentativa falha"""
        username = "test_user_fail"

        self.manager.record_attempt(username, success=False)

        remaining = self.manager.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_record_successful_attempt_resets(self):
        """Testa que tentativa bem-sucedida reseta contador"""
        username = "test_user_success"

        # Registrar algumas falhas
        self.manager.record_attempt(username, success=False)
        self.manager.record_attempt(username, success=False)

        # Registrar sucesso
        self.manager.record_attempt(username, success=True)

        # Deve ter resetado
        remaining = self.manager.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_user_blocked_after_max_attempts(self):
        """Testa que usuário é bloqueado após máximo de tentativas"""
        username = "test_user_blocked"

        # Esgotar tentativas
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.manager.record_attempt(username, success=False)

        assert self.manager.is_locked(username) is True

    def test_user_not_blocked_before_max_attempts(self):
        """Testa que usuário não é bloqueado antes do máximo"""
        username = "test_user_not_blocked"

        # Registrar menos que o máximo
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS - 1):
            self.manager.record_attempt(username, success=False)

        assert self.manager.is_locked(username) is False

    def test_get_lockout_remaining_time(self):
        """Testa obtenção do tempo restante de bloqueio"""
        username = "test_user_lockout_time"

        # Bloquear usuário
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.manager.record_attempt(username, success=False)

        remaining = self.manager.get_remaining_time_minutes(username)

        # Deve estar próximo do tempo de lockout configurado
        assert remaining >= 0
        assert remaining <= Config.Security.LOCKOUT_DURATION_MINUTES

    def test_get_lockout_remaining_seconds(self):
        """Testa obtenção do tempo restante em segundos"""
        username = "test_user_lockout_seconds"

        # Bloquear usuário
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.manager.record_attempt(username, success=False)

        remaining_seconds = self.manager.get_remaining_time_seconds(username)

        assert remaining_seconds >= 0
        assert remaining_seconds <= Config.Security.LOCKOUT_DURATION_MINUTES * 60

    def test_reset_attempts(self):
        """Testa reset manual de tentativas"""
        username = "test_user_reset"

        # Registrar falhas
        self.manager.record_attempt(username, success=False)
        self.manager.record_attempt(username, success=False)

        # Resetar
        self.manager.reset(username)

        remaining = self.manager.get_remaining_attempts(username)
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_get_login_status_message_not_blocked(self):
        """Testa mensagem de status quando não bloqueado"""
        username = "test_user_status_ok"

        self.manager.record_attempt(username, success=False)

        status = self.manager.get_status_message(username)

        assert status is not None
        assert "tentativa" in status["message"].lower() or "restante" in status["message"].lower()

    def test_get_login_status_message_blocked(self):
        """Testa mensagem de status quando bloqueado"""
        username = "test_user_status_blocked"

        # Bloquear
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.manager.record_attempt(username, success=False)

        status = self.manager.get_status_message(username)

        assert status is not None
        assert status["locked"] is True
        assert "bloqueado" in status["message"].lower() or "minuto" in status["message"].lower()

    @patch("ozempic_seguro.session.login_attempts.datetime")
    def test_lockout_expires(self, mock_datetime):
        """Testa que bloqueio expira após tempo configurado"""
        username = "test_user_lockout_expire"

        # Tempo inicial
        initial_time = datetime(2025, 1, 1, 10, 0, 0)
        mock_datetime.now.return_value = initial_time

        # Bloquear usuário
        for _ in range(Config.Security.MAX_LOGIN_ATTEMPTS):
            self.manager.record_attempt(username, success=False)

        # Avançar tempo além do lockout
        future_time = initial_time + timedelta(minutes=Config.Security.LOCKOUT_DURATION_MINUTES + 1)
        mock_datetime.now.return_value = future_time

        # Deve estar desbloqueado
        assert self.manager.is_locked(username) is False


class TestLoginAttemptsManagerEdgeCases:
    """Testes de casos extremos"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.manager = LoginAttemptsManager()
        return

    def test_empty_username(self):
        """Testa comportamento com username vazio"""
        remaining = self.manager.get_remaining_attempts("")
        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_special_characters_username(self):
        """Testa comportamento com caracteres especiais no username"""
        username = "user@test.com"

        self.manager.record_attempt(username, success=False)
        remaining = self.manager.get_remaining_attempts(username)

        assert remaining == Config.Security.MAX_LOGIN_ATTEMPTS - 1

    def test_multiple_users_independent(self):
        """Testa que contadores de usuários são independentes"""
        user1 = "user_independent_1"
        user2 = "user_independent_2"

        # Registrar falhas para user1
        self.manager.record_attempt(user1, success=False)
        self.manager.record_attempt(user1, success=False)

        # user2 não deve ser afetado
        remaining_user2 = self.manager.get_remaining_attempts(user2)
        assert remaining_user2 == Config.Security.MAX_LOGIN_ATTEMPTS

        remaining_user1 = self.manager.get_remaining_attempts(user1)
        assert remaining_user1 == Config.Security.MAX_LOGIN_ATTEMPTS - 2

    def test_get_remaining_time_minutes_not_locked(self):
        """Testa tempo restante quando não está bloqueado"""
        username = "user_not_locked_time"
        remaining = self.manager.get_remaining_time_minutes(username)
        assert remaining == 0

    def test_get_remaining_time_seconds_not_locked(self):
        """Testa tempo restante em segundos quando não está bloqueado"""
        username = "user_not_locked_seconds"
        remaining = self.manager.get_remaining_time_seconds(username)
        assert remaining == 0

    def test_get_remaining_time_minutes_with_attempts(self):
        """Testa tempo restante com tentativas mas não bloqueado"""
        username = "user_attempts_no_lock"
        self.manager.record_attempt(username, success=False)
        remaining = self.manager.get_remaining_time_minutes(username)
        assert remaining == 0

    def test_get_remaining_time_seconds_with_attempts(self):
        """Testa tempo em segundos com tentativas mas não bloqueado"""
        username = "user_attempts_no_lock_sec"
        self.manager.record_attempt(username, success=False)
        remaining = self.manager.get_remaining_time_seconds(username)
        assert remaining == 0

    def test_is_locked_unknown_user(self):
        """Testa is_locked para usuário desconhecido"""
        assert self.manager.is_locked("unknown_user_xyz") is False

    def test_reset_unknown_user(self):
        """Testa reset para usuário desconhecido"""
        self.manager.reset("unknown_reset_user")
        # Não deve lançar exceção

    def test_get_status_message_new_user(self):
        """Testa mensagem de status para usuário novo"""
        status = self.manager.get_status_message("brand_new_user")
        assert status["locked"] is False
        assert status["remaining_attempts"] == Config.Security.MAX_LOGIN_ATTEMPTS

    def test_get_status_message_with_remaining(self):
        """Testa mensagem de status com tentativas restantes"""
        username = "user_with_remaining"
        self.manager.record_attempt(username, success=False)

        status = self.manager.get_status_message(username)
        assert status["locked"] is False
        assert status["remaining_attempts"] < Config.Security.MAX_LOGIN_ATTEMPTS
