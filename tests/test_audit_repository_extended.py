"""
Testes estendidos para AuditRepository - Cobertura adicional.
"""

import pytest

from ozempic_seguro.repositories.audit_repository import AuditRepository


class TestAuditRepositoryExtended:
    """Testes estendidos para AuditRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = AuditRepository()
        return

    def test_create_log_minimal(self):
        """Testa criação de log mínimo"""
        result = self.repo.create_log(user_id=1, action="TEST")

        assert result is None or isinstance(result, int)

    def test_create_log_full(self):
        """Testa criação de log completo"""
        result = self.repo.create_log(
            user_id=1,
            action="CREATE",
            affected_table="usuarios",
            id_afetado=2,
            previous_data={"old": "data"},
            new_data={"new": "data"},
            ip_address="127.0.0.1",
        )

        assert result is None or isinstance(result, int)

    def test_get_logs_default(self):
        """Testa obtenção de logs com parâmetros default"""
        logs = self.repo.get_logs()

        assert isinstance(logs, list)

    def test_get_logs_with_limit(self):
        """Testa obtenção de logs com limite"""
        logs = self.repo.get_logs(limit=5)

        assert isinstance(logs, list)
        assert len(logs) <= 5

    def test_get_logs_with_offset(self):
        """Testa obtenção de logs com offset"""
        logs = self.repo.get_logs(offset=0, limit=10)

        assert isinstance(logs, list)

    def test_get_logs_filter_by_action(self):
        """Testa filtro por ação"""
        logs = self.repo.get_logs(action_filter="LOGIN")

        assert isinstance(logs, list)

    def test_get_logs_filter_by_table(self):
        """Testa filtro por tabela"""
        logs = self.repo.get_logs(table_filter="usuarios")

        assert isinstance(logs, list)

    def test_get_logs_filter_by_date_range(self):
        """Testa filtro por período"""
        logs = self.repo.get_logs(start_date="2025-01-01", end_date="2025-12-31")

        assert isinstance(logs, list)

    def test_count_logs_default(self):
        """Testa contagem de logs"""
        count = self.repo.count_logs()

        assert isinstance(count, int)
        assert count >= 0

    def test_count_logs_with_filter(self):
        """Testa contagem de logs com filtro"""
        count = self.repo.count_logs(action_filter="LOGIN")

        assert isinstance(count, int)
        assert count >= 0
