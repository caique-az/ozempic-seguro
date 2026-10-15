"""Audit trail entries and the actions that produce them."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Any


class AuditAction(StrEnum):
    """Values are the identifiers persisted in the audit table."""

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGIN_BLOCKED = "LOGIN_BLOCKED"
    LOGOUT = "LOGOUT"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    USER_CREATED = "CRIAR"
    USER_DELETED = "EXCLUIR"
    PASSWORD_CHANGED = "ATUALIZAR_SENHA"
    DRAWER_OPENED = "ABRIR_GAVETA"
    DRAWER_CLOSED = "FECHAR_GAVETA"
    TIMER_ENABLED = "TIMER_ATIVADO"
    TIMER_DISABLED = "TIMER_DESATIVADO"
    SYSTEM_LOCK_CLEARED = "BLOQUEIO_REMOVIDO"

    @property
    def label(self) -> str:
        return _ACTION_LABELS[self]


_ACTION_LABELS = {
    AuditAction.LOGIN_SUCCESS: "Login",
    AuditAction.LOGIN_FAILED: "Login com falha",
    AuditAction.LOGIN_BLOCKED: "Login bloqueado",
    AuditAction.LOGOUT: "Logout",
    AuditAction.SESSION_EXPIRED: "Sessão expirada",
    AuditAction.USER_CREATED: "Usuário criado",
    AuditAction.USER_DELETED: "Usuário excluído",
    AuditAction.PASSWORD_CHANGED: "Senha alterada",
    AuditAction.DRAWER_OPENED: "Gaveta aberta",
    AuditAction.DRAWER_CLOSED: "Gaveta fechada",
    AuditAction.TIMER_ENABLED: "Timer ativado",
    AuditAction.TIMER_DISABLED: "Timer desativado",
    AuditAction.SYSTEM_LOCK_CLEARED: "Bloqueio removido",
}


class AuditTarget(StrEnum):
    """Kind of record an audit entry refers to (persisted as the affected table)."""

    USER = "USUARIOS"
    DRAWER = "GAVETAS"
    SESSION = "SESSOES"
    SYSTEM = "SISTEMA"


@dataclass(frozen=True, slots=True)
class AuditEntry:
    id: int
    occurred_at: datetime
    action: str
    actor: str | None
    target: str | None
    target_id: int | None
    details: dict[str, Any] | None
    origin: str | None

    @property
    def action_label(self) -> str:
        try:
            return AuditAction(self.action).label
        except ValueError:
            # Entries written by older versions may use actions that no longer exist.
            return self.action


@dataclass(frozen=True, slots=True)
class AuditFilter:
    action: AuditAction | None = None
    start: date | None = None
    end: date | None = None
