import logging

import customtkinter

from ..bootstrap import Services
from . import assets, theme
from .navigation import Navigator

logger = logging.getLogger(__name__)


class MainApp(customtkinter.CTk):
    IDLE_CHECK_MS = 15_000

    def __init__(self, services: Services) -> None:
        super().__init__()
        self.services = services
        self.withdraw()

        customtkinter.set_appearance_mode(theme.APPEARANCE_MODE)
        customtkinter.set_default_color_theme(theme.COLOR_THEME)
        self.title("Ozempic Seguro")
        self.geometry("{}x{}".format(*theme.WINDOW_SIZE))
        self.minsize(*theme.WINDOW_MIN_SIZE)
        assets.preload()

        self.navigator = Navigator(self, services)
        self.navigator.show_attract()

        # Any touch counts as activity for the inactivity timeout.
        self.bind_all("<Button-1>", lambda _event: services.auth.touch(), add="+")
        self.after(self.IDLE_CHECK_MS, self._check_idle)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.update_idletasks()
        self.deiconify()

    def _check_idle(self) -> None:
        if self.services.auth.expire_if_idle():
            self.navigator.session_expired()
        self.after(self.IDLE_CHECK_MS, self._check_idle)

    def close(self) -> None:
        try:
            self.services.auth.logout()
        except Exception:
            logger.exception("Could not record logout while closing")
        finally:
            self.services.close()
            self.destroy()
