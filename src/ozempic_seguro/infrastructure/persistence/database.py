"""SQLite connection, transactions and schema migrations."""

import logging
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ...paths import MIGRATIONS_DIR

logger = logging.getLogger(__name__)

IN_MEMORY = ":memory:"

type Params = Sequence[Any]


class MigrationError(RuntimeError):
    pass


class Database:
    """A single SQLite connection used from the UI thread.

    Every write goes through `transaction()`, which commits on success and rolls
    back on any exception.
    """

    def __init__(self, path: Path | str, migrations_dir: Path = MIGRATIONS_DIR) -> None:
        if str(path) != IN_MEMORY:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, timeout=30.0)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        if str(path) != IN_MEMORY:
            self._conn.execute("PRAGMA journal_mode = WAL")
        try:
            self._migrate(migrations_dir)
        except BaseException:
            self._conn.close()
            raise

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self._conn
        except BaseException:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def fetch_one(self, sql: str, params: Params = ()) -> sqlite3.Row | None:
        row: sqlite3.Row | None = self._conn.execute(sql, params).fetchone()
        return row

    def fetch_all(self, sql: str, params: Params = ()) -> list[sqlite3.Row]:
        return self._conn.execute(sql, params).fetchall()

    def fetch_value(self, sql: str, params: Params = ()) -> Any:
        row = self._conn.execute(sql, params).fetchone()
        return row[0] if row else None

    def applied_migrations(self) -> list[int]:
        return [row[0] for row in self._conn.execute("SELECT version FROM migrations ORDER BY 1")]

    def _migrate(self, migrations_dir: Path) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()
        applied = set(self.applied_migrations())

        for script in sorted(migrations_dir.glob("*.sql")):
            version = int(script.name.split("_", 1)[0])
            if version in applied:
                continue
            logger.info("Applying migration %s", script.name)
            try:
                # executescript commits any pending transaction and runs in autocommit
                # mode, so the version row is written right after the script succeeds.
                self._conn.executescript(script.read_text(encoding="utf-8"))
                self._conn.execute(
                    "INSERT INTO migrations (version, name) VALUES (?, ?)", (version, script.name)
                )
                self._conn.commit()
            except sqlite3.Error as e:
                self._conn.rollback()
                raise MigrationError(f"Migration {script.name} failed: {e}") from e


def parse_timestamp(value: str | None) -> datetime | None:
    """Convert a SQLite CURRENT_TIMESTAMP value (UTC) to naive local time."""
    if not value:
        return None
    utc = datetime.fromisoformat(value).replace(tzinfo=UTC)
    return utc.astimezone().replace(tzinfo=None)


def to_utc_text(local: datetime) -> str:
    """Format a naive local datetime the way SQLite stores CURRENT_TIMESTAMP."""
    return local.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")
