"""
Serviço de gavetas: lógica de negócio para manipulação de gavetas.

Responsável por gerenciar estado das gavetas e histórico de operações.
"""

from dataclasses import dataclass
from typing import Any

from ..core.logger import logger
from ..repositories.gaveta_repository import GavetaRepository
from ..session.session_manager import SessionManager

# =============================================================================
# DTOs (Data Transfer Objects)
# =============================================================================


@dataclass
class DrawerState:
    """Estado de uma gaveta"""

    numero: int
    is_open: bool
    ultimo_usuario: str | None = None
    ultima_acao: str | None = None

    @property
    def status_display(self) -> str:
        """Retorna status formatado"""
        return "Aberta" if self.is_open else "Fechada"


@dataclass
class DrawerHistoryItem:
    """Item do histórico de gaveta"""

    data_hora: str
    gaveta_id: int
    action: str
    usuario: str

    @property
    def data_hora_display(self) -> str:
        """Retorna data/hora formatada"""
        try:
            if isinstance(self.data_hora, str):
                return self.data_hora
            return str(self.data_hora)
        except Exception:
            return "N/A"

    @property
    def action_display(self) -> str:
        """Returns formatted action"""
        acoes = {
            "aberta": "Abriu",
            "fechada": "Fechou",
            "abrir": "Abriu",
            "fechar": "Fechou",
        }
        return acoes.get(self.action.lower(), self.action.capitalize())


@dataclass
class PaginatedResult:
    """Resultado paginado genérico"""

    items: list[Any]
    total: int
    page: int
    per_page: int

    @property
    def total_pages(self) -> int:
        """Calcula total de páginas"""
        if self.per_page <= 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        """Verifica se há próxima página"""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Verifica se há página anterior"""
        return self.page > 1


# =============================================================================
# Service
# =============================================================================


class GavetaService:
    """
    Serviço singleton para operações de gavetas.

    Responsabilidades:
    - Gerenciar estado das gavetas (aberta/fechada)
    - Aplicar regras de negócio (bloqueio após abertura)
    - Consultar histórico de operações
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa dependências"""
        self._repository = GavetaRepository()
        self._session_manager = SessionManager.get_instance()

    @classmethod
    def get_instance(cls):
        """Retorna a instância singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_state(self, drawer_id: int) -> bool:
        """Returns the current state of a drawer"""
        return self._repository.get_state(drawer_id)

    def set_state(self, drawer_id: int, state: bool, user_type: str) -> tuple[bool, str]:
        """Sets the state of a drawer"""
        return self._repository.set_state(drawer_id, state, user_type)

    def close_drawer(
        self, drawer_id: int, user_type: str, user_id: int | None = None
    ) -> tuple[bool, str]:
        """Closes a drawer (used by Repositor)"""
        return self._repository.set_state(drawer_id, False, user_type, user_id)

    def open_drawer(
        self, drawer_id: int, user_type: str, user_id: int | None = None
    ) -> tuple[bool, str]:
        """
        Opens a drawer (used by Vendedor and Administrador).

        Business rule: blocks system for 5 minutes after opening
        by vendedor or administrador.
        """
        if user_type in ["vendedor", "administrador"] and self._session_manager.is_blocked():
            remaining = self._session_manager.get_remaining_time()
            minutes = remaining // 60
            seconds = remaining % 60
            return (
                False,
                f"Sistema bloqueado por {minutes}:{seconds:02d} minutos após a abertura da gaveta.",
            )

        try:
            if user_id is None:
                user_id = self._session_manager.get_user_id()

            result = self._repository.set_state(drawer_id, True, user_type, user_id)

            if user_type in ["vendedor", "administrador"]:
                self._session_manager.block_for_minutes(5)
                logger.info(
                    f"Drawer {drawer_id} opened by {user_type}, system blocked for 5 minutes"
                )
                return (
                    True,
                    f"Gaveta {drawer_id} aberta com sucesso! O sistema será bloqueado por 5 minutos.",
                )

            return (
                result[0] if isinstance(result, tuple) else result,
                f"Gaveta {drawer_id} aberta com sucesso!",
            )
        except Exception as e:
            logger.error(f"Error opening drawer {drawer_id}: {e}")
            return False, f"Erro ao abrir a gaveta: {e!s}"

    def get_history(self, drawer_id: int, limit: int = 10) -> list[tuple]:
        """Gets the history of changes for a drawer"""
        return self._repository.get_history(drawer_id, limit)

    def get_history_paginated(
        self, drawer_id: int, offset: int = 0, limit: int = 20
    ) -> list[tuple]:
        """Gets the history of changes for a drawer with pagination"""
        return self._repository.get_history_paginated(drawer_id, offset, limit)

    def count_history(self, drawer_id: int) -> int:
        """Returns the total number of history records for a drawer"""
        return self._repository.count_history(drawer_id)

    def get_all_history(self) -> list[tuple]:
        """Returns all history from all drawers"""
        try:
            return self._repository.get_all_history()
        except Exception as e:
            logger.error(f"Error fetching all history: {e}")
            return []

    def get_all_history_paginated(self, offset: int = 0, limit: int = 20) -> list[tuple]:
        """Returns paginated history for all drawers"""
        return self._repository.get_all_history_paginated(offset, limit)

    def count_all_history(self) -> int:
        """Returns the total number of history records from all drawers"""
        result = self._repository.count_all_history()
        return int(result) if result else 0

    # Aliases for backward compatibility (deprecated)
    get_estado = get_state
    set_estado = set_state
    fechar_gaveta = close_drawer
    abrir_gaveta = open_drawer
    get_historico = get_history
    get_historico_paginado = get_history_paginated
    get_total_historico = count_history
    get_todo_historico = get_all_history
    get_todo_historico_paginado = get_all_history_paginated
    get_total_todo_historico = count_all_history


# Alias for backward compatibility
GavetaStateManager = GavetaService
