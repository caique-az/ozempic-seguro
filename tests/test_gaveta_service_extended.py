"""
Testes estendidos para GavetaService - Cobertura adicional.
"""

import pytest

from ozempic_seguro.services.gaveta_service import GavetaService
from ozempic_seguro.session.session_manager import SessionManager


class TestGavetaServiceOperations:
    """Testes de operações de gavetas"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        GavetaService._instance = None
        self.service = GavetaService.get_instance()

        # Configurar sessão com admin
        self.session = SessionManager.get_instance()
        self.session.cleanup()
        self.session.set_current_user({"id": 1, "username": "admin", "tipo": "administrador"})
        yield
        self.session.cleanup()
        GavetaService._instance = None

    def test_abrir_gaveta_admin(self):
        """Testa abertura de gaveta por admin"""
        sucesso, mensagem = self.service.abrir_gaveta(1, "administrador")

        assert isinstance(sucesso, bool)
        assert isinstance(mensagem, str)

    def test_abrir_gaveta_vendedor(self):
        """Testa abertura de gaveta por vendedor"""
        self.session.set_current_user({"id": 2, "username": "vendedor", "tipo": "vendedor"})

        sucesso, mensagem = self.service.abrir_gaveta(2, "vendedor")

        assert isinstance(sucesso, bool)
        assert isinstance(mensagem, str)

    def test_abrir_gaveta_repositor(self):
        """Testa abertura de gaveta por repositor"""
        self.session.set_current_user({"id": 3, "username": "repositor", "tipo": "repositor"})

        sucesso, mensagem = self.service.abrir_gaveta(3, "repositor")

        assert isinstance(sucesso, bool)
        assert isinstance(mensagem, str)

    def test_fechar_gaveta(self):
        """Testa fechamento de gaveta"""
        # Primeiro abre
        self.service.open_drawer(4, "administrador")

        # Depois fecha
        resultado = self.service.close_drawer(4, "administrador", user_id=1)

        assert isinstance(resultado, tuple)

    def test_get_estado(self):
        """Testa obtenção de estado"""
        estado = self.service.get_estado(1)

        assert isinstance(estado, bool)

    def test_session_is_blocked_when_not_blocked(self):
        """Testa verificação de bloqueio quando não bloqueado"""
        self.session.clear_block()

        # Verificar via session manager
        blocked = self.session.is_blocked()

        assert blocked is False

    def test_session_is_blocked_when_blocked(self):
        """Testa verificação de bloqueio quando bloqueado"""
        self.session.block_for_minutes(1)

        # Verificar via session manager
        blocked = self.session.is_blocked()

        assert blocked is True

        # Limpar
        self.session.clear_block()

    def test_session_get_remaining_time(self):
        """Testa obtenção de tempo restante"""
        self.session.block_for_minutes(1)

        remaining = self.session.get_remaining_time()

        assert isinstance(remaining, int)
        assert remaining >= 0

        # Limpar
        self.session.clear_block()


class TestGavetaServiceHistory:
    """Testes de histórico de gavetas"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        GavetaService._instance = None
        self.service = GavetaService.get_instance()
        yield
        GavetaService._instance = None

    def test_get_historico(self):
        """Testa obtenção de histórico"""
        historico = self.service.get_history(1, limit=10)

        assert isinstance(historico, list)

    def test_get_historico_paginado(self):
        """Testa obtenção de histórico paginado"""
        historico = self.service.get_historico_paginado(1, offset=0, limit=20)

        assert isinstance(historico, list)

    def test_get_total_historico(self):
        """Testa contagem de histórico"""
        total = self.service.get_total_historico(1)

        assert isinstance(total, int)
        assert total >= 0

    def test_get_todo_historico(self):
        """Testa obtenção de todo histórico"""
        historico = self.service.get_todo_historico()

        assert isinstance(historico, list)

    def test_get_todo_historico_paginado(self):
        """Testa obtenção de todo histórico paginado"""
        historico = self.service.get_todo_historico_paginado(offset=0, limit=20)

        assert isinstance(historico, list)

    def test_get_total_todo_historico(self):
        """Testa contagem de todo histórico"""
        total = self.service.get_total_todo_historico()

        assert isinstance(total, int)
        assert total >= 0
