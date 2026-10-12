"""
Gerenciador de sessão principal do sistema Ozempic Seguro.

Responsável por controlar sessões de usuário, timeouts e bloqueios.
"""

import threading
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional

from ..config import Config
from ..core.logger import logger
from .login_attempts import LoginAttemptsManager
from .timer_manager import TimerManager


class SessionManager:
    """
    Gerenciador de sessão singleton thread-safe.

    Responsabilidades:
    - Gerenciamento de usuário logado
    - Controle de timeout de sessão
    - Delegação para LoginAttemptsManager e TimerManager

    Uso:
        session = SessionManager.get_instance()
        session.set_current_user(user_dict)
    """

    _instance: Optional["SessionManager"] = None
    _lock = threading.Lock()

    # Callback para auditoria (evita import circular)
    _audit_callback: Callable[[int, str, str, dict], None] | None = None

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa atributos da instância"""
        self._current_user: dict[str, Any] | None = None
        self._last_activity: datetime | None = None
        self._session_timeout: int = Config.Security.SESSION_TIMEOUT_MINUTES
        self._timeout_timer: threading.Timer | None = None

        # Componentes delegados
        self._login_attempts = LoginAttemptsManager()
        self._timer = TimerManager()

    @classmethod
    def set_audit_callback(cls, callback: Callable[[int, str, str, dict], None]) -> None:
        """Define callback para auditoria (evita import circular)."""
        cls._audit_callback = callback

    @classmethod
    def get_instance(cls):
        """Retorna a instância singleton do SessionManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ==================== Gerenciamento de Usuário ====================

    def set_current_user(self, user):
        """Define o usuário atual da sessão"""
        self._current_user = user
        if user:
            self._last_activity = datetime.now()
            self._start_timeout_timer()
        else:
            self._stop_timeout_timer()
            self._last_activity = None

    def get_current_user(self):
        """Retorna o usuário atual da sessão"""
        return self._current_user

    def is_logged_in(self):
        """Verifica se há um usuário logado"""
        return self._current_user is not None

    def logout(self):
        """Faz logout do usuário atual"""
        self.set_current_user(None)

    def update_activity(self):
        """Atualiza o timestamp da última atividade e reinicia timer"""
        if self._current_user:
            self._last_activity = datetime.now()
            self._stop_timeout_timer()
            self._start_timeout_timer()

    update_last_activity = update_activity  # Alias para compatibilidade

    def is_admin(self):
        """Verifica se o usuário atual é administrador"""
        return self._current_user and self._current_user.get("tipo") == "administrador"

    def is_tecnico(self):
        """Verifica se o usuário atual é técnico"""
        if self._current_user is None:
            return False
        return self._current_user.get("tipo") == "tecnico"

    def get_user_id(self):
        """Obtém o ID do usuário atualmente logado"""
        if self._current_user and "id" in self._current_user:
            return self._current_user["id"]
        return None

    # ==================== Timeout de Sessão ====================

    def is_session_expired(self):
        """Verifica se a sessão expirou por inatividade"""
        if not self._current_user or not self._last_activity:
            return False

        time_since_activity = datetime.now() - self._last_activity
        return time_since_activity.total_seconds() > (self._session_timeout * 60)

    def _start_timeout_timer(self):
        """Inicia o timer de timeout da sessão"""
        self._stop_timeout_timer()

        if self._current_user:
            self._timeout_timer = threading.Timer(self._session_timeout * 60, self._expire_session)
            self._timeout_timer.start()

    def _stop_timeout_timer(self):
        """Para o timer de timeout"""
        if self._timeout_timer:
            self._timeout_timer.cancel()
            self._timeout_timer = None

    def _expire_session(self) -> None:
        """Expira a sessão por inatividade"""
        if self._current_user:
            user_id = self._current_user.get("id")

            if self._audit_callback:
                try:
                    self._audit_callback(
                        user_id, "SESSION_EXPIRED", "SESSOES", {"motivo": "timeout_inatividade"}
                    )
                except Exception as e:
                    logger.error(f"Error logging session expiration: {e}")

            logger.info(f"Session expired for user {user_id}")
            self._current_user = None
            self._last_activity = None

    def get_session_remaining_time(self):
        """Retorna tempo restante da sessão em minutos"""
        if not self._current_user or not self._last_activity:
            return 0

        elapsed = datetime.now() - self._last_activity
        remaining_seconds = (self._session_timeout * 60) - elapsed.total_seconds()
        return max(0, int(remaining_seconds / 60))

    def set_session_timeout(self, minutes):
        """Define o timeout da sessão em minutos"""
        if self.is_admin():
            self._session_timeout = minutes
            if self._current_user:
                self._start_timeout_timer()
            return True
        return False

    # ==================== Timer do Sistema (delegado) ====================

    def is_blocked(self):
        """Verifica se o sistema está bloqueado"""
        return self._timer.is_blocked()

    def get_remaining_time(self):
        """Retorna o tempo restante de bloqueio em segundos"""
        return self._timer.get_remaining_time()

    def block_for_minutes(self, minutes=5):
        """Bloqueia o sistema por um número específico de minutos"""
        if not (
            self.is_admin() or (self._current_user and self._current_user.get("tipo") == "vendedor")
        ):
            return False
        if not self._timer.is_enabled():
            return False
        return self._timer.block_for_minutes(minutes)

    def clear_block(self):
        """Remove o bloqueio do sistema"""
        if not self.is_admin():
            return False
        self._timer.clear_block()
        return True

    def set_timer_enabled(self, enabled):
        """Ativa ou desativa a função de timer"""
        if not self.is_admin() and not self.is_tecnico():
            return False
        self._timer.set_enabled(enabled)
        return True

    def is_timer_enabled(self):
        """Verifica se a função de timer está ativada"""
        return self._timer.is_enabled()

    # ==================== Tentativas de Login (delegado) ====================

    def record_login_attempt(self, username, success=True):
        """Registra tentativa de login para controle de força bruta"""
        self._login_attempts.record_attempt(username, success)

    def is_user_locked(self, username):
        """Verifica se usuário está bloqueado por tentativas de login"""
        return self._login_attempts.is_locked(username)

    def get_lockout_remaining_time(self, username):
        """Retorna tempo restante de bloqueio em minutos"""
        return self._login_attempts.get_remaining_time_minutes(username)

    def get_lockout_remaining_seconds(self, username):
        """Retorna tempo restante de bloqueio em segundos"""
        return self._login_attempts.get_remaining_time_seconds(username)

    def get_remaining_attempts(self, username):
        """Retorna número de tentativas restantes antes do bloqueio"""
        return self._login_attempts.get_remaining_attempts(username)

    def get_login_status_message(self, username):
        """Retorna mensagem personalizada sobre o status de login"""
        return self._login_attempts.get_status_message(username)

    def reset_login_attempts(self, username):
        """Reseta tentativas de login de um usuário"""
        self._login_attempts.reset(username)

    # Aliases para compatibilidade
    def increment_login_attempts(self, username):
        """Alias para record_login_attempt(success=False)"""
        self.record_login_attempt(username, success=False)

    def is_user_blocked(self, username):
        """Alias para is_user_locked"""
        return self.is_user_locked(username)

    is_user_blocked_by_time = is_user_blocked

    # ==================== Cleanup ====================

    def cleanup(self) -> None:
        """Limpa a sessão e para timers"""
        self._stop_timeout_timer()

        if self._current_user and self._audit_callback:
            try:
                self._audit_callback(
                    self._current_user.get("id"),
                    "SESSION_CLEANUP",
                    "SESSOES",
                    {"details": "Sessão encerrada via cleanup"},
                )
            except Exception as e:
                logger.debug(f"Could not log cleanup: {e}")

        self._current_user = None
        self._last_activity = None
        self._timeout_timer = None
        self._timer.clear_block()
