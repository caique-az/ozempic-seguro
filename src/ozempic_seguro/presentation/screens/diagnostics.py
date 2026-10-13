"""Drawer hardware status.

There is no hardware integration yet: the screen shows a fixed sample so the layout
can be evaluated, and says so explicitly.
"""

from dataclasses import dataclass
from typing import Any

import customtkinter

from .. import theme
from ..navigation import Navigator
from .base import Screen


@dataclass(frozen=True)
class _Slot:
    number: int
    connected: bool
    is_open: bool = False
    working: bool = True


_SAMPLE = [
    _Slot(1, connected=True, is_open=True),
    _Slot(2, connected=True, is_open=True, working=False),
    _Slot(3, connected=True),
    _Slot(4, connected=True),
    *(_Slot(n, connected=False) for n in range(5, 9)),
]

_LEGEND = [
    ("🟢", "Fechada/Funcionando"),
    ("🟠", "Aberta/Funcionando"),
    ("🔴", "Mau Funcionamento"),
    ("⬜", "Espaço Disponível"),
]


class DiagnosticsScreen(Screen):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Diagnóstico de Gavetas")
        card = customtkinter.CTkFrame(self, fg_color="white", corner_radius=15)
        card.pack(fill="both", expand=True, padx=40, pady=(20, 110))

        customtkinter.CTkLabel(
            card,
            text="⚠️ Modo demonstração: dados simulados, sem integração com o hardware",
            font=(theme.FONT, 12, "bold"),
            text_color=theme.WARNING_TEXT,
            fg_color=theme.WARNING_BG,
            corner_radius=8,
        ).pack(fill="x", padx=20, pady=(15, 5), ipady=6)

        connected = sum(slot.connected for slot in _SAMPLE)
        customtkinter.CTkLabel(
            card,
            text=f"💻 Capacidade: {len(_SAMPLE)} gavetas | Conectadas: {connected} | "
            f"Disponíveis: {len(_SAMPLE) - connected}",
            font=(theme.FONT, 12),
            text_color=theme.TEXT_MUTED,
        ).pack(pady=10)

        grid = customtkinter.CTkFrame(card, fg_color="transparent")
        grid.pack(pady=10, padx=20, expand=True)
        for index, slot in enumerate(_SAMPLE):
            row, column = divmod(index, 4)
            self._slot(grid, slot).grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        legend = customtkinter.CTkFrame(card, fg_color="#F9F9F9", corner_radius=10)
        legend.pack(pady=(10, 20), padx=20, fill="x")
        customtkinter.CTkLabel(legend, text="Legenda:", font=(theme.FONT, 12, "bold")).pack(
            side="left", padx=(20, 10), pady=10
        )
        for color, text in _LEGEND:
            customtkinter.CTkLabel(legend, text=f"{color} {text}", font=(theme.FONT, 11)).pack(
                side="left", padx=15
            )

        self.add_back_button()

    def _slot(self, parent: Any, slot: _Slot) -> customtkinter.CTkFrame:
        if not slot.connected:
            colors, lines = (
                ("#F5F5F5", "#CCCCCC"),
                [("+", 24, theme.TEXT_FAINT), ("Espaço Disponível", 11, theme.TEXT_MUTED)],
            )
        elif not slot.working:
            colors, lines = ("#FFEBEE", "#F44336"), [("⚠️ DEFEITO", 11, "#D32F2F")]
        elif slot.is_open:
            colors, lines = ("#FFF3E0", "#FF9800"), [("🔓 ABERTA", 12, "#FF6B35")]
        else:
            colors, lines = ("#E8F5E9", "#4CAF50"), [("🔒 FECHADA", 12, theme.SUCCESS_TEXT)]

        frame = customtkinter.CTkFrame(
            parent, fg_color=colors[0], border_color=colors[1], border_width=2, corner_radius=10
        )
        if slot.connected:
            customtkinter.CTkLabel(
                frame, text=f"Gaveta {slot.number}", font=(theme.FONT, 14, "bold")
            ).pack(padx=30, pady=(20, 8))
        for text, size, color in lines:
            customtkinter.CTkLabel(
                frame, text=text, font=(theme.FONT, size, "bold"), text_color=color
            ).pack(padx=30, pady=(0, 8))
        return frame
