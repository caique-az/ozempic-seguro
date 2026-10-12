from datetime import datetime

import pytest

from ozempic_seguro.domain.audit import AuditAction, AuditEntry
from ozempic_seguro.domain.drawers import DrawerAction


def make_entry(action: str) -> AuditEntry:
    return AuditEntry(
        id=1,
        occurred_at=datetime(2026, 1, 1, 12, 0),
        action=action,
        actor="00",
        target=None,
        target_id=None,
        details=None,
        origin=None,
    )


@pytest.mark.parametrize("action", list(AuditAction))
def test_every_action_has_a_label(action):
    assert action.label


def test_entry_label_uses_the_known_action():
    assert make_entry("ABRIR_GAVETA").action_label == "Gaveta aberta"


def test_entry_label_falls_back_to_raw_value_for_legacy_actions():
    assert make_entry("SECURITY_VIOLATION").action_label == "SECURITY_VIOLATION"


def test_drawer_action_labels():
    assert DrawerAction.OPENED.label == "Aberta"
    assert DrawerAction.CLOSED.label == "Fechada"
