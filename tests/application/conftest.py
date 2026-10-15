"""In-memory fakes for the domain ports and a fully wired set of use cases."""

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any

import pytest

from ozempic_seguro.application.audit import AuditService
from ozempic_seguro.application.auth import AuthService
from ozempic_seguro.application.drawers import DrawerService
from ozempic_seguro.application.state import LoginThrottle, Session, SystemLock
from ozempic_seguro.application.timer import TimerService
from ozempic_seguro.application.users import UserService
from ozempic_seguro.domain.audit import AuditAction, AuditEntry, AuditFilter, AuditTarget
from ozempic_seguro.domain.drawers import DrawerAction, DrawerEvent
from ozempic_seguro.domain.exceptions import UsernameTakenError
from ozempic_seguro.domain.users import Role, User

SESSION_TIMEOUT_MINUTES = 10
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
DRAWER_LOCK_MINUTES = 5


class FakeClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 1, 15, 9, 0, 0)

    def now(self) -> datetime:
        return self.current

    def advance(self, **delta: float) -> None:
        self.current += timedelta(**delta)


class FakeHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.hashes: dict[int, str] = {}

    def add(self, username: str, password_hash: str, full_name: str, role: Role) -> User:
        if self.get_by_username(username):
            raise UsernameTakenError(username)
        user = User(len(self.users) + 1, username, full_name, role)
        self.users[user.id] = user
        self.hashes[user.id] = password_hash
        return user

    def get(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self.users.values() if u.username == username), None)

    def get_password_hash(self, user_id: int) -> str | None:
        return self.hashes.get(user_id)

    def list_all(self) -> list[User]:
        return list(self.users.values())

    def set_password_hash(self, user_id: int, password_hash: str) -> None:
        self.hashes[user_id] = password_hash

    def deactivate(self, user_id: int) -> None:
        self.users[user_id] = replace(self.users[user_id], active=False)

    def count_active(self, role: Role) -> int:
        return sum(1 for u in self.users.values() if u.role is role and u.active)


class InMemoryDrawerRepository:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.open: set[int] = set()
        self.events: list[DrawerEvent] = []

    def is_open(self, drawer_number: int) -> bool:
        return drawer_number in self.open

    def set_open(self, drawer_number: int, is_open: bool, user_id: int) -> None:
        (self.open.add if is_open else self.open.discard)(drawer_number)
        action = DrawerAction.OPENED if is_open else DrawerAction.CLOSED
        self.events.insert(0, DrawerEvent(drawer_number, action, str(user_id), self.clock.now()))

    def history(self, drawer_number: int, offset: int, limit: int) -> list[DrawerEvent]:
        events = [e for e in self.events if e.drawer_number == drawer_number]
        return events[offset : offset + limit]

    def count_history(self, drawer_number: int) -> int:
        return sum(1 for e in self.events if e.drawer_number == drawer_number)

    def all_history(self, offset: int, limit: int) -> list[DrawerEvent]:
        return self.events[offset : offset + limit]

    def count_all_history(self) -> int:
        return len(self.events)


@dataclass
class RecordedAudit:
    action: AuditAction
    user_id: int | None
    target: AuditTarget | None
    target_id: int | None
    details: dict[str, Any] | None


class InMemoryAuditLog:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.records: list[RecordedAudit] = []

    def record(
        self,
        action: AuditAction,
        *,
        user_id: int | None = None,
        target: AuditTarget | None = None,
        target_id: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.records.append(RecordedAudit(action, user_id, target, target_id, details))

    def actions(self) -> list[AuditAction]:
        return [r.action for r in self.records]

    def _matching(self, criteria: AuditFilter) -> list[AuditEntry]:
        entries = [
            AuditEntry(i, self.clock.now(), r.action.value, None, None, None, r.details, None)
            for i, r in enumerate(self.records, start=1)
        ]
        if criteria.action:
            entries = [e for e in entries if e.action == criteria.action.value]
        return entries

    def search(self, criteria: AuditFilter, offset: int, limit: int) -> list[AuditEntry]:
        return self._matching(criteria)[offset : offset + limit]

    def count(self, criteria: AuditFilter) -> int:
        return len(self._matching(criteria))


@dataclass
class App:
    clock: FakeClock
    users_repo: InMemoryUserRepository
    drawers_repo: InMemoryDrawerRepository
    audit_log: InMemoryAuditLog
    session: Session
    throttle: LoginThrottle
    system_lock: SystemLock
    auth: AuthService
    drawers: DrawerService
    users: UserService
    audit: AuditService
    timer: TimerService
    accounts: dict[Role, User] = field(default_factory=dict)

    def login_as(self, role: Role) -> User:
        user = self.accounts[role]
        return self.auth.login(user.username, "1234")


@pytest.fixture
def app() -> App:
    clock = FakeClock()
    hasher = FakeHasher()
    users_repo = InMemoryUserRepository()
    drawers_repo = InMemoryDrawerRepository(clock)
    audit_log = InMemoryAuditLog(clock)
    session = Session(clock, SESSION_TIMEOUT_MINUTES)
    throttle = LoginThrottle(clock, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES)
    system_lock = SystemLock(clock)

    accounts = {
        role: users_repo.add(username, hasher.hash("1234"), role.label, role)
        for username, role in [
            ("00", Role.ADMIN),
            ("10", Role.SELLER),
            ("20", Role.STOCKER),
            ("01", Role.TECHNICIAN),
        ]
    }

    return App(
        clock=clock,
        users_repo=users_repo,
        drawers_repo=drawers_repo,
        audit_log=audit_log,
        session=session,
        throttle=throttle,
        system_lock=system_lock,
        auth=AuthService(users_repo, hasher, audit_log, session, throttle, system_lock),
        drawers=DrawerService(drawers_repo, audit_log, session, system_lock, DRAWER_LOCK_MINUTES),
        users=UserService(users_repo, hasher, audit_log, session),
        audit=AuditService(audit_log, session),
        timer=TimerService(system_lock, audit_log, session),
        accounts=accounts,
    )
