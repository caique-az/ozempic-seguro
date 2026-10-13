from typing import Any

import customtkinter

from .. import theme
from .buttons import ModernButton

_ICONS = {"question": "❓", "warning": "⚠️", "error": "❌", "info": "ℹ️", "success": "✅"}
_TOAST_COLORS = {
    "info": theme.INFO,
    "success": theme.SUCCESS,
    "warning": theme.WARNING,
    "error": theme.DANGER,
}


def center(window: customtkinter.CTkToplevel, width: int, height: int) -> None:
    window.update_idletasks()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


class ConfirmDialog:
    """Modal yes/no question. Use `ConfirmDialog.ask(...)`."""

    def __init__(
        self,
        parent: Any,
        title: str,
        message: str,
        icon: str,
        confirm_text: str,
        cancel_text: str,
    ) -> None:
        self.result = False
        self._dialog = customtkinter.CTkToplevel(parent)
        self._dialog.title(title)
        self._dialog.resizable(False, False)
        self._dialog.transient(parent.winfo_toplevel())
        center(self._dialog, 420, 260)
        self._dialog.grab_set()

        body = customtkinter.CTkFrame(self._dialog, fg_color="white")
        body.pack(fill="both", expand=True, padx=20, pady=20)
        customtkinter.CTkLabel(
            body, text=_ICONS.get(icon, "❓"), font=(theme.FONT, 32), text_color=theme.INFO
        ).pack(pady=(10, 15))
        customtkinter.CTkLabel(
            body, text=message, font=(theme.FONT, 14), text_color="black", wraplength=360
        ).pack(pady=(0, 20))

        buttons = customtkinter.CTkFrame(body, fg_color="transparent")
        buttons.pack()
        ModernButton(buttons, cancel_text, self._dialog.destroy, style="secondary", width=120).pack(
            side="left", padx=(0, 10)
        )
        ModernButton(buttons, confirm_text, self._confirm, width=120).pack(side="left")

        self._dialog.wait_window()

    def _confirm(self) -> None:
        self.result = True
        self._dialog.destroy()

    @staticmethod
    def ask(
        parent: Any,
        title: str,
        message: str,
        *,
        icon: str = "question",
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar",
    ) -> bool:
        return ConfirmDialog(parent, title, message, icon, confirm_text, cancel_text).result


class Toast:
    """Notification that slides in from the top right corner and leaves by itself."""

    _START, _END, _STEP, _FRAME_MS = 1.3, 0.98, 0.04, 15

    def __init__(self, parent: Any, message: str, kind: str, duration_ms: int) -> None:
        self._parent = parent
        self._duration_ms = duration_ms
        self._label = customtkinter.CTkLabel(
            parent,
            text=f"  {_ICONS.get(kind, '')}  {message}  ",
            font=(theme.FONT, 13, "bold"),
            text_color="white",
            fg_color=_TOAST_COLORS.get(kind, theme.INFO),
            corner_radius=0,
            padx=20,
            pady=12,
        )
        self._slide(self._START, -self._STEP)

    def _slide(self, x: float, step: float) -> None:
        if not self._label.winfo_exists():
            return
        if step < 0 and x <= self._END:
            self._label.place(relx=self._END, rely=0.02, anchor="ne")
            self._parent.after(self._duration_ms, lambda: self._slide(self._END, self._STEP))
            return
        if step > 0 and x >= self._START:
            self._label.destroy()
            return
        self._label.place(relx=x, rely=0.02, anchor="ne")
        self._label.lift()
        self._parent.after(self._FRAME_MS, lambda: self._slide(x + step, step))

    @staticmethod
    def show(parent: Any, message: str, kind: str = "info", duration_ms: int = 3000) -> None:
        Toast(parent, message, kind, duration_ms)
