"""Screens shown before login."""

from collections.abc import Callable
from typing import Any

import customtkinter

from .. import theme
from ..assets import image
from ..widgets.buttons import BackButton
from ..widgets.header import Header


class AttractScreen(customtkinter.CTkFrame):
    """Idle screen: any touch starts a session."""

    def __init__(
        self, master: Any, text: str, image_name: str, on_touch: Callable[[], object]
    ) -> None:
        super().__init__(master, fg_color="white", corner_radius=0)
        label = customtkinter.CTkLabel(
            self, text=text, font=(theme.FONT, 32, "bold"), text_color="black"
        )
        label.pack(pady=40)
        picture = customtkinter.CTkLabel(self, image=image(image_name, 300), text="")
        picture.pack(pady=20)
        for widget in (self, label, picture):
            widget.bind("<Button-1>", lambda _event: on_touch())


class StartSessionScreen(customtkinter.CTkFrame):
    def __init__(
        self, master: Any, on_start: Callable[[], object], on_back: Callable[[], object]
    ) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND_DARK, corner_radius=0)
        Header(self, "Iniciar Sessão")
        customtkinter.CTkButton(
            self,
            text="Iniciar Sessão",
            font=(theme.FONT, 16, "bold"),
            width=300,
            height=60,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#E0E0E0",
            command=on_start,
        ).place(relx=0.5, rely=0.5, anchor="center")
        BackButton(self, on_back)
