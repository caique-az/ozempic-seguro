"""Querying the audit trail."""

from datetime import date, timedelta

from ..domain.audit import AuditEntry, AuditFilter
from ..domain.permissions import Permission, require
from ..domain.ports import AuditLog
from .pagination import Page, offset_for
from .state import Session


class AuditService:
    def __init__(self, audit: AuditLog, session: Session) -> None:
        self._audit = audit
        self._session = session

    def search(self, criteria: AuditFilter, page: int = 1, per_page: int = 50) -> Page[AuditEntry]:
        require(self._session.require_user(), Permission.VIEW_AUDIT)
        items = self._audit.search(criteria, offset_for(page, per_page), per_page)
        return Page(items, self._audit.count(criteria), page, per_page)

    @staticmethod
    def last_days(today: date, days: int = 7) -> AuditFilter:
        return AuditFilter(start=today - timedelta(days=days), end=today)
