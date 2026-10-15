"""End-to-end check of the wiring: real SQLite, real bcrypt, every layer together."""

import pytest

from ozempic_seguro.bootstrap import build_services
from ozempic_seguro.domain.audit import AuditAction, AuditFilter
from ozempic_seguro.domain.exceptions import SystemLockedError
from ozempic_seguro.domain.users import Role
from ozempic_seguro.infrastructure.settings import Settings


@pytest.fixture
def services(tmp_path):
    settings = Settings(
        database_path=tmp_path / "app.db",
        bcrypt_rounds=10,
        admin_password="1111",
        technician_password="2222",
    )
    built = build_services(settings)
    yield built
    built.close()


def test_drawer_flow_through_every_layer(services):
    services.auth.login("00", "1111")
    seller = services.users.register("Maria", "10", "1234", Role.SELLER)
    services.auth.logout()

    services.auth.login("10", "1234")
    result = services.drawers.open(1001)
    with pytest.raises(SystemLockedError):
        services.drawers.open(1002)
    services.auth.logout()

    services.auth.login("00", "1111")
    history = services.drawers.all_history()
    log = services.audit.search(AuditFilter(action=AuditAction.DRAWER_OPENED))

    assert result.lock_minutes == 5
    assert history.items[0].actor == "Maria"
    assert log.items[0].actor == seller.username


def test_default_users_are_seeded_once(tmp_path):
    settings = Settings(database_path=tmp_path / "app.db", bcrypt_rounds=10)
    build_services(settings).close()
    services = build_services(settings)

    services.auth.login("00", "admin@2025")

    assert {u.username for u in services.users.list_users()} == {"00", "01"}
    services.close()
