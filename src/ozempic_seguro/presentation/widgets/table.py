"""Read-only table with pagination, built on ttk.Treeview."""

from collections.abc import Callable, Sequence
from tkinter import ttk
from typing import Any

import customtkinter

from .. import theme


class Table(customtkinter.CTkFrame):
    def __init__(
        self,
        master: Any,
        columns: Sequence[tuple[str, str, int]],
        on_page: Callable[[int], None],
        on_open: Callable[[int], None] | None = None,
    ) -> None:
        """`columns` are (id, heading, width); `on_open` receives the index of a double-clicked row."""
        super().__init__(master, fg_color="white", corner_radius=10)
        self._on_page = on_page
        self._page = 1

        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=(theme.FONT, 10))
        style.configure("Treeview.Heading", font=(theme.FONT, 10, "bold"))

        body = customtkinter.CTkFrame(self, fg_color="white")
        body.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(body)
        scrollbar.pack(side="right", fill="y")
        self._tree = ttk.Treeview(
            body,
            columns=[c[0] for c in columns],
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        scrollbar.config(command=self._tree.yview)
        for column_id, heading, width in columns:
            self._tree.heading(column_id, text=heading, anchor="w")
            self._tree.column(column_id, width=width, anchor="w")
        self._tree.tag_configure("odd", background=theme.ROW)
        self._tree.pack(fill="both", expand=True)
        if on_open:
            self._tree.bind("<Double-1>", lambda _e: self._open(on_open))

        pager = customtkinter.CTkFrame(self, fg_color="transparent")
        pager.pack(fill="x", padx=5, pady=(0, 5))
        self._previous = customtkinter.CTkButton(
            pager, text="Anterior", width=100, command=lambda: on_page(self._page - 1)
        )
        self._previous.pack(side="left", padx=5)
        self._label = customtkinter.CTkLabel(pager, text="", text_color=theme.TEXT)
        self._label.pack(side="left", padx=5)
        self._next = customtkinter.CTkButton(
            pager, text="Próximo", width=100, command=lambda: on_page(self._page + 1)
        )
        self._next.pack(side="left", padx=5)

    def show(
        self, rows: Sequence[Sequence[object]], page: int, total_pages: int, total: int
    ) -> None:
        self._page = page
        self._tree.delete(*self._tree.get_children())
        for index, row in enumerate(rows):
            self._tree.insert(
                "", "end", iid=str(index), values=list(row), tags=("odd",) if index % 2 else ()
            )
        self._label.configure(text=f"Página {page} de {total_pages} ({total} registros)")
        self._previous.configure(state="normal" if page > 1 else "disabled")
        self._next.configure(state="normal" if page < total_pages else "disabled")

    def _open(self, on_open: Callable[[int], None]) -> None:
        selection = self._tree.selection()
        if selection:
            on_open(int(selection[0]))
