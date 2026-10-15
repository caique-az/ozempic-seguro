from typing import Any

import customtkinter

from .. import theme
from ..assets import image


class Header(customtkinter.CTkFrame):
    """White top bar with the screen title and the logo."""

    def __init__(self, master: Any, title: str) -> None:
        super().__init__(master, fg_color="white", corner_radius=0, height=80)
        self.pack(fill="x", side="top")
        customtkinter.CTkLabel(
            self, text=title, font=(theme.FONT, 24, "bold"), text_color="black"
        ).pack(side="left", padx=20, pady=20)
        customtkinter.CTkLabel(self, image=image("logo.jpg", 60), text="").pack(
            side="right", padx=20
        )
