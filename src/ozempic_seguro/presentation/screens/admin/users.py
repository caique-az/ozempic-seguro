from typing import Any

import customtkinter

from ....domain.exceptions import DomainError
from ....domain.users import User
from ... import theme
from ...navigation import Navigator
from ...widgets.buttons import ModernButton
from ...widgets.dialogs import ConfirmDialog, Toast, center
from ...widgets.keyboards import NumericKeypad
from ..base import Screen


class UsersScreen(Screen):
    """List users and change their password or deactivate them."""

    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Gerenciamento de Usuários")
        content = customtkinter.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(20, 110))
        content.columnconfigure((0, 1), weight=1)
        content.rowconfigure(0, weight=1)

        table = customtkinter.CTkFrame(content, fg_color="white", corner_radius=15)
        table.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        heading = customtkinter.CTkFrame(table, fg_color=theme.BORDER, corner_radius=8)
        heading.pack(fill="x", padx=10, pady=10)
        for column, text in enumerate(["Usuário", "Nome Completo", "Tipo", "Status"]):
            heading.columnconfigure(column, weight=1)
            customtkinter.CTkLabel(
                heading, text=text, font=(theme.FONT, 13, "bold"), text_color=theme.TEXT, anchor="w"
            ).grid(row=0, column=column, padx=10, pady=8, sticky="ew")
        self._rows = customtkinter.CTkScrollableFrame(table, fg_color="white")
        self._rows.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._details = customtkinter.CTkFrame(content, fg_color="white", corner_radius=15)
        self._details.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.add_back_button()
        self._load()

    def _load(self) -> None:
        for widget in self._rows.winfo_children():
            widget.destroy()
        self._show_placeholder()

        users: list[User] = []
        if not self.attempt(lambda: users.extend(self.services.users.list_users())):
            return

        for index, user in enumerate(users):
            row = customtkinter.CTkFrame(
                self._rows, fg_color=theme.ROW if index % 2 == 0 else theme.ROW_ALT, corner_radius=8
            )
            row.pack(fill="x", pady=2, padx=5)
            values = [user.username, user.full_name, user.role.label, _status(user)]
            for column, text in enumerate(values):
                row.columnconfigure(column, weight=1)
                label = customtkinter.CTkLabel(
                    row,
                    text=text,
                    font=(theme.FONT, 12, "bold" if column == 0 else "normal"),
                    text_color=theme.TEXT if user.active else theme.TEXT_FAINT,
                    anchor="w",
                )
                label.grid(row=0, column=column, padx=10, pady=8, sticky="ew")
                label.bind("<Button-1>", lambda _e, u=user: self._select(u))
            row.bind("<Button-1>", lambda _e, u=user: self._select(u))

    def _show_placeholder(self) -> None:
        for widget in self._details.winfo_children():
            widget.destroy()
        customtkinter.CTkLabel(
            self._details,
            text="Selecione um usuário para visualizar e editar",
            font=(theme.FONT, 14, "bold"),
            text_color=theme.TEXT_MUTED,
            wraplength=300,
        ).pack(pady=50, padx=20)

    def _select(self, user: User) -> None:
        for widget in self._details.winfo_children():
            widget.destroy()

        customtkinter.CTkLabel(
            self._details, text="Detalhes do Usuário", font=(theme.FONT, 16, "bold")
        ).pack(pady=(20, 15))
        created = f"{user.created_at:%d/%m/%Y}" if user.created_at else "N/A"
        for name, value in [
            ("Usuário", user.username),
            ("Nome Completo", user.full_name),
            ("Tipo", user.role.label),
            ("Status", _status(user)),
            ("Data de Criação", created),
        ]:
            customtkinter.CTkLabel(
                self._details, text=f"{name}: {value}", font=(theme.FONT, 12), anchor="w"
            ).pack(fill="x", padx=30, pady=2)

        if user.is_protected or not user.active:
            notice = (
                "⚠️ Usuários técnicos não podem ser alterados pelo painel"
                if user.is_protected
                else "Usuário excluído: mantido apenas para o histórico de auditoria"
            )
            customtkinter.CTkLabel(
                self._details,
                text=notice,
                font=(theme.FONT, 11, "bold"),
                text_color=theme.WARNING_TEXT,
                fg_color=theme.WARNING_BG,
                corner_radius=8,
                wraplength=300,
            ).pack(padx=20, pady=20, ipadx=10, ipady=10)
            return

        actions = customtkinter.CTkFrame(self._details, fg_color="transparent")
        actions.pack(pady=20)
        ModernButton(
            actions,
            "🔑 Alterar Senha",
            lambda: ChangePasswordDialog(self, user),
            style="success",
            width=170,
            height=50,
        ).pack(side="left", padx=5)
        ModernButton(
            actions,
            "🗑️ Excluir Usuário",
            lambda: self._delete(user),
            style="danger",
            width=170,
            height=50,
        ).pack(side="left", padx=5)

    def _delete(self, user: User) -> None:
        if not ConfirmDialog.ask(
            self,
            "Confirmar Exclusão",
            f"Excluir o usuário '{user.full_name}' ({user.username})?\n\n"
            "Ele não poderá mais acessar o sistema; o histórico é preservado.",
            icon="warning",
            confirm_text="Excluir",
        ):
            return
        if self.attempt(lambda: self.services.users.delete(user.id)):
            Toast.show(self, "Usuário excluído com sucesso", "success")
            self._load()


