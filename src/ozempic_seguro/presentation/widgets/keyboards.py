"""On-screen keyboards for the touch device."""

from collections.abc import Callable
from functools import partial
from typing import Any, ClassVar

import customtkinter

from .. import theme
from .buttons import ModernButton

BACKSPACE = "⌫"


class NumericKeypad(customtkinter.CTkFrame):
    """3x4 digit keypad that types into whichever entry is currently active."""

    def __init__(
        self,
        master: Any,
        get_target: Callable[[], customtkinter.CTkEntry],
        extra_keys: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self._get_target = get_target
        rows = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", BACKSPACE]]
        if not extra_keys:
            rows[-1][-1] = ""
        for r, row in enumerate(rows):
            for c, key in enumerate(row):
                if key:
                    ModernButton(
                        self,
                        key,
                        partial(self.press, key),
                        style="secondary",
                        width=90,
                        height=50,
                        font=(theme.FONT, 16, "bold"),
                    ).grid(row=r, column=c, padx=6, pady=6)

    def press(self, key: str) -> None:
        target = self._get_target()
        if key == BACKSPACE:
            target.delete(len(target.get()) - 1, "end")
        else:
            target.insert("end", key)


class VirtualKeyboard(customtkinter.CTkFrame):
    """Full alphanumeric keyboard with a save key."""

    _ROWS = (
        "1234567890",
        "qwertyuiop",
        "asdfghjklç",
        "zxcvbnm",
    )
    _KEY: ClassVar[dict[str, Any]] = {
        "height": 40,
        "font": (theme.FONT, 12, "bold"),
        "fg_color": "#FFFFFF",
        "text_color": "#000000",
        "hover_color": "#E0E0E0",
        "corner_radius": 5,
    }

    def __init__(
        self,
        master: Any,
        get_target: Callable[[], customtkinter.CTkEntry],
        on_save: Callable[[], object],
    ) -> None:
        super().__init__(master, fg_color="#F0F0F0", corner_radius=10)
        self._get_target = get_target
        self._on_save = on_save
        self._uppercase = False
        for column in range(10):
            self.grid_columnconfigure(column, weight=1)
        self._build()

    def _build(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

        for r, row in enumerate(self._ROWS):
            self.grid_rowconfigure(r, weight=1)
            for c, key in enumerate(row):
                shown = key.upper() if self._uppercase else key
                self._key(shown, partial(self._type, shown)).grid(
                    row=r, column=c, padx=2, pady=2, sticky="nsew"
                )

        last_letter_row = len(self._ROWS) - 1
        self._key(
            "SALVAR", self._on_save, fg_color="#2ECC71", text_color="white", hover_color="#27AE60"
        ).grid(row=last_letter_row, column=7, columnspan=2, padx=2, pady=2, sticky="nsew")
        self._key(BACKSPACE, self._backspace, fg_color="#E74C3C", text_color="white").grid(
            row=last_letter_row, column=9, padx=2, pady=2, sticky="nsew"
        )

        function_row = len(self._ROWS)
        self._key(
            "MAIÚSCULAS",
            self._toggle_case,
            fg_color="#3498DB" if self._uppercase else "#FFFFFF",
            text_color="#FFFFFF" if self._uppercase else "#000000",
        ).grid(row=function_row, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        self._key("LIMPAR", lambda: self._get_target().delete(0, "end")).grid(
            row=function_row, column=2, columnspan=2, padx=2, pady=2, sticky="nsew"
        )
        self._key("______", lambda: self._type(" ")).grid(
            row=function_row, column=4, columnspan=6, padx=2, pady=2, sticky="nsew"
        )

    def _key(self, text: str, command: Callable[[], object], **style: Any) -> Any:
        return customtkinter.CTkButton(self, text=text, command=command, **{**self._KEY, **style})

    def _type(self, text: str) -> None:
        self._get_target().insert("end", text)

    def _backspace(self) -> None:
        target = self._get_target()
        target.delete(len(target.get()) - 1, "end")

    def _toggle_case(self) -> None:
        self._uppercase = not self._uppercase
        self._build()
