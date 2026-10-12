"""Login, logout and session lifetime."""

from dataclasses import dataclass

from ..domain.audit import AuditAction, AuditTarget
from ..domain.exceptions import AccountLockedError, InvalidCredentialsError
from ..domain.ports import AuditLog, PasswordHasher, UserRepository
from ..domain.users import User
from .state import LoginThrottle, Session, SystemLock


@dataclass(frozen=True, slots=True)
class LoginStatus:
    locked: bool
    remaining_seconds: int
    remaining_attempts: int
    max_attempts: int

    @property
    def has_failed_attempts(self) -> bool:
        return not self.locked and self.remaining_attempts < self.max_attempts


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        audit: AuditLog,
        session: Session,
        throttle: LoginThrottle,
        system_lock: SystemLock,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._audit = audit
        self._session = session
        self._throttle = throttle
        self._system_lock = system_lock

    @property
    def current_user(self) -> User | None:
        return self._session.user

    def login(self, username: str, password: str) -> User:
        """Authenticate and start a session.

        Raises AccountLockedError while the username is throttled and
        InvalidCredentialsError for an unknown user, inactive user or wrong password.
        """
        username = username.strip()

        locked_seconds = self._throttle.locked_seconds(username)
        if locked_seconds:
            self._audit.record(
                AuditAction.LOGIN_BLOCKED, target=AuditTarget.USER, details={"username": username}
            )
            raise AccountLockedError(locked_seconds)

        user = self._authenticate(username, password)
        if user is None:
            self._throttle.register_failure(username)
            self._audit.record(
                AuditAction.LOGIN_FAILED, target=AuditTarget.USER, details={"username": username}
            )
            locked_seconds = self._throttle.locked_seconds(username)
            if locked_seconds:
                raise AccountLockedError(locked_seconds)
            raise InvalidCredentialsError(self._throttle.remaining_attempts(username))

        self._throttle.register_success(username)
        self._session.start(user)
        self._audit.record(
            AuditAction.LOGIN_SUCCESS, user_id=user.id, target=AuditTarget.USER, target_id=user.id
        )
        return user

    def logout(self) -> bool:
        """End the session. Returns True if the drawer timer had to be re-enabled."""
        user = self._session.user
        if user is None:
            return False
        self._audit.record(
            AuditAction.LOGOUT, user_id=user.id, target=AuditTarget.SESSION, target_id=user.id
        )
        self._session.end()
        return self._restore_timer(user)

    def expire_if_idle(self) -> bool:
        """End the session if it has been inactive for too long. Returns True if it expired."""
        user = self._session.user
        if user is None or not self._session.is_expired():
            return False
        self._audit.record(
            AuditAction.SESSION_EXPIRED,
            user_id=user.id,
            target=AuditTarget.SESSION,
            target_id=user.id,
        )
        self._session.end()
        self._restore_timer(user)
        return True

    def touch(self) -> None:
        """Register user activity, postponing the inactivity timeout."""
        self._session.touch()

    def login_status(self, username: str) -> LoginStatus:
        username = username.strip()
        locked_seconds = self._throttle.locked_seconds(username)
        return LoginStatus(
            locked=locked_seconds > 0,
            remaining_seconds=locked_seconds,
            remaining_attempts=self._throttle.remaining_attempts(username),
            max_attempts=self._throttle.max_attempts,
        )

    def _authenticate(self, username: str, password: str) -> User | None:
        if not username or not password:
            return None
        user = self._users.get_by_username(username)
        if user is None or not user.active:
            return None
        password_hash = self._users.get_password_hash(user.id)
        if password_hash is None or not self._hasher.verify(password, password_hash):
            return None
        return user

    def _restore_timer(self, user: User) -> bool:
        # A technician may disable the drawer timer for maintenance; it must not
        # stay disabled once the session is over.
        if self._system_lock.enabled:
            return False
        self._system_lock.enable()
        self._audit.record(
            AuditAction.TIMER_ENABLED,
            user_id=user.id,
            target=AuditTarget.SYSTEM,
            details={"reason": "session_end"},
        )
        return True
