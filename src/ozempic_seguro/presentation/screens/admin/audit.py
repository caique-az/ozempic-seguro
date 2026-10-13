from datetime import date
from tkinter import messagebox
from typing import Any

import customtkinter

from ....application.audit import AuditService
from ....domain.audit import AuditEntry, AuditFilter
from ... import theme
from ...formatting import (
    ALL_ACTIONS,
    action_from_label,
    action_options,
    format_date,
    format_details,
    parse_date,
)
from ...navigation import Navigator
from ...widgets.dialogs import center
from ...widgets.table import Table
from ..base import Screen


class AuditScreen(Screen):
    PER_PAGE = 50

    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Registro de Auditoria")
        self._entries: list[AuditEntry] = []
        self._criteria = AuditService.last_days(date.today())
        self._build_filters()
        self._table = Table(
            self,
            [
                ("when", "Data/Hora", 150),
                ("actor", "Usuário", 90),
                ("action", "Ação", 140),
                ("target", "Alvo", 90),
                ("target_id", "ID", 60),
                ("details", "Detalhes", 260),
                ("origin", "Estação", 110),
            ],
            on_page=self._load,
            on_open=self._show_details,
        )
        self._table.pack(fill="both", expand=True, padx=20, pady=(0, 110))
        self.add_back_button()
        self._load(1)

    def _build_filters(self) -> None:
        bar = customtkinter.CTkFrame(self, fg_color=theme.PANEL)
        bar.pack(fill="x", padx=20, pady=10, ipady=8)

        def label(text: str, column: int) -> None:
            customtkinter.CTkLabel(
                bar, text=text, text_color="white", font=(theme.FONT, 12, "bold")
            ).grid(row=0, column=column, padx=(10, 5), pady=5)

        label("Ação:", 0)
        self._action = customtkinter.CTkComboBox(
            bar, values=action_options(), width=170, state="readonly"
        )
        self._action.set(ALL_ACTIONS)
        self._action.grid(row=0, column=1, pady=5)

        label("De:", 2)
        self._start = customtkinter.CTkEntry(bar, width=110, placeholder_text="dd/mm/aaaa")
        self._start.insert(0, format_date(self._criteria.start))
        self._start.grid(row=0, column=3, pady=5)

        label("Até:", 4)
        self._end = customtkinter.CTkEntry(bar, width=110, placeholder_text="dd/mm/aaaa")
        self._end.insert(0, format_date(self._criteria.end))
        self._end.grid(row=0, column=5, pady=5)

        customtkinter.CTkButton(
            bar, text="Filtrar", width=110, fg_color="#17A2B8", command=self._apply
        ).grid(row=0, column=6, padx=10, pady=5)

    def _apply(self) -> None:
        try:
            self._criteria = AuditFilter(
                action=action_from_label(self._action.get()),
                start=parse_date(self._start.get()),
                end=parse_date(self._end.get()),
            )
        except ValueError as error:
            messagebox.showwarning("Filtro inválido", str(error), parent=self)
            return
        self._load(1)

    def _load(self, page: int) -> None:
        def load() -> None:
            result = self.services.audit.search(self._criteria, page, self.PER_PAGE)
            self._entries = result.items
            rows = [
                (
                    f"{e.occurred_at:%d/%m/%Y %H:%M:%S}",
                    e.actor or "-",
                    e.action_label,
                    e.target or "",
                    e.target_id if e.target_id is not None else "",
                    format_details(e.details),
                    e.origin or "",
                )
                for e in result.items
            ]
            self._table.show(rows, result.page, result.total_pages, result.total)

        self.attempt(load)

    def _show_details(self, index: int) -> None:
        entry = self._entries[index]
        window = customtkinter.CTkToplevel(self)
        window.title("Detalhes do Registro")
        center(window, 560, 380)
        window.transient(self.winfo_toplevel())

        body = customtkinter.CTkFrame(window, fg_color="white")
        body.pack(fill="both", expand=True, padx=10, pady=10)
        fields = [
            ("Data/Hora", f"{entry.occurred_at:%d/%m/%Y %H:%M:%S}"),
            ("Usuário", entry.actor or "-"),
            ("Ação", entry.action_label),
            ("Alvo", f"{entry.target or ''} {entry.target_id or ''}".strip()),
            ("Estação", entry.origin or ""),
            ("Detalhes", format_details(entry.details)),
        ]
        for name, value in fields:
            customtkinter.CTkLabel(
                body,
                text=f"{name}: {value}",
                font=(theme.FONT, 12),
                anchor="w",
                wraplength=500,
                justify="left",
            ).pack(fill="x", padx=10, pady=4)
        customtkinter.CTkButton(window, text="Fechar", width=100, command=window.destroy).pack(
            pady=10
        )
