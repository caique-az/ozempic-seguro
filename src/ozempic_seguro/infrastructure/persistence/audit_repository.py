import json
import sqlite3
from datetime import datetime, time, timedelta
from typing import Any

from ...domain.audit import AuditAction, AuditEntry, AuditFilter, AuditTarget
from .database import Database, Params, parse_timestamp, to_utc_text


def _to_entry(row: sqlite3.Row) -> AuditEntry:
    occurred_at = parse_timestamp(row["data_hora"])
    assert occurred_at is not None
    # Older versions stored the context in either column.
    raw_details = row["dados_novos"] or row["dados_anteriores"]
    return AuditEntry(
        id=row["id"],
        occurred_at=occurred_at,
        action=row["acao"],
        actor=row["actor"],
        target=row["tabela_afetada"],
        target_id=row["id_afetado"],
        details=json.loads(raw_details) if raw_details else None,
        origin=row["endereco_ip"],
    )


def _where(criteria: AuditFilter) -> tuple[str, Params]:
    clauses = []
    params: list[Any] = []
    if criteria.action:
        clauses.append("a.acao = ?")
        params.append(criteria.action.value)
    # Timestamps are stored in UTC; filter dates refer to local calendar days.
    if criteria.start:
        clauses.append("a.data_hora >= ?")
        params.append(to_utc_text(datetime.combine(criteria.start, time.min)))
    if criteria.end:
        clauses.append("a.data_hora < ?")
        params.append(to_utc_text(datetime.combine(criteria.end + timedelta(days=1), time.min)))
    return (" WHERE " + " AND ".join(clauses) if clauses else ""), params


class SqliteAuditRepository:
    def __init__(self, db: Database, origin: str) -> None:
        """`origin` identifies the workstation that produced the entries."""
        self._db = db
        self._origin = origin

    def record(
        self,
        action: AuditAction,
        *,
        user_id: int | None = None,
        target: AuditTarget | None = None,
        target_id: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO auditoria "
                "(usuario_id, acao, tabela_afetada, id_afetado, dados_novos, endereco_ip) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    action.value,
                    (target or AuditTarget.SYSTEM).value,
                    target_id,
                    json.dumps(details, ensure_ascii=False) if details else None,
                    self._origin,
                ),
            )

    def search(self, criteria: AuditFilter, offset: int, limit: int) -> list[AuditEntry]:
        where, params = _where(criteria)
        rows = self._db.fetch_all(
            "SELECT a.*, u.username AS actor FROM auditoria a "
            f"LEFT JOIN usuarios u ON u.id = a.usuario_id{where} "
            "ORDER BY a.data_hora DESC, a.id DESC LIMIT ? OFFSET ?",
            (*params, limit, offset),
        )
        return [_to_entry(row) for row in rows]

    def count(self, criteria: AuditFilter) -> int:
        where, params = _where(criteria)
        return int(self._db.fetch_value(f"SELECT COUNT(*) FROM auditoria a{where}", params))
