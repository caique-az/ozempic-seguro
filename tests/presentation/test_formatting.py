from datetime import date

import pytest

from ozempic_seguro.domain.audit import AuditAction
from ozempic_seguro.presentation.formatting import (
    ALL_ACTIONS,
    action_from_label,
    action_options,
    format_date,
    format_details,
    parse_date,
)


@pytest.mark.parametrize("text", ["15/01/2026", "2026-01-15", "  15/01/2026  "])
def test_parse_date_accepts_both_formats(text):
    assert parse_date(text) == date(2026, 1, 15)


def test_parse_date_empty_means_no_limit():
    assert parse_date("   ") is None


@pytest.mark.parametrize("text", ["31/02/2026", "ontem", "2026/01/15"])
def test_parse_date_rejects_invalid_input(text):
    with pytest.raises(ValueError, match="dd/mm/aaaa"):
        parse_date(text)


def test_format_date():
    assert format_date(date(2026, 1, 5)) == "05/01/2026"
    assert format_date(None) == ""


def test_action_options_round_trip():
    options = action_options()

    assert options[0] == ALL_ACTIONS
    assert action_from_label(ALL_ACTIONS) is None
    assert [action_from_label(label) for label in options[1:]] == list(AuditAction)


def test_format_details():
    assert format_details({"username": "10", "role": "vendedor"}) == "username: 10, role: vendedor"
    assert format_details(None) == ""
