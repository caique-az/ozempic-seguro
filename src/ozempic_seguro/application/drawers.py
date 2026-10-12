"""Opening, closing and inspecting medication drawers."""

from dataclasses import dataclass

from ..domain.audit import AuditAction, AuditTarget
from ..domain.drawers import DrawerEvent
from ..domain.exceptions import DrawerStateError, SystemLockedError
from ..domain.permissions import Permission, opening_locks_system, require
from ..domain.ports import AuditLog, DrawerRepository
from .pagination import Page, offset_for
from .state import Session, SystemLock


@dataclass(frozen=True, slots=True)
class OpenResult:
    drawer_number: int
    lock_minutes: int | None
    """Minutes the system was locked for after this opening, or None if it was not locked."""


class DrawerService:
    def __init__(
        self,
        drawers: DrawerRepository,
        audit: AuditLog,
        session: Session,
        system_lock: SystemLock,
        lock_minutes: int,
    ) -> None:
        self._drawers = drawers
        self._audit = audit
        self._session = session
        self._system_lock = system_lock
        self._lock_minutes = lock_minutes

    def is_open(self, drawer_number: int) -> bool:
        self._session.require_user()
        return self._drawers.is_open(drawer_number)

    def open(self, drawer_number: int) -> OpenResult:
        user = self._session.require_user()
        require(user, Permission.OPEN_DRAWER)

        locks = opening_locks_system(user.role)
        if locks:
            remaining = self._system_lock.remaining_seconds()
            if remaining:
                raise SystemLockedError(remaining)

        if self._drawers.is_open(drawer_number):
            raise DrawerStateError(f"A gaveta {drawer_number} já está aberta")

        self._drawers.set_open(drawer_number, True, user.id)
        self._audit.record(
            AuditAction.DRAWER_OPENED,
            user_id=user.id,
            target=AuditTarget.DRAWER,
            target_id=drawer_number,
        )

        locked = locks and self._system_lock.lock(self._lock_minutes)
        return OpenResult(drawer_number, self._lock_minutes if locked else None)

    def close(self, drawer_number: int) -> None:
        user = self._session.require_user()
        require(user, Permission.CLOSE_DRAWER)

        if not self._drawers.is_open(drawer_number):
            raise DrawerStateError(f"A gaveta {drawer_number} já está fechada")

        self._drawers.set_open(drawer_number, False, user.id)
        self._audit.record(
            AuditAction.DRAWER_CLOSED,
            user_id=user.id,
            target=AuditTarget.DRAWER,
            target_id=drawer_number,
        )

    def history(self, drawer_number: int, page: int = 1, per_page: int = 20) -> Page[DrawerEvent]:
        require(self._session.require_user(), Permission.VIEW_DRAWER_HISTORY)
        items = self._drawers.history(drawer_number, offset_for(page, per_page), per_page)
        return Page(items, self._drawers.count_history(drawer_number), page, per_page)

    def all_history(self, page: int = 1, per_page: int = 20) -> Page[DrawerEvent]:
        require(self._session.require_user(), Permission.VIEW_ALL_HISTORY)
        items = self._drawers.all_history(offset_for(page, per_page), per_page)
        return Page(items, self._drawers.count_all_history(), page, per_page)
