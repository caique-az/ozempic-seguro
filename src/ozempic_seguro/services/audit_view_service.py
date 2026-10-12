"""
Serviço de visualização de auditoria - Lógica de auditoria separada das views.

Responsabilidades:
- Obter logs de auditoria
- Filtrar logs
- Paginar resultados
- Formatar dados para exibição
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..core.logger import logger
from .audit_service import AuditService


@dataclass
class AuditLogItem:
    """Item de log de auditoria"""

    id: int
    timestamp: str
    usuario: str
    action: str
    tabela: str
    id_afetado: int | None
    dados_anteriores: str | None
    dados_novos: str | None
    ip: str | None

    @property
    def timestamp_display(self) -> str:
        """Retorna data/hora formatada"""
        try:
            if isinstance(self.timestamp, str):
                return self.timestamp
            return str(self.timestamp)
        except Exception:
            return "N/A"

    @property
    def action_display(self) -> str:
        """Retorna ação formatada"""
        return self.action.upper() if self.action else "N/A"


@dataclass
class AuditFilter:
    """Filtros para busca de auditoria"""

    action: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    user: str | None = None
    table: str | None = None

    @classmethod
    def default_last_7_days(cls) -> "AuditFilter":
        """Cria filtro padrão dos últimos 7 dias"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return cls(
            start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d")
        )


@dataclass
class PaginatedAuditResult:
    """Resultado paginado de auditoria"""

    items: list[AuditLogItem]
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


class AuditViewService:
    """
    Serviço de visualização de auditoria.

    Encapsula toda a lógica de auditoria que estava nas views.
    """

    DEFAULT_PAGE_SIZE = 50
    AVAILABLE_ACTIONS = ("Todas", "LOGIN", "LOGOUT", "CRIAR", "ATUALIZAR", "EXCLUIR")

    def __init__(self):
        self._audit_service = AuditService()

    def get_logs(
        self, filter: AuditFilter | None = None, page: int = 1, per_page: int = DEFAULT_PAGE_SIZE
    ) -> PaginatedAuditResult:
        """
        Obtém logs de auditoria com filtros e paginação.

        Args:
            filter: Filtros a aplicar
            page: Página atual
            per_page: Itens por página

        Returns:
            PaginatedAuditResult com logs
        """
        try:
            offset = (page - 1) * per_page

            # Preparar filtros
            action_filter = None
            start_date = None
            end_date = None

            if filter:
                if filter.action and filter.action != "Todas":
                    action_filter = filter.action
                start_date = filter.start_date
                end_date = filter.end_date

            logs = self._audit_service.get_logs(
                offset=offset,
                limit=per_page,
                action_filter=action_filter,
                start_date=start_date,
                end_date=end_date,
            )

            total = self._audit_service.count_logs(
                action_filter=action_filter, start_date=start_date, end_date=end_date
            )

            # Converter para AuditLogItem
            items = []
            for log in logs:
                try:
                    items.append(
                        AuditLogItem(
                            id=log.get("id", 0),
                            timestamp=log.get("data_hora", ""),
                            usuario=log.get("usuario", ""),
                            action=log.get("acao", ""),
                            tabela=log.get("tabela_afetada", ""),
                            id_afetado=log.get("id_afetado"),
                            dados_anteriores=log.get("dados_anteriores"),
                            dados_novos=log.get("dados_novos"),
                            ip=log.get("endereco_ip"),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Error parsing audit log: {e}")
                    continue

            return PaginatedAuditResult(items=items, total=total, page=page, per_page=per_page)

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return PaginatedAuditResult(items=[], total=0, page=page, per_page=per_page)

    def get_available_actions(self) -> list[str]:
        """Retorna lista de ações disponíveis para filtro"""
        return list(self.AVAILABLE_ACTIONS)

    def get_default_filter(self) -> AuditFilter:
        """Retorna filtro padrão (últimos 7 dias)"""
        return AuditFilter.default_last_7_days()


def get_audit_view_service() -> AuditViewService:
    """Retorna instância do AuditViewService"""
    return AuditViewService()
