from collections.abc import Callable
from typing import Any

import customtkinter

from .. import theme
from ..assets import image

_STYLES: dict[str, dict[str, Any]] = {
    "primary": {"fg_color": "#2E86C1", "hover_color": "#1F618D", "text_color": "white"},
    "secondary": {
        "fg_color": "white",
        "hover_color": "#F8F9FA",
        "text_color": "black",
        "border_color": "#DEE2E6",
        "border_width": 2,
    },
    "success": {"fg_color": "#28A745", "hover_color": "#1E7E34", "text_color": "white"},
    "danger": {"fg_color": "#DC3545", "hover_color": "#C82333", "text_color": "white"},
    "warning": {"fg_color": "#FFC107", "hover_color": "#E0A800", "text_color": "black"},
}


class ModernButton(customtkinter.CTkButton):
    """Button with one of the predefined color styles."""

    def __init__(
        self,
        master: Any,
        text: str,
        command: Callable[[], object] | None = None,
        style: str = "primary",
        **kwargs: Any,
    ) -> None:
        options = {
            "font": (theme.FONT, 14, "bold"),
            "corner_radius": 8,
            "height": 45,
            "width": 200,
            **_STYLES.get(style, _STYLES["primary"]),
            **kwargs,
        }
        super().__init__(master, text=text, command=command, **options)


class _IconButton(customtkinter.CTkFrame):
    """Round icon button placed near the bottom of a screen."""

    def __init__(
        self, master: Any, icon: str, command: Callable[[], object] | None, label: str | None
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.place(relx=0.5, rely=0.88, anchor="center")
        customtkinter.CTkButton(
            self,
            text="",
            width=40,
            height=40,
            image=image(icon, 40),
            fg_color="transparent",
            hover_color=theme.BACKGROUND,
            command=command,
        ).pack()
        if label:
            customtkinter.CTkLabel(
                self, text=label, font=(theme.FONT, 12), text_color="white"
            ).pack(pady=(5, 0))


class BackButton(_IconButton):
    def __init__(self, master: Any, command: Callable[[], object] | None) -> None:
        super().__init__(master, "botao_voltar.png", command, None)


class EndSessionButton(_IconButton):
    def __init__(self, master: Any, command: Callable[[], object]) -> None:
        super().__init__(master, "elipse.png", command, "Finalizar sessão")


class ButtonGrid(customtkinter.CTkFrame):
    """Grid of menu buttons that reflows its columns to the available width."""

    _BUTTON_WIDTH = 220

    def __init__(self, master: Any, buttons: list[tuple[str, Callable[[], object], str]]) -> None:
        super().__init__(master, fg_color="transparent")
        self.pack(expand=True, fill="both", padx=20, pady=20)
        self._buttons = buttons
        self._columns = 3
        self._build()
        self.bind("<Configure>", self._reflow)

    def _build(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        for index, (text, command, style) in enumerate(self._buttons):
            row, column = divmod(index, self._columns)
            ModernButton(self, text, command, style).grid(
                row=row, column=column, padx=10, pady=10, sticky="ew"
            )
        for column in range(self._columns):
            self.grid_columnconfigure(column, weight=1)

    def _reflow(self, event: Any) -> None:
        columns = max(1, min(3, event.width // self._BUTTON_WIDTH))
        if event.widget is self and columns != self._columns:
            self._columns = columns
            self._build()
