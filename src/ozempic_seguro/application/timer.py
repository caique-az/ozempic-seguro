"""Control of the post-opening system lock (the drawer "timer")."""

from dataclasses import dataclass

from ..domain.audit import AuditAction, AuditTarget
from ..domain.permissions import Permission, require
from ..domain.ports import AuditLog
from .state import Session, SystemLock


@dataclass(frozen=True, slots=True)
class TimerStatus:
    enabled: bool
    remaining_seconds: int

    @property
    def locked(self) -> bool:
        return self.remaining_seconds > 0

    @property
    def remaining_display(self) -> str:
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes}:{seconds:02d}"


class TimerService:
    def __init__(self, system_lock: SystemLock, audit: AuditLog, session: Session) -> None:
        self._lock = system_lock
        self._audit = audit
        self._session = session

    def status(self) -> TimerStatus:
        return TimerStatus(self._lock.enabled, self._lock.remaining_seconds())

    def enable(self) -> None:
        self._set_enabled(True)

    def disable(self) -> None:
        self._set_enabled(False)

    def clear_lock(self) -> None:
        user = self._session.require_user()
        require(user, Permission.CLEAR_SYSTEM_LOCK)
        self._lock.clear()
        self._audit.record(
            AuditAction.SYSTEM_LOCK_CLEARED, user_id=user.id, target=AuditTarget.SYSTEM
        )

    def _set_enabled(self, enabled: bool) -> None:
        user = self._session.require_user()
        require(user, Permission.CONTROL_TIMER)
        if enabled == self._lock.enabled:
            return
        if enabled:
            self._lock.enable()
        else:
            self._lock.disable()
        self._audit.record(
            AuditAction.TIMER_ENABLED if enabled else AuditAction.TIMER_DISABLED,
            user_id=user.id,
            target=AuditTarget.SYSTEM,
        )
