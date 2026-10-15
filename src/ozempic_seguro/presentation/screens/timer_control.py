from typing import Any

import customtkinter

from ...domain.permissions import Permission, has_permission
from .. import theme
from ..navigation import Navigator
from ..widgets.dialogs import ConfirmDialog, Toast
from .base import Screen


class TimerControlScreen(Screen):
    """Enable or disable the lock that follows a drawer opening."""

    REFRESH_MS = 1000

    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Controle de Timer")
        self._timer = self.services.timer
        user = self.services.auth.current_user
        assert user is not None
        self._can_clear = has_permission(user.role, Permission.CLEAR_SYSTEM_LOCK)
        self._job: str | None = None

        card = customtkinter.CTkFrame(self, fg_color="white", corner_radius=15)
        card.pack(expand=True, fill="both", padx=40, pady=(20, 110))
        customtkinter.CTkLabel(
            card,
            text="Bloqueio após abertura de gaveta",
            font=(theme.FONT, 20, "bold"),
            text_color=theme.TEXT,
        ).pack(pady=(30, 10))
        customtkinter.CTkLabel(
            card,
            text=f"Com o timer ativo, abrir uma gaveta bloqueia novas aberturas por "
            f"{self.services.settings.drawer_lock_minutes} minutos.\n"
            "O timer é reativado automaticamente quando a sessão termina.",
            font=(theme.FONT, 12),
            text_color=theme.TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, 20))

        self._status_box = customtkinter.CTkFrame(card, corner_radius=10)
        self._status_box.pack(pady=10, padx=40)
        self._status = customtkinter.CTkLabel(
            self._status_box, text="", font=(theme.FONT, 18, "bold")
        )
        self._status.pack(padx=50, pady=20)

        self._toggle = customtkinter.CTkButton(
            card,
            text="",
            width=200,
            height=50,
            font=(theme.FONT, 14, "bold"),
            command=self._on_toggle,
        )
        self._toggle.pack(pady=10)
        self._clear = customtkinter.CTkButton(
            card,
            text="Remover bloqueio atual",
            width=200,
            height=40,
            fg_color=theme.PANEL,
            command=self._on_clear,
        )

        self.add_back_button()
        self._refresh()

    def _on_toggle(self) -> None:
        if self._timer.status().enabled:
            if ConfirmDialog.ask(
                self,
                "Desativar Timer",
                "Desativar o timer? Gavetas poderão ser abertas em sequência sem bloqueio.",
                icon="warning",
                confirm_text="Desativar",
            ) and self.attempt(self._timer.disable):
                Toast.show(self, "Timer desativado", "warning")
        elif self.attempt(self._timer.enable):
            Toast.show(self, "Timer ativado", "success")
        self._refresh()

    def _on_clear(self) -> None:
        if self.attempt(self._timer.clear_lock):
            Toast.show(self, "Bloqueio removido", "success")
        self._refresh()

    def _refresh(self) -> None:
        status = self._timer.status()
        if status.enabled:
            text = "🟢 Timer ATIVADO"
            if status.locked:
                text += f"\nBloqueado - {status.remaining_display}"
            self._status_box.configure(fg_color=theme.SUCCESS_BG)
            self._status.configure(text=text, text_color=theme.SUCCESS_TEXT)
            self._toggle.configure(
                text="Desativar Timer", fg_color="#F44336", hover_color="#D32F2F"
            )
        else:
            self._status_box.configure(fg_color=theme.DANGER_BG)
            self._status.configure(text="🔴 Timer DESATIVADO", text_color=theme.DANGER_TEXT)
            self._toggle.configure(text="Ativar Timer", fg_color="#4CAF50", hover_color="#388E3C")

        if self._can_clear and status.locked:
            self._clear.pack(pady=(0, 10))
        else:
            self._clear.pack_forget()
        self._job = self.after(self.REFRESH_MS, self._refresh)

    def destroy(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
        super().destroy()
