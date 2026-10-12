"""Role-based access control: which profile may perform which action."""

from enum import StrEnum

from .exceptions import PermissionDeniedError
from .users import Role, User


class Permission(StrEnum):
    OPEN_DRAWER = "open_drawer"
    CLOSE_DRAWER = "close_drawer"
    VIEW_DRAWER_HISTORY = "view_drawer_history"
    VIEW_ALL_HISTORY = "view_all_history"
    VIEW_AUDIT = "view_audit"
    MANAGE_USERS = "manage_users"
    CONTROL_TIMER = "control_timer"
    CLEAR_SYSTEM_LOCK = "clear_system_lock"
    RUN_DIAGNOSTICS = "run_diagnostics"


_GRANTS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(
        {
            Permission.OPEN_DRAWER,
            Permission.CLOSE_DRAWER,
            Permission.VIEW_DRAWER_HISTORY,
            Permission.VIEW_ALL_HISTORY,
            Permission.VIEW_AUDIT,
            Permission.MANAGE_USERS,
            Permission.CONTROL_TIMER,
            Permission.CLEAR_SYSTEM_LOCK,
            Permission.RUN_DIAGNOSTICS,
        }
    ),
    Role.SELLER: frozenset({Permission.OPEN_DRAWER, Permission.VIEW_DRAWER_HISTORY}),
    Role.STOCKER: frozenset({Permission.CLOSE_DRAWER, Permission.VIEW_DRAWER_HISTORY}),
    Role.TECHNICIAN: frozenset({Permission.CONTROL_TIMER, Permission.RUN_DIAGNOSTICS}),
}

# Opening a drawer as one of these roles locks the system for a while, so a
# second drawer cannot be opened right after the first one.
_ROLES_THAT_LOCK_ON_OPEN = frozenset({Role.ADMIN, Role.SELLER})

_DENIED_MESSAGES = {
    Permission.OPEN_DRAWER: "Você não tem permissão para abrir gavetas",
    Permission.CLOSE_DRAWER: "Você não tem permissão para fechar gavetas",
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in _GRANTS[role]


def require(user: User, permission: Permission) -> None:
    if not has_permission(user.role, permission):
        raise PermissionDeniedError(
            _DENIED_MESSAGES.get(permission, "Você não tem permissão para esta operação")
        )


def opening_locks_system(role: Role) -> bool:
    return role in _ROLES_THAT_LOCK_ON_OPEN
