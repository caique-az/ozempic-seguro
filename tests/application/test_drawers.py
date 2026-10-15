import pytest

from ozempic_seguro.domain.audit import AuditAction, AuditTarget
from ozempic_seguro.domain.drawers import DrawerAction
from ozempic_seguro.domain.exceptions import (
    DrawerStateError,
    NotAuthenticatedError,
    PermissionDeniedError,
    SystemLockedError,
)
from ozempic_seguro.domain.users import Role


class TestOpen:
    def test_seller_opens_and_locks_the_system(self, app):
        app.login_as(Role.SELLER)

        result = app.drawers.open(1001)

        assert result.lock_minutes == 5
        assert app.drawers.is_open(1001)
        assert app.timer.status().locked
        record = app.audit_log.records[-1]
        assert record.action is AuditAction.DRAWER_OPENED
        assert (record.target, record.target_id) == (AuditTarget.DRAWER, 1001)

    def test_second_opening_is_blocked_while_locked(self, app):
        app.login_as(Role.SELLER)
        app.drawers.open(1001)
        app.clock.advance(minutes=2)

        with pytest.raises(SystemLockedError) as error:
            app.drawers.open(1002)

        assert error.value.remaining_seconds == 3 * 60

    def test_can_open_again_after_the_lock(self, app):
        app.login_as(Role.SELLER)
        app.drawers.open(1001)
        app.clock.advance(minutes=5)

        assert app.drawers.open(1002).lock_minutes == 5

    def test_disabled_timer_does_not_lock(self, app):
        app.system_lock.disable()
        app.login_as(Role.SELLER)

        assert app.drawers.open(1001).lock_minutes is None
        assert app.drawers.open(1002).lock_minutes is None

    def test_stocker_cannot_open(self, app):
        app.login_as(Role.STOCKER)

        with pytest.raises(PermissionDeniedError, match="abrir"):
            app.drawers.open(1001)

    def test_already_open_drawer(self, app):
        app.login_as(Role.ADMIN)
        app.drawers.open(1001)
        app.system_lock.clear()

        with pytest.raises(DrawerStateError):
            app.drawers.open(1001)

    def test_requires_authentication(self, app):
        with pytest.raises(NotAuthenticatedError):
            app.drawers.open(1001)


class TestClose:
    def test_stocker_closes_without_locking(self, app):
        app.drawers_repo.open.add(1001)
        app.login_as(Role.STOCKER)

        app.drawers.close(1001)

        assert not app.drawers.is_open(1001)
        assert not app.timer.status().locked
        assert app.audit_log.actions()[-1] is AuditAction.DRAWER_CLOSED

    def test_seller_cannot_close(self, app):
        app.drawers_repo.open.add(1001)
        app.login_as(Role.SELLER)

        with pytest.raises(PermissionDeniedError, match="fechar"):
            app.drawers.close(1001)

    def test_closed_drawer(self, app):
        app.login_as(Role.STOCKER)

        with pytest.raises(DrawerStateError):
            app.drawers.close(1001)


class TestHistory:
    def test_drawer_history_is_paginated_newest_first(self, app):
        app.system_lock.disable()
        app.login_as(Role.ADMIN)
        for _ in range(3):
            app.drawers.open(1001)
            app.drawers.close(1001)
        app.drawers.open(1002)

        page = app.drawers.history(1001, page=1, per_page=4)

        assert page.total == 6
        assert page.total_pages == 2
        assert [e.action for e in page.items[:2]] == [DrawerAction.CLOSED, DrawerAction.OPENED]

    def test_all_history_requires_admin(self, app):
        app.login_as(Role.SELLER)

        with pytest.raises(PermissionDeniedError):
            app.drawers.all_history()

    def test_all_history(self, app):
        app.login_as(Role.ADMIN)
        app.drawers.open(1001)

        page = app.drawers.all_history()

        assert page.total == 1
        assert page.items[0].drawer_number == 1001

    def test_technician_cannot_see_drawer_history(self, app):
        app.login_as(Role.TECHNICIAN)

        with pytest.raises(PermissionDeniedError):
            app.drawers.history(1001)
