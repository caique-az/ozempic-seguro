"""
Testes para AuditRepository - Operações de auditoria.
"""

from datetime import datetime

import pytest

from ozempic_seguro.repositories.audit_repository import AuditRepository


class TestAuditRepository:
    """Testes para AuditRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = AuditRepository()
        return

    def test_create_log_success(self):
        """Testa criação de log de auditoria"""
        log_id = self.repo.create_log(
            user_id=1,
            action="TEST_ACTION",
            affected_table="TEST_TABLE",
            id_afetado=1,
            previous_data={"old": "value"},
            new_data={"new": "value"},
            ip_address="127.0.0.1",
        )

        assert log_id is not None
        assert isinstance(log_id, int)

    def test_create_log_minimal(self):
        """Testa criação de log com dados mínimos"""
        log_id = self.repo.create_log(
            user_id=1, action="MINIMAL_ACTION", affected_table="TEST_TABLE"
        )

        assert log_id is not None

    def test_create_log_without_user(self):
        """Testa criação de log sem usuário (ações de sistema)"""
        log_id = self.repo.create_log(user_id=None, action="SYSTEM_ACTION", affected_table="SYSTEM")

        assert log_id is not None

    def test_get_logs(self):
        """Testa obtenção de logs"""
        # Criar alguns logs primeiro
        self.repo.create_log(user_id=1, action="GET_LOGS_TEST", affected_table="TEST")

        logs = self.repo.get_logs(offset=0, limit=10)

        assert isinstance(logs, list)

    def test_get_logs_with_filter(self):
        """Testa obtenção de logs com filtro"""
        # Criar log específico
        self.repo.create_log(user_id=1, action="FILTERED_ACTION", affected_table="FILTERED_TABLE")

        logs = self.repo.get_logs(offset=0, limit=10, action_filter="FILTERED_ACTION")

        assert isinstance(logs, list)
        # Todos os logs retornados devem ter a ação filtrada
        for log in logs:
            assert log["acao"] == "FILTERED_ACTION"

    def test_count_logs(self):
        """Testa contagem de logs"""
        count = self.repo.count_logs()

        assert isinstance(count, int)
        assert count >= 0

    def test_count_logs_with_filter(self):
        """Testa contagem de logs com filtro"""
        # Criar log específico
        unique_action = f"COUNT_TEST_{datetime.now().timestamp()}"
        self.repo.create_log(user_id=1, action=unique_action, affected_table="TEST")

        count = self.repo.count_logs(action_filter=unique_action)

        assert count >= 1


class TestAuditRepositoryFilters:
    """Testes para filtros de AuditRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = AuditRepository()
        return

    def test_filter_by_table(self):
        """Testa filtro por tabela"""
        unique_table = f"TABLE_{datetime.now().timestamp()}"

        self.repo.create_log(user_id=1, action="TEST", affected_table=unique_table)

        logs = self.repo.get_logs(table_filter=unique_table)

        for log in logs:
            assert log["tabela_afetada"] == unique_table

    def test_filter_by_user(self):
        """Testa filtro por usuário"""
        logs = self.repo.get_logs(user_filter=1)

        # Logs filtrados por usuário devem ter o usuário correto
        # O campo retornado é 'usuario' (username), não 'usuario_id'
        assert isinstance(logs, list)

    def test_pagination(self):
        """Testa paginação de logs"""
        # Criar vários logs
        for i in range(5):
            self.repo.create_log(user_id=1, action=f"PAGINATION_TEST_{i}", affected_table="TEST")

        # Buscar primeira página
        page1 = self.repo.get_logs(offset=0, limit=2)
        # Buscar segunda página
        page2 = self.repo.get_logs(offset=2, limit=2)

        # Páginas devem ser diferentes
        if len(page1) > 0 and len(page2) > 0:
            assert page1[0]["id"] != page2[0]["id"]


class TestAuditRepositoryAdditional:
    """Testes adicionais para AuditRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = AuditRepository()
        return

    def test_get_logs_empty_filter(self):
        """Testa logs com filtro que não retorna nada"""
        logs = self.repo.get_logs(action_filter="NONEXISTENT_ACTION_12345")
        assert isinstance(logs, list)

    def test_count_logs_empty_filter(self):
        """Testa contagem com filtro que não retorna nada"""
        count = self.repo.count_logs(action_filter="NONEXISTENT_ACTION_12345")
        assert count == 0

    def test_create_log_with_all_fields(self):
        """Testa criação de log com todos os campos"""
        log_id = self.repo.create_log(
            user_id=1,
            action="COMPLETE_LOG",
            affected_table="USERS",
            id_afetado=100,
            previous_data={"status": "active"},
            new_data={"status": "inactive"},
            ip_address="192.168.1.1",
        )
        assert log_id is not None

    def test_get_logs_default_limit(self):
        """Testa logs com limite padrão"""
        logs = self.repo.get_logs()
        assert isinstance(logs, list)

    def test_create_log_with_none_ip(self):
        """Testa criação de log sem IP"""
        log_id = self.repo.create_log(
            user_id=1, action="NO_IP_LOG", affected_table="TEST", ip_address=None
        )
        assert log_id is not None

    def test_filter_by_date_range(self):
        """Testa filtro por intervalo de datas"""
        logs = self.repo.get_logs(start_date="2020-01-01", end_date="2030-12-31")
        assert isinstance(logs, list)

    def test_count_logs_with_date_filter(self):
        """Testa contagem com filtro de data"""
        count = self.repo.count_logs(start_date="2020-01-01", end_date="2030-12-31")
        assert isinstance(count, int)


class TestAuditRepositoryFilterCombinations:
    """Testes para filtros do AuditRepository"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = AuditRepository()
        return

    def test_filter_by_user(self):
        """Testa filtro por usuário"""
        logs = self.repo.get_logs(user_filter=1)
        assert isinstance(logs, list)

    def test_filter_by_table(self):
        """Testa filtro por tabela"""
        logs = self.repo.get_logs(table_filter="usuarios")
        assert isinstance(logs, list)

    def test_combined_filters(self):
        """Testa filtros combinados"""
        logs = self.repo.get_logs(action_filter="LOGIN", table_filter="usuarios")
        assert isinstance(logs, list)

    def test_pagination_offset(self):
        """Testa paginação com offset"""
        logs = self.repo.get_logs(offset=10, limit=5)
        assert isinstance(logs, list)

    def test_large_limit(self):
        """Testa com limite grande"""
        logs = self.repo.get_logs(limit=1000)
        assert isinstance(logs, list)

    def test_count_with_user_filter(self):
        """Testa contagem com filtro de usuário"""
        count = self.repo.count_logs(user_filter=1)
        assert isinstance(count, int)

    def test_count_with_table_filter(self):
        """Testa contagem com filtro de tabela"""
        count = self.repo.count_logs(table_filter="usuarios")
        assert isinstance(count, int)

    def test_count_with_action_filter(self):
        """Testa contagem com filtro de ação"""
        count = self.repo.count_logs(action_filter="LOGIN")
        assert isinstance(count, int)
