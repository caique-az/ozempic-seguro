"""Users, roles and credential rules."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Role(StrEnum):
    """User profile. Values are the identifiers persisted in the database."""

    ADMIN = "administrador"
    SELLER = "vendedor"
    STOCKER = "repositor"
    TECHNICIAN = "tecnico"

    @property
    def label(self) -> str:
        return _ROLE_LABELS[self]


_ROLE_LABELS = {
    Role.ADMIN: "Administrador",
    Role.SELLER: "Vendedor",
    Role.STOCKER: "Repositor",
    Role.TECHNICIAN: "Técnico",
}


@dataclass(frozen=True, slots=True)
class User:
    id: int
    username: str
    full_name: str
    role: Role
    active: bool = True
    created_at: datetime | None = None

    @property
    def is_protected(self) -> bool:
        """Technicians maintain the device and cannot be changed from the admin panel."""
        return self.role is Role.TECHNICIAN


class CredentialPolicy:
    """Constraints matching the numeric virtual keyboard used on the device."""

    USERNAME_MAX_LENGTH = 8
    PASSWORD_MIN_LENGTH = 4
    PASSWORD_MAX_LENGTH = 8
    NAME_MAX_LENGTH = 26

    @classmethod
    def password_errors(cls, password: str) -> list[str]:
        if not password:
            return ["A senha é obrigatória"]
        errors = []
        if not password.isdigit():
            errors.append("A senha deve conter apenas números")
        if not cls.PASSWORD_MIN_LENGTH <= len(password) <= cls.PASSWORD_MAX_LENGTH:
            errors.append(
                f"A senha deve ter entre {cls.PASSWORD_MIN_LENGTH} e "
                f"{cls.PASSWORD_MAX_LENGTH} dígitos"
            )
        return errors

    @classmethod
    def new_user_errors(cls, full_name: str, username: str, password: str) -> list[str]:
        errors = []

        full_name = full_name.strip()
        if not full_name:
            errors.append("O nome é obrigatório")
        elif len(full_name) > cls.NAME_MAX_LENGTH:
            errors.append(f"O nome deve ter no máximo {cls.NAME_MAX_LENGTH} caracteres")

        username = username.strip()
        if not username:
            errors.append("O usuário é obrigatório")
        else:
            if not username.isdigit():
                errors.append("O usuário deve conter apenas números")
            if len(username) > cls.USERNAME_MAX_LENGTH:
                errors.append(f"O usuário deve ter no máximo {cls.USERNAME_MAX_LENGTH} dígitos")

        return errors + cls.password_errors(password)
