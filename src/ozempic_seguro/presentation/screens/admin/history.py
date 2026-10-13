from typing import Any

from ...navigation import Navigator
from ...widgets.table import Table
from ..base import Screen


class HistoryScreen(Screen):
    """Open/close history of every drawer."""

    PER_PAGE = 20

    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Histórico de Ações nas Gavetas")
        self._table = Table(
            self,
            [
                ("when", "Data/Hora", 180),
                ("drawer", "Gaveta", 100),
                ("action", "Ação", 120),
                ("actor", "Usuário", 220),
            ],
            on_page=self._load,
        )
        self._table.pack(fill="both", expand=True, padx=40, pady=(20, 110))
        self.add_back_button()
        self._load(1)

    def _load(self, page: int) -> None:
        def load() -> None:
            result = self.services.drawers.all_history(page, self.PER_PAGE)
            rows = [
                (
                    f"{e.occurred_at:%d/%m/%Y %H:%M:%S}",
                    e.drawer_number,
                    e.action.label,
                    e.actor or "Sistema",
                )
                for e in result.items
            ]
            self._table.show(rows, result.page, result.total_pages, result.total)

        self.attempt(load)
