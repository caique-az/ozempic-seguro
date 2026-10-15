"""Interfaces the application needs from the outside world.

The infrastructure layer provides the implementations; tests provide in-memory fakes.
"""

from datetime import datetime
from typing import Any, Protocol

from .audit import AuditAction, AuditEntry, AuditFilter, AuditTarget
from .drawers import DrawerEvent
from .users import Role, User


class UserRepository(Protocol):
    def add(self, username: str, password_hash: str, full_name: str, role: Role) -> User:
        """Persist a new user. Raises UsernameTakenError if the username exists."""
        ...

    def get(self, user_id: int) -> User | None: ...

    def get_by_username(self, username: str) -> User | None: ...

    def get_password_hash(self, user_id: int) -> str | None: ...

    def list_all(self) -> list[User]: ...

    def set_password_hash(self, user_id: int, password_hash: str) -> None: ...

    def deactivate(self, user_id: int) -> None: ...

    def count_active(self, role: Role) -> int: ...


class DrawerRepository(Protocol):
    def is_open(self, drawer_number: int) -> bool: ...

    def set_open(self, drawer_number: int, is_open: bool, user_id: int) -> None:
        """Change the drawer state and append the change to its history."""
        ...

    def history(self, drawer_number: int, offset: int, limit: int) -> list[DrawerEvent]: ...

    def count_history(self, drawer_number: int) -> int: ...

    def all_history(self, offset: int, limit: int) -> list[DrawerEvent]: ...

    def count_all_history(self) -> int: ...


class AuditLog(Protocol):
    def record(
        self,
        action: AuditAction,
        *,
        user_id: int | None = None,
        target: AuditTarget | None = None,
        target_id: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    def search(self, criteria: AuditFilter, offset: int, limit: int) -> list[AuditEntry]: ...

    def count(self, criteria: AuditFilter) -> int: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
