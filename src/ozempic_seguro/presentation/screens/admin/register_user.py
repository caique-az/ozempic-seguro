from typing import Any

import customtkinter

from ....domain.exceptions import DomainError, ValidationError
from ....domain.users import CredentialPolicy, Role
from ... import theme
from ...navigation import Navigator
from ...widgets.dialogs import ConfirmDialog, Toast
from ...widgets.keyboards import VirtualKeyboard
from ..base import Screen

_P = CredentialPolicy


class RegisterUserScreen(Screen):
    def __init__(self, master: Any, nav: Navigator) -> None:
        super().__init__(master, nav, "Cadastro de Usuário")
        form = customtkinter.CTkFrame(self, fg_color="transparent")
        form.pack(side="left", fill="both", expand=True, padx=40, pady=(10, 110))

        self.name_entry = self._field(
            form, f"Nome (máx. {_P.NAME_MAX_LENGTH} caracteres)", self._fits_name
        )
        self.username_entry = self._field(
            form, f"Usuário (até {_P.USERNAME_MAX_LENGTH} dígitos)", self._fits_digits
        )
        self.password_entry = self._field(
            form,
            f"Senha ({_P.PASSWORD_MIN_LENGTH} a {_P.PASSWORD_MAX_LENGTH} dígitos)",
            self._fits_digits,
            show="•",
        )

        customtkinter.CTkLabel(
            form, text="Tipo de Usuário", font=(theme.FONT, 16, "bold"), text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        self.role = customtkinter.StringVar(value=Role.SELLER.value)
        for role in (Role.SELLER, Role.STOCKER, Role.ADMIN, Role.TECHNICIAN):
            customtkinter.CTkRadioButton(
                form, text=role.label, variable=self.role, value=role.value, text_color="white"
            ).pack(anchor="w", padx=10, pady=2)

        self.error_label = customtkinter.CTkLabel(
            form, text="", text_color="#FFB3B3", font=(theme.FONT, 12, "bold"), justify="left"
        )
        self.error_label.pack(anchor="w", pady=10)

        self._active = self.name_entry
        keyboard_area = customtkinter.CTkFrame(self, fg_color="transparent", width=600)
        keyboard_area.pack(side="right", fill="y", padx=20, pady=(20, 110))
        keyboard_area.pack_propagate(False)
        VirtualKeyboard(keyboard_area, lambda: self._active, self._save).pack(
            fill="both", expand=True
        )
        self.add_back_button()

    def _field(self, parent: Any, label: str, validator: Any, **options: Any) -> Any:
        customtkinter.CTkLabel(
            parent, text=label, font=(theme.FONT, 16, "bold"), text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        entry = customtkinter.CTkEntry(
            parent,
            width=300,
            height=40,
            font=(theme.FONT, 14),
            validate="key",
            validatecommand=(self.register(validator), "%P"),
            **options,
        )
        entry.pack(anchor="w")
        entry.bind("<Button-1>", lambda _e: setattr(self, "_active", entry))
        return entry

    @staticmethod
    def _fits_name(value: str) -> bool:
        return len(value) <= _P.NAME_MAX_LENGTH

    @staticmethod
    def _fits_digits(value: str) -> bool:
        return value == "" or (value.isdigit() and len(value) <= _P.PASSWORD_MAX_LENGTH)

    def _save(self) -> None:
        role = Role(self.role.get())
        name = self.name_entry.get().strip()
        if not ConfirmDialog.ask(
            self,
            "Confirmar Cadastro",
            f"Cadastrar '{name}' como {role.label}?",
            confirm_text="Cadastrar",
        ):
            return

        try:
            self.services.users.register(
                name, self.username_entry.get(), self.password_entry.get(), role
            )
        except ValidationError as error:
            self.error_label.configure(text="\n".join(error.errors))
            return
        except DomainError as error:
            self.error_label.configure(text=error.message)
            return

        Toast.show(self, f"Usuário '{name}' cadastrado com sucesso!", "success")
        self.error_label.configure(text="")
        for entry in (self.name_entry, self.username_entry, self.password_entry):
            entry.delete(0, "end")
        self.role.set(Role.SELLER.value)
        self._active = self.name_entry
