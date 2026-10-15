import pytest

from ozempic_seguro.domain.audit import AuditAction
from ozempic_seguro.domain.exceptions import AccountLockedError, InvalidCredentialsError
from ozempic_seguro.domain.users import Role


class TestLogin:
    def test_success_starts_session_and_is_audited(self, app):
        user = app.auth.login(" 10 ", "1234")

        assert user.role is Role.SELLER
        assert app.auth.current_user == user
        assert app.audit_log.actions() == [AuditAction.LOGIN_SUCCESS]
        assert app.audit_log.records[0].user_id == user.id

    @pytest.mark.parametrize(
        ("username", "password"),
        [("10", "9999"), ("99", "1234"), ("", "1234"), ("10", "")],
    )
    def test_rejects_invalid_credentials(self, app, username, password):
        with pytest.raises(InvalidCredentialsError):
            app.auth.login(username, password)

        assert app.auth.current_user is None
        assert app.audit_log.actions() == [AuditAction.LOGIN_FAILED]

    def test_rejects_inactive_user(self, app):
        app.users_repo.deactivate(app.accounts[Role.SELLER].id)

        with pytest.raises(InvalidCredentialsError):
            app.auth.login("10", "1234")

    def test_each_failure_counts_once(self, app):
        # Regression: failures used to be registered twice per attempt, locking
        # the account on the second wrong password instead of the third.
        with pytest.raises(InvalidCredentialsError) as first:
            app.auth.login("10", "0000")
        with pytest.raises(InvalidCredentialsError) as second:
            app.auth.login("10", "0000")

        assert first.value.remaining_attempts == 2
        assert second.value.remaining_attempts == 1

    def test_locks_after_max_attempts(self, app):
        for _ in range(2):
            with pytest.raises(InvalidCredentialsError):
                app.auth.login("10", "0000")

        with pytest.raises(AccountLockedError) as locked:
            app.auth.login("10", "0000")

        assert locked.value.remaining_seconds == 5 * 60

    def test_locked_account_rejects_even_the_right_password(self, app):
        for _ in range(3):
            with pytest.raises((InvalidCredentialsError, AccountLockedError)):
                app.auth.login("10", "0000")

        with pytest.raises(AccountLockedError):
            app.auth.login("10", "1234")

        assert app.audit_log.actions()[-1] is AuditAction.LOGIN_BLOCKED

    def test_lock_expires(self, app):
        for _ in range(3):
            with pytest.raises((InvalidCredentialsError, AccountLockedError)):
                app.auth.login("10", "0000")

        app.clock.advance(minutes=5)

        assert app.auth.login("10", "1234").username == "10"

    def test_success_resets_failures(self, app):
        with pytest.raises(InvalidCredentialsError):
            app.auth.login("10", "0000")
        app.auth.login("10", "1234")

        assert app.auth.login_status("10").remaining_attempts == 3


class TestLoginStatus:
    def test_fresh_username(self, app):
        status = app.auth.login_status("10")

        assert not status.locked
        assert not status.has_failed_attempts
        assert status.remaining_attempts == status.max_attempts == 3

    def test_after_a_failure(self, app):
        with pytest.raises(InvalidCredentialsError):
            app.auth.login("10", "0000")

        status = app.auth.login_status("10")
        assert status.has_failed_attempts
        assert status.remaining_attempts == 2

    def test_while_locked(self, app):
        for _ in range(3):
            with pytest.raises((InvalidCredentialsError, AccountLockedError)):
                app.auth.login("10", "0000")
        app.clock.advance(seconds=60)

        status = app.auth.login_status("10")
        assert status.locked
        assert status.remaining_seconds == 4 * 60
        assert not status.has_failed_attempts


class TestLogout:
    def test_ends_session_and_is_audited(self, app):
        app.login_as(Role.SELLER)

        assert app.auth.logout() is False
        assert app.auth.current_user is None
        assert app.audit_log.actions()[-1] is AuditAction.LOGOUT

    def test_without_session_does_nothing(self, app):
        assert app.auth.logout() is False
        assert app.audit_log.actions() == []

    def test_re_enables_the_timer(self, app):
        app.login_as(Role.TECHNICIAN)
        app.timer.disable()

        assert app.auth.logout() is True
        assert app.timer.status().enabled
        assert app.audit_log.actions()[-2:] == [AuditAction.LOGOUT, AuditAction.TIMER_ENABLED]


class TestInactivity:
    def test_session_expires_after_timeout(self, app):
        app.login_as(Role.SELLER)
        app.clock.advance(minutes=9)
        assert app.auth.expire_if_idle() is False

        app.clock.advance(minutes=1)
        assert app.auth.expire_if_idle() is True
        assert app.auth.current_user is None
        assert app.audit_log.actions()[-1] is AuditAction.SESSION_EXPIRED

    def test_activity_postpones_expiry(self, app):
        app.login_as(Role.SELLER)
        app.clock.advance(minutes=9)
        app.auth.touch()
        app.clock.advance(minutes=9)

        assert app.auth.expire_if_idle() is False

    def test_expiry_re_enables_the_timer(self, app):
        app.login_as(Role.TECHNICIAN)
        app.timer.disable()
        app.clock.advance(minutes=10)

        app.auth.expire_if_idle()

        assert app.timer.status().enabled

    def test_no_session_never_expires(self, app):
        app.clock.advance(hours=1)
        assert app.auth.expire_if_idle() is False
