"""
Serviço de controle de timer - Lógica de timer separada das views.

Responsabilidades:
- Habilitar/desabilitar timer
- Bloquear/desbloquear sistema
- Obter tempo restante
- Gerenciar estado do timer
"""

from dataclasses import dataclass

from ..core.logger import logger
from ..session.session_manager import SessionManager


@dataclass
class TimerStatus:
    """Status do timer"""

    enabled: bool
    blocked: bool
    remaining_seconds: int
    remaining_minutes: int

    @property
    def remaining_display(self) -> str:
        """Retorna tempo restante formatado"""
        if not self.blocked:
            return "Não bloqueado"

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def status_display(self) -> str:
        """Retorna status formatado"""
        if not self.enabled:
            return "Timer desabilitado"
        if self.blocked:
            return f"Bloqueado - {self.remaining_display}"
        return "Timer habilitado"


class TimerControlService:
    """
    Serviço de controle de timer.

    Encapsula toda a lógica de timer que estava nas views.
    """

    def __init__(self):
        self._session = SessionManager.get_instance()

    def get_status(self) -> TimerStatus:
        """
        Obtém status atual do timer.

        Returns:
            TimerStatus com estado atual
        """
        enabled = self._session.is_timer_enabled()
        blocked = self._session.is_blocked()
        remaining = self._session.get_remaining_time() if blocked else 0

        return TimerStatus(
            enabled=enabled,
            blocked=blocked,
            remaining_seconds=remaining,
            remaining_minutes=remaining // 60,
        )

    def enable_timer(self) -> tuple[bool, str]:
        """
        Habilita o timer.

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            self._session.set_timer_enabled(True)
            logger.info("Timer enabled")
            return True, "Timer habilitado com sucesso"
        except Exception as e:
            logger.error(f"Error enabling timer: {e}")
            return False, f"Erro ao habilitar timer: {e!s}"

    def disable_timer(self) -> tuple[bool, str]:
        """
        Desabilita o timer.

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            self._session.set_timer_enabled(False)
            logger.info("Timer disabled")
            return True, "Timer desabilitado com sucesso"
        except Exception as e:
            logger.error(f"Error disabling timer: {e}")
            return False, f"Erro ao desabilitar timer: {e!s}"

    def toggle_timer(self) -> tuple[bool, str, bool]:
        """
        Alterna estado do timer.

        Returns:
            Tuple (sucesso, mensagem, novo_estado)
        """
        current = self._session.is_timer_enabled()

        if current:
            success, msg = self.disable_timer()
        else:
            success, msg = self.enable_timer()

        return success, msg, not current

    def block_system(self, minutes: int) -> tuple[bool, str]:
        """
        Bloqueia o sistema por um período.

        Args:
            minutes: Minutos de bloqueio

        Returns:
            Tuple (sucesso, mensagem)
        """
        if minutes <= 0:
            return False, "Tempo de bloqueio deve ser maior que zero"

        try:
            self._session.block_for_minutes(minutes)
            logger.info(f"System blocked for {minutes} minutes")
            return True, f"Sistema bloqueado por {minutes} minutos"
        except Exception as e:
            logger.error(f"Error blocking system: {e}")
            return False, f"Erro ao bloquear sistema: {e!s}"

    def unblock_system(self) -> tuple[bool, str]:
        """
        Desbloqueia o sistema.

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            self._session.clear_block()
            logger.info("System unblocked")
            return True, "Sistema desbloqueado com sucesso"
        except Exception as e:
            logger.error(f"Error unblocking system: {e}")
            return False, f"Erro ao desbloquear sistema: {e!s}"

    def is_timer_enabled(self) -> bool:
        """Verifica se timer está habilitado"""
        return self._session.is_timer_enabled()

    def is_blocked(self) -> bool:
        """Verifica se sistema está bloqueado"""
        return self._session.is_blocked()

    def get_remaining_time(self) -> int:
        """Obtém tempo restante de bloqueio em segundos"""
        return self._session.get_remaining_time()


def get_timer_control_service() -> TimerControlService:
    """Retorna instância do TimerControlService"""
    return TimerControlService()
