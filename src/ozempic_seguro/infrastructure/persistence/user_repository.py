import sqlite3

from ...domain.exceptions import UsernameTakenError
from ...domain.users import Role, User
from .database import Database, parse_timestamp

_COLUMNS = "id, username, nome_completo, tipo, ativo, data_criacao"


def _to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        username=row["username"],
        full_name=row["nome_completo"],
        role=Role(row["tipo"]),
        active=bool(row["ativo"]),
        created_at=parse_timestamp(row["data_criacao"]),
    )


class SqliteUserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def add(self, username: str, password_hash: str, full_name: str, role: Role) -> User:
        try:
            with self._db.transaction() as conn:
                cursor = conn.execute(
                    "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo) "
                    "VALUES (?, ?, ?, ?)",
                    (username, password_hash, full_name, role.value),
                )
        except sqlite3.IntegrityError as e:
            raise UsernameTakenError(username) from e
        user = self.get(int(cursor.lastrowid or 0))
        assert user is not None
        return user

    def get(self, user_id: int) -> User | None:
        row = self._db.fetch_one(f"SELECT {_COLUMNS} FROM usuarios WHERE id = ?", (user_id,))
        return _to_user(row) if row else None

    def get_by_username(self, username: str) -> User | None:
        row = self._db.fetch_one(f"SELECT {_COLUMNS} FROM usuarios WHERE username = ?", (username,))
        return _to_user(row) if row else None

    def get_password_hash(self, user_id: int) -> str | None:
        value = self._db.fetch_value("SELECT senha_hash FROM usuarios WHERE id = ?", (user_id,))
        return str(value) if value is not None else None

    def list_all(self) -> list[User]:
        rows = self._db.fetch_all(f"SELECT {_COLUMNS} FROM usuarios ORDER BY ativo DESC, id")
        return [_to_user(row) for row in rows]

    def set_password_hash(self, user_id: int, password_hash: str) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE id = ?", (password_hash, user_id)
            )

    def deactivate(self, user_id: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (user_id,))

    def count_active(self, role: Role) -> int:
        return int(
            self._db.fetch_value(
                "SELECT COUNT(*) FROM usuarios WHERE tipo = ? AND ativo = 1", (role.value,)
            )
        )
