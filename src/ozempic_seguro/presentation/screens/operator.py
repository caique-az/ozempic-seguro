from typing import Any

from ..navigation import Navigator
from ..widgets.drawers import DrawerButton, DrawerGrid
from .base import Screen


class DrawerScreen(Screen):
    """Drawer grid for the logged-in user; what a tap does depends on their permissions."""

    def __init__(self, master: Any, nav: Navigator, title: str) -> None:
        super().__init__(master, nav, title)
        user = self.services.auth.current_user
        assert user is not None
        DrawerGrid(
            self,
            lambda parent, number: DrawerButton(
                parent,
                number,
                user,
                self.services.drawers,
                self.services.timer,
                self.services.settings.drawer_lock_minutes,
                self.attempt,
            ),
        )


class OperatorScreen(DrawerScreen):
    """Home screen of sellers (open only) and stockers (close only)."""

    def __init__(self, master: Any, nav: Navigator) -> None:
        user = nav.services.auth.current_user
        assert user is not None
        super().__init__(master, nav, user.role.label)
        self.add_end_session_button()
