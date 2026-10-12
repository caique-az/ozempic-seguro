import pytest

from ozempic_seguro.domain.exceptions import PermissionDeniedError
from ozempic_seguro.domain.permissions import (
    Permission,
    has_permission,
    opening_locks_system,
    require,
)
from ozempic_seguro.domain.users import Role, User

P = Permission

EXPECTED_GRANTS = {
    Role.ADMIN: set(Permission),
    Role.SELLER: {P.OPEN_DRAWER, P.VIEW_DRAWER_HISTORY},
    Role.STOCKER: {P.CLOSE_DRAWER, P.VIEW_DRAWER_HISTORY},
    Role.TECHNICIAN: {P.CONTROL_TIMER, P.RUN_DIAGNOSTICS},
}


@pytest.mark.parametrize("role", list(Role))
def test_permission_matrix(role):
    granted = {p for p in Permission if has_permission(role, p)}
    assert granted == EXPECTED_GRANTS[role]


def test_require_passes_when_granted():
    require(User(1, "10", "Ana", Role.SELLER), Permission.OPEN_DRAWER)


@pytest.mark.parametrize(
    ("role", "permission", "message"),
    [
        (Role.SELLER, P.CLOSE_DRAWER, "Você não tem permissão para fechar gavetas"),
        (Role.STOCKER, P.OPEN_DRAWER, "Você não tem permissão para abrir gavetas"),
        (Role.SELLER, P.MANAGE_USERS, "Você não tem permissão para esta operação"),
    ],
)
def test_require_raises_with_a_message_for_the_user(role, permission, message):
    with pytest.raises(PermissionDeniedError, match=message):
        require(User(1, "10", "Ana", role), permission)


@pytest.mark.parametrize(
    ("role", "locks"),
    [(Role.ADMIN, True), (Role.SELLER, True), (Role.STOCKER, False), (Role.TECHNICIAN, False)],
)
def test_opening_locks_system(role, locks):
    assert opening_locks_system(role) is locks
