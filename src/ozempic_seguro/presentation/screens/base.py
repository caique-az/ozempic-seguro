from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter

from ...domain.exceptions import DomainError
from .. import theme
from ..navigation import Navigator
from ..widgets.buttons import BackButton, EndSessionButton
from ..widgets.dialogs import ConfirmDialog
from ..widgets.header import Header


class Screen(customtkinter.CTkFrame):
    """Base for screens shown after login: header, access to use cases and error display."""

    def __init__(self, master: Any, nav: Navigator, title: str) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, corner_radius=0)
        self.nav = nav
        self.services = nav.services
        Header(self, title)

    def attempt(self, action: Callable[[], object]) -> bool:
        """Run a use case; business rule violations are shown to the user instead of raised."""
        try:
            action()
        except DomainError as error:
            messagebox.showwarning("Aviso", error.message, parent=self)
            return False
        return True

    def add_back_button(self) -> None:
        BackButton(self, self.nav.show_home)

    def add_end_session_button(self) -> None:
        EndSessionButton(self, self.confirm_end_session)

    def confirm_end_session(self) -> None:
        if ConfirmDialog.ask(
            self,
            "Finalizar Sessão",
            "Tem certeza que deseja sair do sistema?",
            confirm_text="Sair",
        ):
            self.nav.end_session()
