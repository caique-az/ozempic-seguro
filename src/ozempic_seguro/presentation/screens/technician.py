from typing import Any

import customtkinter

from ..navigation import Navigator
from ..widgets.buttons import ModernButton
from .base import Screen
from .diagnostics import DiagnosticsScreen
from .timer_control import TimerControlScreen


class TechnicianScreen(Screen):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Técnico")
        menu = customtkinter.CTkFrame(self, fg_color="transparent")
        menu.pack(expand=True, pady=30)
        ModernButton(
            menu,
            "🔧 Diagnóstico",
            lambda: nav.show(lambda parent: DiagnosticsScreen(parent, nav)),
            style="warning",
            width=280,
            height=60,
        ).pack(pady=15)
        ModernButton(
            menu,
            "⏱️ Controle de Timer",
            lambda: nav.show(lambda parent: TimerControlScreen(parent, nav)),
            style="secondary",
            width=280,
            height=60,
        ).pack(pady=15)
        self.add_end_session_button()
