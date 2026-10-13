import sqlite3

from ...domain.drawers import DrawerAction, DrawerEvent
from .database import Database, parse_timestamp

_HISTORY = """
    SELECT g.numero_gaveta, h.acao, h.data_hora,
           COALESCE(u.nome_completo, u.username) AS actor
    FROM historico_gavetas h
    JOIN gavetas g ON g.id = h.gaveta_id
    LEFT JOIN usuarios u ON u.id = h.usuario_id
"""


def _to_event(row: sqlite3.Row) -> DrawerEvent:
    occurred_at = parse_timestamp(row["data_hora"])
    assert occurred_at is not None
    return DrawerEvent(
        drawer_number=int(row["numero_gaveta"]),
        action=DrawerAction(row["acao"]),
        actor=row["actor"],
        occurred_at=occurred_at,
    )


class SqliteDrawerRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def is_open(self, drawer_number: int) -> bool:
        value = self._db.fetch_value(
            "SELECT esta_aberta FROM gavetas WHERE numero_gaveta = ?", (str(drawer_number),)
        )
        return bool(value)

    def set_open(self, drawer_number: int, is_open: bool, user_id: int) -> None:
        number = str(drawer_number)
        action = DrawerAction.OPENED if is_open else DrawerAction.CLOSED
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO gavetas (numero_gaveta, esta_aberta) VALUES (?, 0)",
                (number,),
            )
            conn.execute(
                "UPDATE gavetas SET esta_aberta = ?, ultima_atualizacao = CURRENT_TIMESTAMP "
                "WHERE numero_gaveta = ?",
                (int(is_open), number),
            )
            conn.execute(
                "INSERT INTO historico_gavetas (gaveta_id, usuario_id, acao) "
                "SELECT id, ?, ? FROM gavetas WHERE numero_gaveta = ?",
                (user_id, action.value, number),
            )

    def history(self, drawer_number: int, offset: int, limit: int) -> list[DrawerEvent]:
        rows = self._db.fetch_all(
            f"{_HISTORY} WHERE g.numero_gaveta = ? "
            "ORDER BY h.data_hora DESC, h.id DESC LIMIT ? OFFSET ?",
            (str(drawer_number), limit, offset),
        )
        return [_to_event(row) for row in rows]

    def count_history(self, drawer_number: int) -> int:
        return int(
            self._db.fetch_value(
                "SELECT COUNT(*) FROM historico_gavetas h "
                "JOIN gavetas g ON g.id = h.gaveta_id WHERE g.numero_gaveta = ?",
                (str(drawer_number),),
            )
        )

    def all_history(self, offset: int, limit: int) -> list[DrawerEvent]:
        rows = self._db.fetch_all(
            f"{_HISTORY} ORDER BY h.data_hora DESC, h.id DESC LIMIT ? OFFSET ?", (limit, offset)
        )
        return [_to_event(row) for row in rows]

    def count_all_history(self) -> int:
        return int(self._db.fetch_value("SELECT COUNT(*) FROM historico_gavetas"))
