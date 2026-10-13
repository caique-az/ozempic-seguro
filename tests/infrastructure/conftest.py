import pytest

from ozempic_seguro.infrastructure.persistence.audit_repository import SqliteAuditRepository
from ozempic_seguro.infrastructure.persistence.database import Database
from ozempic_seguro.infrastructure.persistence.drawer_repository import SqliteDrawerRepository
from ozempic_seguro.infrastructure.persistence.user_repository import SqliteUserRepository
from ozempic_seguro.infrastructure.system import BcryptPasswordHasher


@pytest.fixture
def db(tmp_path):
    database = Database(tmp_path / "test.db")
    yield database
    database.close()


@pytest.fixture
def users(db):
    return SqliteUserRepository(db)


@pytest.fixture
def drawers(db):
    return SqliteDrawerRepository(db)


@pytest.fixture
def audit(db):
    return SqliteAuditRepository(db, origin="test-host")


@pytest.fixture
def hasher():
    # Minimum cost keeps the suite fast; production uses Settings.bcrypt_rounds.
    return BcryptPasswordHasher(rounds=4)
