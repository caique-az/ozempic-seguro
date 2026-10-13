"""Composition root: the only module that knows every layer and wires them together."""

import socket
from dataclasses import dataclass

from .application.audit import AuditService
from .application.auth import AuthService
from .application.drawers import DrawerService
from .application.state import LoginThrottle, Session, SystemLock
from .application.timer import TimerService
from .application.users import UserService
from .domain.ports import Clock
from .infrastructure.persistence.audit_repository import SqliteAuditRepository
from .infrastructure.persistence.database import Database
from .infrastructure.persistence.drawer_repository import SqliteDrawerRepository
from .infrastructure.persistence.seed import ensure_default_users
from .infrastructure.persistence.user_repository import SqliteUserRepository
from .infrastructure.settings import Settings
from .infrastructure.system import BcryptPasswordHasher, SystemClock


@dataclass(frozen=True, slots=True)
class Services:
    """Use cases handed to the presentation layer."""

    settings: Settings
    auth: AuthService
    drawers: DrawerService
    users: UserService
    audit: AuditService
    timer: TimerService
    database: Database

    def close(self) -> None:
        self.database.close()


def build_services(settings: Settings, clock: Clock | None = None) -> Services:
    clock = clock or SystemClock()
    database = Database(settings.database_path)
    hasher = BcryptPasswordHasher(settings.bcrypt_rounds)

    users = SqliteUserRepository(database)
    drawers = SqliteDrawerRepository(database)
    audit = SqliteAuditRepository(database, origin=socket.gethostname())
    ensure_default_users(users, hasher, settings)

    session = Session(clock, settings.session_timeout_minutes)
    throttle = LoginThrottle(clock, settings.max_login_attempts, settings.lockout_minutes)
    system_lock = SystemLock(clock)

    return Services(
        settings=settings,
        auth=AuthService(users, hasher, audit, session, throttle, system_lock),
        drawers=DrawerService(drawers, audit, session, system_lock, settings.drawer_lock_minutes),
        users=UserService(users, hasher, audit, session),
        audit=AuditService(audit, session),
        timer=TimerService(system_lock, audit, session),
        database=database,
    )
