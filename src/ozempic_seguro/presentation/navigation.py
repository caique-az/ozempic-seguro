"""Screen switching and the session-level flow (attract loop, login, home, logout)."""

from collections.abc import Callable
from typing import TYPE_CHECKING

import customtkinter

from ..domain.users import Role
from . import theme
from .widgets.dialogs import Toast

if TYPE_CHECKING:
    from ..bootstrap import Services

type ScreenFactory = Callable[[customtkinter.CTkFrame], customtkinter.CTkFrame]


class Navigator:
    ATTRACT_INTERVAL_MS = 3000

    def __init__(self, root: customtkinter.CTk, services: "Services") -> None:
        self.root = root
        self.services = services
        self.container = customtkinter.CTkFrame(root, fg_color=theme.BACKGROUND, corner_radius=0)
        self.container.pack(fill="both", expand=True)
        self._current: customtkinter.CTkFrame | None = None
        self._attract_job: str | None = None
        self._attract_index = 0

    def show(self, factory: ScreenFactory) -> customtkinter.CTkFrame:
        """Build the next screen behind the current one, then swap them without flicker."""
        self._stop_attract()
        screen = factory(self.container)
        screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        screen.update_idletasks()
        screen.lift()
        if self._current is not None:
            self._current.destroy()
        self._current = screen
        return screen

    def show_attract(self) -> None:
        """Alternate the "touch to start" and logo screens until someone touches the screen."""
        from .screens.start import AttractScreen

        pages = [
            ("TOQUE NA TELA PARA COMEÇAR", "dedo.png"),
            ("TOQUE NA TELA PARA COMEÇAR", "logo.jpg"),
        ]
        text, image_name = pages[self._attract_index % len(pages)]
        self.show(lambda parent: AttractScreen(parent, text, image_name, self.show_start_session))
        self._attract_index += 1
        self._attract_job = self.root.after(self.ATTRACT_INTERVAL_MS, self.show_attract)

    def show_start_session(self) -> None:
        from .screens.start import StartSessionScreen

        self.show(lambda parent: StartSessionScreen(parent, self.show_login, self.show_attract))

    def show_login(self) -> None:
        from .screens.login import LoginScreen

        self.show(lambda parent: LoginScreen(parent, self))

    def show_home(self) -> None:
        from .screens.admin.panel import AdminPanelScreen
        from .screens.operator import OperatorScreen
        from .screens.technician import TechnicianScreen

        user = self.services.auth.current_user
        if user is None:
            self.show_start_session()
            return

        homes: dict[Role, ScreenFactory] = {
            Role.ADMIN: lambda parent: AdminPanelScreen(parent, self),
            Role.SELLER: lambda parent: OperatorScreen(parent, self),
            Role.STOCKER: lambda parent: OperatorScreen(parent, self),
            Role.TECHNICIAN: lambda parent: TechnicianScreen(parent, self),
        }
        self.show(homes[user.role])

    def end_session(self) -> None:
        timer_restored = self.services.auth.logout()
        self.show_start_session()
        Toast.show(self.container, "Sessão finalizada com sucesso", "success")
        if timer_restored:
            Toast.show(self.container, "Timer reativado automaticamente", "info", 4000)

    def session_expired(self) -> None:
        self.show_start_session()
        Toast.show(self.container, "Sessão encerrada por inatividade", "warning", 5000)

    def _stop_attract(self) -> None:
        if self._attract_job is not None:
            self.root.after_cancel(self._attract_job)
            self._attract_job = None
