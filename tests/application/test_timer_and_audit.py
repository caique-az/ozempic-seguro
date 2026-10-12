from datetime import date

import pytest

from ozempic_seguro.application.audit import AuditService
from ozempic_seguro.domain.audit import AuditAction, AuditFilter
from ozempic_seguro.domain.exceptions import NotAuthenticatedError, PermissionDeniedError
from ozempic_seguro.domain.users import Role


class TestTimer:
    def test_status_reflects_the_lock(self, app):
        app.login_as(Role.SELLER)
        app.drawers.open(1001)
        app.clock.advance(seconds=30)

        status = app.timer.status()

        assert status.enabled
        assert status.locked
        assert status.remaining_display == "4:30"

    def test_technician_toggles_the_timer(self, app):
        app.login_as(Role.TECHNICIAN)

        app.timer.disable()
        assert not app.timer.status().enabled
        app.timer.enable()
        assert app.timer.status().enabled

        assert app.audit_log.actions()[-2:] == [
            AuditAction.TIMER_DISABLED,
            AuditAction.TIMER_ENABLED,
        ]

    def test_toggling_to_the_current_state_is_not_audited(self, app):
        app.login_as(Role.TECHNICIAN)
        before = len(app.audit_log.records)

        app.timer.enable()

        assert len(app.audit_log.records) == before

    def test_disabling_lifts_an_active_lock(self, app):
        app.login_as(Role.SELLER)
        app.drawers.open(1001)
        app.auth.logout()
        app.login_as(Role.TECHNICIAN)

        app.timer.disable()

        assert not app.timer.status().locked

    def test_seller_cannot_toggle(self, app):
        app.login_as(Role.SELLER)

        with pytest.raises(PermissionDeniedError):
            app.timer.disable()

    def test_only_admin_clears_the_lock(self, app):
        app.login_as(Role.ADMIN)
        app.drawers.open(1001)

        app.timer.clear_lock()

        assert not app.timer.status().locked
        assert app.audit_log.actions()[-1] is AuditAction.SYSTEM_LOCK_CLEARED

        app.auth.logout()
        app.login_as(Role.TECHNICIAN)
        with pytest.raises(PermissionDeniedError):
            app.timer.clear_lock()

    def test_requires_authentication(self, app):
        with pytest.raises(NotAuthenticatedError):
            app.timer.enable()


class TestAuditQuery:
    def test_admin_searches_with_filter_and_pagination(self, app):
        app.login_as(Role.ADMIN)
        app.drawers.open(1001)

        page = app.audit.search(AuditFilter(action=AuditAction.DRAWER_OPENED), per_page=10)

        assert page.total == 1
        assert page.items[0].action_label == "Gaveta aberta"

    def test_requires_admin(self, app):
        app.login_as(Role.SELLER)

        with pytest.raises(PermissionDeniedError):
            app.audit.search(AuditFilter())

    def test_last_days_filter(self):
        criteria = AuditService.last_days(date(2026, 1, 15))

        assert (criteria.start, criteria.end) == (date(2026, 1, 8), date(2026, 1, 15))
        assert criteria.action is None
