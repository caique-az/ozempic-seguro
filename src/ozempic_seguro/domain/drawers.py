"""Medication drawers and their open/close history."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DrawerAction(StrEnum):
    """Values are the identifiers persisted in the drawer history."""

    OPENED = "aberta"
    CLOSED = "fechada"

    @property
    def label(self) -> str:
        return "Aberta" if self is DrawerAction.OPENED else "Fechada"


@dataclass(frozen=True, slots=True)
class DrawerEvent:
    drawer_number: int
    action: DrawerAction
    actor: str | None
    occurred_at: datetime
