import pytest

from ozempic_seguro.application.state import LoginThrottle, Session, SystemLock
from ozempic_seguro.domain.exceptions import NotAuthenticatedError
from ozempic_seguro.domain.users import Role, User

USER = User(1, "10", "Ana", Role.SELLER)


@pytest.fixture
def clock(app):
    return app.clock


class TestSession:
    def test_require_user_without_session(self, clock):
        with pytest.raises(NotAuthenticatedError):
            Session(clock, 10).require_user()

    def test_touch_without_session_is_ignored(self, clock):
        session = Session(clock, 10)
        session.touch()

        assert session.user is None
        assert not session.is_expired()

    def test_expires_exactly_at_timeout(self, clock):
        session = Session(clock, 10)
        session.start(USER)

        clock.advance(minutes=10)

        assert session.is_expired()


class TestLoginThrottle:
    def test_failures_below_the_limit_do_not_lock(self, clock):
        throttle = LoginThrottle(clock, max_attempts=3, lockout_minutes=5)
        throttle.register_failure("10")
        throttle.register_failure("10")

        assert throttle.locked_seconds("10") == 0
        assert throttle.remaining_attempts("10") == 1

    def test_usernames_are_tracked_independently(self, clock):
        throttle = LoginThrottle(clock, max_attempts=1, lockout_minutes=5)
        throttle.register_failure("10")

        assert throttle.locked_seconds("10") == 300
        assert throttle.locked_seconds("20") == 0


class TestSystemLock:
    def test_lock_is_refused_while_disabled(self, clock):
        lock = SystemLock(clock)
        lock.disable()

        assert lock.lock(5) is False
        assert not lock.is_locked()

    def test_lock_expires(self, clock):
        lock = SystemLock(clock)
        lock.lock(5)
        clock.advance(minutes=5)

        assert not lock.is_locked()
        assert lock.remaining_seconds() == 0

    def test_re_enabling_restores_a_pending_lock(self, clock):
        lock = SystemLock(clock)
        lock.lock(5)
        lock.disable()
        assert not lock.is_locked()

        lock.enable()

        assert lock.remaining_seconds() == 300
