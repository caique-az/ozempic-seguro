from datetime import date, timedelta

import pytest

from ozempic_seguro.domain.audit import AuditAction, AuditFilter, AuditTarget
from ozempic_seguro.domain.drawers import DrawerAction
from ozempic_seguro.domain.exceptions import UsernameTakenError
from ozempic_seguro.domain.users import Role


class TestUserRepository:
    def test_add_and_get(self, users):
        user = users.add("10", "hash", "Maria", Role.SELLER)

        assert users.get(user.id) == user
        assert users.get_by_username("10") == user
        assert (user.role, user.active) == (Role.SELLER, True)
        assert user.created_at is not None
        assert users.get_password_hash(user.id) == "hash"

    def test_missing_user(self, users):
        assert users.get(999) is None
        assert users.get_by_username("999") is None
        assert users.get_password_hash(999) is None

    def test_duplicate_username(self, users):
        users.add("10", "hash", "Maria", Role.SELLER)

        with pytest.raises(UsernameTakenError):
            users.add("10", "hash", "Outra", Role.STOCKER)

    def test_set_password_hash(self, users):
        user = users.add("10", "old", "Maria", Role.SELLER)

        users.set_password_hash(user.id, "new")

        assert users.get_password_hash(user.id) == "new"

    def test_deactivate_and_count(self, users):
        first = users.add("00", "h", "Admin", Role.ADMIN)
        users.add("02", "h", "Admin 2", Role.ADMIN)

        users.deactivate(first.id)

        assert users.get(first.id).active is False
        assert users.count_active(Role.ADMIN) == 1

    def test_list_shows_active_users_first(self, users):
        first = users.add("00", "h", "Admin", Role.ADMIN)
        users.add("10", "h", "Maria", Role.SELLER)
        users.deactivate(first.id)

        assert [u.username for u in users.list_all()] == ["10", "00"]

    def test_deactivated_user_with_audit_history_is_kept(self, users, audit):
        # Regression: the old hard DELETE failed with a foreign key error for any
        # user that had ever logged in.
        user = users.add("10", "h", "Maria", Role.SELLER)
        audit.record(AuditAction.LOGIN_SUCCESS, user_id=user.id)

        users.deactivate(user.id)

        assert users.get(user.id) is not None


class TestDrawerRepository:
    @pytest.fixture
    def user(self, users):
        return users.add("10", "h", "Maria", Role.SELLER)

    def test_unknown_drawer_is_closed(self, drawers):
        assert drawers.is_open(1001) is False

    def test_open_and_close_record_history(self, drawers, user):
        drawers.set_open(1001, True, user.id)
        assert drawers.is_open(1001)

        drawers.set_open(1001, False, user.id)
        assert not drawers.is_open(1001)

        events = drawers.history(1001, offset=0, limit=10)
        assert [e.action for e in events] == [DrawerAction.CLOSED, DrawerAction.OPENED]
        assert events[0].actor == "Maria"
        assert events[0].drawer_number == 1001
        assert drawers.count_history(1001) == 2

    def test_history_is_per_drawer_and_paginated(self, drawers, user):
        for number in (1001, 1001, 1002):
            drawers.set_open(number, True, user.id)

        assert drawers.count_history(1002) == 1
        assert drawers.count_all_history() == 3
        assert len(drawers.all_history(offset=1, limit=10)) == 2
        assert drawers.history(1001, offset=1, limit=1)[0].drawer_number == 1001


class TestAuditRepository:
    def test_record_and_search(self, audit, users):
        user = users.add("10", "h", "Maria", Role.SELLER)
        audit.record(
            AuditAction.DRAWER_OPENED,
            user_id=user.id,
            target=AuditTarget.DRAWER,
            target_id=1001,
            details={"motivo": "venda"},
        )

        (entry,) = audit.search(AuditFilter(), offset=0, limit=10)

        assert entry.action == "ABRIR_GAVETA"
        assert entry.action_label == "Gaveta aberta"
        assert (entry.actor, entry.target, entry.target_id) == ("10", "GAVETAS", 1001)
        assert entry.details == {"motivo": "venda"}
        assert entry.origin == "test-host"

    def test_entry_without_user_or_target(self, audit):
        audit.record(AuditAction.LOGIN_FAILED, details={"username": "99"})

        (entry,) = audit.search(AuditFilter(), offset=0, limit=10)

        assert entry.actor is None
        assert entry.target == "SISTEMA"

    def test_filter_by_action(self, audit):
        audit.record(AuditAction.LOGIN_FAILED)
        audit.record(AuditAction.LOGOUT)
        audit.record(AuditAction.LOGOUT)

        criteria = AuditFilter(action=AuditAction.LOGOUT)

        assert audit.count(criteria) == 2
        assert {e.action for e in audit.search(criteria, 0, 10)} == {"LOGOUT"}

    def test_filter_by_local_date_range(self, audit):
        audit.record(AuditAction.LOGOUT)
        today = date.today()

        assert audit.count(AuditFilter(start=today, end=today)) == 1
        assert audit.count(AuditFilter(end=today - timedelta(days=1))) == 0
        assert audit.count(AuditFilter(start=today + timedelta(days=1))) == 0

    def test_pagination_returns_newest_first(self, audit):
        for action in (AuditAction.LOGIN_SUCCESS, AuditAction.LOGOUT):
            audit.record(action)

        first_page = audit.search(AuditFilter(), offset=0, limit=1)

        assert [e.action for e in first_page] == ["LOGOUT"]

    def test_reads_legacy_entries(self, audit, db):
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO auditoria (acao, tabela_afetada, dados_anteriores) "
                "VALUES ('SECURITY_VIOLATION', 'USUARIOS', '{\"a\": 1}')"
            )

        (entry,) = audit.search(AuditFilter(), 0, 10)

        assert entry.action_label == "SECURITY_VIOLATION"
        assert entry.details == {"a": 1}