class ChangePasswordDialog(customtkinter.CTkToplevel):
    def __init__(self, screen: UsersScreen, user: User) -> None:
        super().__init__(screen)
        self.title("Alterar Senha")
        center(self, 700, 400)
        self.transient(screen.winfo_toplevel())
        self.grab_set()
        self._screen = screen
        self._user = user

        body = customtkinter.CTkFrame(self, fg_color="white")
        body.pack(fill="both", expand=True, padx=20, pady=20)
        fields = customtkinter.CTkFrame(body, fg_color="transparent")
        fields.pack(side="left", fill="both", expand=True, padx=(0, 10))
        customtkinter.CTkLabel(
            fields, text=f"Alterar senha de {user.full_name}", font=(theme.FONT, 16, "bold")
        ).pack(pady=(0, 20))

        def entry(label: str) -> customtkinter.CTkEntry:
            customtkinter.CTkLabel(fields, text=label, anchor="w").pack(fill="x", pady=(5, 5))
            widget = customtkinter.CTkEntry(fields, show="•", width=300)
            widget.pack(fill="x", pady=(0, 10))
            widget.bind("<Button-1>", lambda _e: setattr(self, "_active", widget))
            return widget

        self._new = entry("Nova Senha:")
        self._confirmation = entry("Confirmar Senha:")
        self._active = self._new
        self._message = customtkinter.CTkLabel(
            fields, text="", text_color=theme.DANGER, wraplength=300, justify="left"
        )
        self._message.pack(fill="x", pady=(10, 0))

        buttons = customtkinter.CTkFrame(fields, fg_color="transparent")
        buttons.pack(fill="x", pady=(20, 0))
        ModernButton(buttons, "💾 Salvar", self._save, style="success", height=40, width=140).pack(
            side="left", padx=5
        )
        ModernButton(
            buttons, "Cancelar", self.destroy, style="secondary", height=40, width=140
        ).pack(side="left", padx=5)

        NumericKeypad(body, lambda: self._active, fg_color="white").pack(side="right", fill="y")
        self._new.focus_set()

    def _save(self) -> None:
        try:
            self._screen.services.users.change_password(
                self._user.id, self._new.get(), self._confirmation.get()
            )
        except DomainError as error:
            self._message.configure(text=f"❌ {error.message}")
            return
        Toast.show(self._screen, "Senha alterada com sucesso", "success")
        self.destroy()


def _status(user: User) -> str:
    return "Ativo" if user.active else "Inativo"
