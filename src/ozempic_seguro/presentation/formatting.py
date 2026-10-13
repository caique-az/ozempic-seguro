"""Conversions between what the user types or sees and domain values (no Tk code)."""

from datetime import date, datetime
from typing import Any

from ..domain.audit import AuditAction

ALL_ACTIONS = "Todas"
_DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d")


def parse_date(text: str) -> date | None:
    """Accept dd/mm/aaaa or aaaa-mm-dd; an empty field means no limit."""
    text = text.strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Data inválida: '{text}'. Use o formato dd/mm/aaaa")


def format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def action_options() -> list[str]:
    return [ALL_ACTIONS, *(action.label for action in AuditAction)]


def action_from_label(label: str) -> AuditAction | None:
    return next((action for action in AuditAction if action.label == label), None)


def format_details(details: dict[str, Any] | None) -> str:
    if not details:
        return ""
    return ", ".join(f"{key}: {value}" for key, value in details.items())
