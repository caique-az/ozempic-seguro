from tkinter import messagebox
from typing import Any

import customtkinter

from ...domain.exceptions import AccountLockedError, InvalidCredentialsError
from .. import theme
from ..navigation import Navigator
from ..widgets.buttons import BackButton, ModernButton
from ..widgets.header import Header
from ..widgets.keyboards import NumericKeypad

_DEFAULT_HINT = "Digite suas credenciais para acessar o sistema"


class LoginScreen(customtkinter.CTkFrame):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND_DARK, corner_radius=0)
        self.nav = nav
        self.auth = nav.services.auth
        self._countdown_job: str | None = None

        Header(self, "Login")
        self._build_form()
        self._build_keypad()
        BackButton(self, nav.show_start_session)

    def _build_form(self) -> None:
        form = customtkinter.CTkFrame(self, fg_color=theme.BACKGROUND_DARK)
        form.place(x=40, y=100)

        def field(label: str, pady: tuple[int, int], **options: Any) -> customtkinter.CTkEntry:
            customtkinter.CTkLabel(
                form, text=label, font=(theme.FONT, 16, "bold"), text_color="white"
            ).pack(anchor="w", pady=pady)
            entry = customtkinter.CTkEntry(form, width=300, height=40, **options)
            entry.pack(pady=10)
            entry.bind("<Button-1>", lambda _e: self._activate(entry))
            return entry

        self.username_entry = field("Usuário", (0, 5))
        self.password_entry = field("Senha", (20, 5), show="*")
        self.username_entry.bind("<KeyRelease>", lambda _e: self._refresh_status())
        self.password_entry.bind("<Return>", lambda _e: self._submit())

        self.status_label = customtkinter.CTkLabel(
            form,
            text=_DEFAULT_HINT,
            font=(theme.FONT, 12),
            text_color=theme.STATUS_OK,
            wraplength=280,
        )
        self.status_label.pack(pady=(10, 0))

        self._active = self.username_entry
        self.after(100, self.username_entry.focus_set)

    def _build_keypad(self) -> None:
        panel = customtkinter.CTkFrame(self, fg_color=theme.WHITE, corner_radius=20)
        panel.place(x=500, y=100)
        NumericKeypad(panel, lambda: self._active, extra_keys=False, fg_color="transparent").grid(
            row=0, column=0
        )

        actions = customtkinter.CTkFrame(panel, fg_color="transparent")
        actions.grid(row=1, column=0, pady=15)
        for text, command, style in [
            ("🗑️ Apagar", self._backspace, "warning"),
            ("❌ Cancelar", lambda: self._active.delete(0, "end"), "danger"),
            ("✅ Confirmar", self._submit, "success"),
        ]:
            ModernButton(actions, text, command, style=style, width=120).pack(side="left", padx=5)

    def _activate(self, entry: customtkinter.CTkEntry) -> None:
        self._active = entry

    def _backspace(self) -> None:
        self._active.delete(len(self._active.get()) - 1, "end")

    def _submit(self) -> None:
        username = self.username_entry.get()
        try:
            self.auth.login(username, self.password_entry.get())
        except AccountLockedError as error:
            messagebox.showerror("Conta Bloqueada", error.message, parent=self)
            self._start_countdown(username)
        except InvalidCredentialsError as error:
            messagebox.showerror("Login Inválido", error.message, parent=self)
            self.password_entry.delete(0, "end")
            self._refresh_status()
        else:
            self.nav.show_home()

    def _refresh_status(self) -> None:
        username = self.username_entry.get().strip()
        if not username:
            self.status_label.configure(text=_DEFAULT_HINT, text_color=theme.STATUS_OK)
            return

        status = self.auth.login_status(username)
        if status.locked:
            self._start_countdown(username)
        elif status.has_failed_attempts:
            self.status_label.configure(
                text=f"Atenção: {status.remaining_attempts} tentativa(s) restante(s)",
                text_color=theme.STATUS_WARNING,
            )
        else:
            self.status_label.configure(text=_DEFAULT_HINT, text_color=theme.STATUS_OK)

    def _start_countdown(self, username: str) -> None:
        if self._countdown_job is not None:
            self.after_cancel(self._countdown_job)
            self._countdown_job = None

        remaining = self.auth.login_status(username).remaining_seconds
        if remaining <= 0:
            self.status_label.configure(
                text="Bloqueio expirado. Você pode tentar novamente", text_color=theme.STATUS_OK
            )
            return

        minutes, seconds = divmod(remaining, 60)
        self.status_label.configure(
            text=f"Conta bloqueada - Restam {minutes}:{seconds:02d}",
            text_color=theme.STATUS_ERROR,
        )
        self._countdown_job = self.after(1000, lambda: self._start_countdown(username))

    def destroy(self) -> None:
        if self._countdown_job is not None:
            self.after_cancel(self._countdown_job)
        super().destroy()
