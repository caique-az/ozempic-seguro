"""In-memory runtime state shared by the use cases.

Time always comes from an injected Clock, so expiry rules are testable without sleeping
and nothing runs on background threads (Tkinter is not thread-safe).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..domain.exceptions import NotAuthenticatedError
from ..domain.ports import Clock
from ..domain.users import User


class Session:
    """The authenticated user and their inactivity deadline."""

    def __init__(self, clock: Clock, timeout_minutes: int) -> None:
        self._clock = clock
        self._timeout = timedelta(minutes=timeout_minutes)
        self._user: User | None = None
        self._last_activity: datetime | None = None

    @property
    def user(self) -> User | None:
        return self._user

    def require_user(self) -> User:
        if self._user is None:
            raise NotAuthenticatedError()
        return self._user

    def start(self, user: User) -> None:
        self._user = user
        self._last_activity = self._clock.now()

    def end(self) -> None:
        self._user = None
        self._last_activity = None

    def touch(self) -> None:
        if self._user is not None:
            self._last_activity = self._clock.now()

    def is_expired(self) -> bool:
        if self._user is None or self._last_activity is None:
            return False
        return self._clock.now() - self._last_activity >= self._timeout


@dataclass
class _Attempts:
    failures: int = 0
    locked_until: datetime | None = None


class LoginThrottle:
    """Brute-force protection: lock a username after too many failed logins."""

    def __init__(self, clock: Clock, max_attempts: int, lockout_minutes: int) -> None:
        self._clock = clock
        self._max_attempts = max_attempts
        self._lockout = timedelta(minutes=lockout_minutes)
        self._attempts: dict[str, _Attempts] = {}

    @property
    def max_attempts(self) -> int:
        return self._max_attempts

    def locked_seconds(self, username: str) -> int:
        """Seconds until the username can try again; 0 when it is not locked."""
        attempts = self._attempts.get(username)
        if attempts is None or attempts.locked_until is None:
            return 0
        remaining = (attempts.locked_until - self._clock.now()).total_seconds()
        if remaining <= 0:
            del self._attempts[username]
            return 0
        return int(remaining)

    def remaining_attempts(self, username: str) -> int:
        attempts = self._attempts.get(username)
        failures = attempts.failures if attempts else 0
        return max(0, self._max_attempts - failures)

    def register_failure(self, username: str) -> None:
        attempts = self._attempts.setdefault(username, _Attempts())
        attempts.failures += 1
        if attempts.failures >= self._max_attempts:
            attempts.locked_until = self._clock.now() + self._lockout

    def register_success(self, username: str) -> None:
        self._attempts.pop(username, None)


class SystemLock:
    """Temporary lock applied after a drawer is opened (the "timer")."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._enabled = True
        self._locked_until: datetime | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def remaining_seconds(self) -> int:
        if not self._enabled or self._locked_until is None:
            return 0
        remaining = (self._locked_until - self._clock.now()).total_seconds()
        if remaining <= 0:
            self._locked_until = None
            return 0
        return int(remaining)

    def is_locked(self) -> bool:
        return self.remaining_seconds() > 0

    def lock(self, minutes: int) -> bool:
        """Start a lock; returns False when the timer is disabled."""
        if not self._enabled:
            return False
        self._locked_until = self._clock.now() + timedelta(minutes=minutes)
        return True

    def clear(self) -> None:
        self._locked_until = None
