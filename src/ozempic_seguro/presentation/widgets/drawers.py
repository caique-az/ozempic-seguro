"""Drawer grid: open/close drawers and inspect their history."""

from collections.abc import Callable
from typing import Any

import customtkinter

from ...application.drawers import DrawerService
from ...application.timer import TimerService
from ...domain.permissions import Permission, has_permission, opening_locks_system
from ...domain.users import User
from .. import theme
from ..assets import image
from .dialogs import ConfirmDialog, Toast, center

FIRST_DRAWER = 1001
DRAWER_COUNT = 15


def drawer_numbers() -> list[int]:
    return list(range(FIRST_DRAWER, FIRST_DRAWER + DRAWER_COUNT))


class DrawerButton(customtkinter.CTkFrame):
    """One drawer: tap to open or close it according to the user's permissions."""

    def __init__(
        self,
        master: Any,
        number: int,
        user: User,
        drawers: DrawerService,
        timer: TimerService,
        lock_minutes: int,
        attempt: Callable[[Callable[[], object]], bool],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._number = number
        self._user = user
        self._drawers = drawers
        self._timer = timer
        self._lock_minutes = lock_minutes
        self._attempt = attempt

        # The image must be set at construction: CTkButton only lays out its image
        # label when it is created with one.
        self._button = customtkinter.CTkButton(
            self,
            text="",
            width=120,
            height=120,
            image=self._image(),
            fg_color="transparent",
            hover_color=theme.BACKGROUND,
            command=self._on_tap,
        )
        self._button.pack(pady=(0, 5))
        customtkinter.CTkLabel(
            self, text=str(number), font=(theme.FONT, 12), text_color="white"
        ).pack()
        if has_permission(user.role, Permission.VIEW_DRAWER_HISTORY):
            customtkinter.CTkButton(
                self,
                text="Histórico",
                width=80,
                height=22,
                font=(theme.FONT, 11),
                fg_color=theme.PANEL,
                command=lambda: DrawerHistoryWindow(self, number, drawers),
            ).pack(pady=(4, 0))

    def _image(self) -> customtkinter.CTkImage:
        is_open = self._drawers.is_open(self._number)
        return image("gaveta.png" if is_open else "gaveta_black.png", 120)

    def _refresh(self) -> None:
        self._button.configure(image=self._image())

    def _on_tap(self) -> None:
        if self._drawers.is_open(self._number):
            self._attempt(self._close)
        elif self._confirm_opening():
            self._attempt(self._open)
        self._refresh()

    def _confirm_opening(self) -> bool:
        # Without permission, skip the dialog and let the use case report the denial.
        if not has_permission(self._user.role, Permission.OPEN_DRAWER):
            return True
        if not (self._timer.status().enabled and opening_locks_system(self._user.role)):
            return True
        return ConfirmDialog.ask(
            self,
            "Confirmar Abertura",
            f"Deseja realmente abrir a gaveta {self._number}?\n\n"
            f"O sistema será bloqueado por {self._lock_minutes} minutos após a abertura.",
            confirm_text="Abrir",
        )

    def _open(self) -> None:
        result = self._drawers.open(self._number)
        message = f"Gaveta {self._number} aberta"
        if result.lock_minutes:
            message += f" - sistema bloqueado por {result.lock_minutes} min"
        Toast.show(self.winfo_toplevel(), message, "success")

    def _close(self) -> None:
        self._drawers.close(self._number)
        Toast.show(self.winfo_toplevel(), f"Gaveta {self._number} fechada", "success")


class DrawerGrid(customtkinter.CTkFrame):
    """Pages of 2x4 drawers."""

    ROWS, COLUMNS = 2, 4

    def __init__(self, master: Any, build_drawer: Callable[[Any, int], DrawerButton]) -> None:
        super().__init__(master, fg_color="transparent")
        self.pack(expand=True, fill="both", padx=30, pady=(20, 110))
        self._build_drawer = build_drawer
        self._numbers = drawer_numbers()
        self._per_page = self.ROWS * self.COLUMNS
        self._pages = -(-len(self._numbers) // self._per_page)
        self._page = 0

        self._grid = customtkinter.CTkFrame(self, fg_color="transparent")
        self._grid.pack(expand=True, fill="both")
        for row in range(self.ROWS):
            self._grid.rowconfigure(row, weight=1)
        for column in range(self.COLUMNS):
            self._grid.columnconfigure(column, weight=1)

        nav = customtkinter.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=(10, 0))
        self._previous = customtkinter.CTkButton(
            nav, text="← Anterior", width=120, command=lambda: self._show(self._page - 1)
        )
        self._previous.pack(side="left", padx=(10, 5))
        self._next = customtkinter.CTkButton(
            nav, text="Próxima →", width=120, command=lambda: self._show(self._page + 1)
        )
        self._next.pack(side="left")
        self._show(0)

    def _show(self, page: int) -> None:
        self._page = max(0, min(page, self._pages - 1))
        for widget in self._grid.winfo_children():
            widget.destroy()

        start = self._page * self._per_page
        for index, number in enumerate(self._numbers[start : start + self._per_page]):
            row, column = divmod(index, self.COLUMNS)
            self._build_drawer(self._grid, number).grid(
                row=row, column=column, padx=10, pady=10, sticky="nsew"
            )

        self._previous.configure(state="normal" if self._page > 0 else "disabled")
        self._next.configure(state="normal" if self._page < self._pages - 1 else "disabled")


class DrawerHistoryWindow(customtkinter.CTkToplevel):
    PER_PAGE = 20

    def __init__(self, master: Any, number: int, drawers: DrawerService) -> None:
        super().__init__(master)
        self.title(f"Histórico - Gaveta {number}")
        center(self, 600, 420)
        self.transient(master.winfo_toplevel())
        self._number = number
        self._drawers = drawers
        self._page = 1

        body = customtkinter.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        customtkinter.CTkLabel(
            body, text=f"Histórico - Gaveta {number}", font=(theme.FONT, 14, "bold")
        ).pack(pady=(0, 10))
        self._list = customtkinter.CTkScrollableFrame(body, fg_color="transparent")
        self._list.pack(fill="both", expand=True)

        controls = customtkinter.CTkFrame(body, fg_color="transparent")
        controls.pack(fill="x", pady=(5, 0))
        self._previous = customtkinter.CTkButton(
            controls, text="Anterior", command=lambda: self._load(self._page - 1)
        )
        self._previous.pack(side="left", padx=5)
        self._label = customtkinter.CTkLabel(controls, text="", width=120)
        self._label.pack(side="left")
        self._next = customtkinter.CTkButton(
            controls, text="Próximo", command=lambda: self._load(self._page + 1)
        )
        self._next.pack(side="left", padx=5)
        customtkinter.CTkButton(controls, text="Fechar", command=self.destroy).pack(side="right")

        self._load(1)

    def _load(self, page: int) -> None:
        result = self._drawers.history(self._number, page, self.PER_PAGE)
        self._page = result.page
        for widget in self._list.winfo_children():
            widget.destroy()

        self._label.configure(text=f"Página {result.page} de {result.total_pages}")
        self._previous.configure(state="normal" if result.has_previous else "disabled")
        self._next.configure(state="normal" if result.has_next else "disabled")

        if not result.items:
            customtkinter.CTkLabel(
                self._list, text="Nenhum registro para esta gaveta.", text_color="gray"
            ).pack(pady=10)
            return

        for event in result.items:
            row = customtkinter.CTkFrame(self._list, fg_color=theme.ROW, corner_radius=5)
            row.pack(fill="x", pady=2, padx=2)
            customtkinter.CTkLabel(
                row,
                text=f"{event.occurred_at:%d/%m/%Y %H:%M:%S} - {event.action.label} por "
                f"{event.actor or 'Sistema'}",
                anchor="w",
            ).pack(fill="x", padx=5, pady=5)
