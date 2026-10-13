import sqlite3

import pytest

from ozempic_seguro.infrastructure.persistence.database import (
    IN_MEMORY,
    Database,
    MigrationError,
    parse_timestamp,
    to_utc_text,
)


def test_applies_every_migration_once(tmp_path):
    path = tmp_path / "app.db"
    Database(path).close()
    db = Database(path)

    assert db.applied_migrations() == [1, 2]
    tables = {row[0] for row in db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"usuarios", "gavetas", "historico_gavetas", "auditoria"} <= tables
    db.close()


def test_creates_parent_directory(tmp_path):
    Database(tmp_path / "nested" / "dir" / "app.db").close()

    assert (tmp_path / "nested" / "dir" / "app.db").exists()


def test_in_memory_database():
    db = Database(IN_MEMORY)

    assert db.fetch_value("SELECT COUNT(*) FROM usuarios") == 0
    db.close()


def test_enforces_foreign_keys(db):
    with pytest.raises(sqlite3.IntegrityError), db.transaction() as conn:
        conn.execute("INSERT INTO historico_gavetas (gaveta_id, acao) VALUES (999, 'aberta')")


def test_transaction_rolls_back_on_error(db):
    def insert_then_fail():
        with db.transaction() as conn:
            conn.execute("INSERT INTO gavetas (numero_gaveta) VALUES ('1001')")
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        insert_then_fail()

    assert db.fetch_value("SELECT COUNT(*) FROM gavetas") == 0


def test_failed_migration_raises(tmp_path):
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_broken.sql").write_text("CREATE TABLE (", encoding="utf-8")

    with pytest.raises(MigrationError, match="001_broken.sql"):
        Database(IN_MEMORY, migrations_dir=migrations)


def test_timestamps_round_trip_between_local_and_utc():
    stored = to_utc_text(parse_timestamp("2026-01-15 12:30:00"))

    assert stored == "2026-01-15 12:30:00"
    assert parse_timestamp(None) is None
