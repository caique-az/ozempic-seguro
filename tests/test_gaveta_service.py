"""
Testes para GavetaService - Cobertura de operações de gavetas.
"""

import pytest
from unittest.mock import patch, MagicMock

from ozempic_seguro.services.gaveta_service import GavetaService


class TestGavetaService:
    """Testes para GavetaService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        # Reset singleton para testes isolados
        GavetaService._instance = None
        self.service = GavetaService.get_instance()
        yield
        GavetaService._instance = None

    def test_singleton_pattern(self):
        """Testa que GavetaService é singleton"""
        service1 = GavetaService.get_instance()
        service2 = GavetaService.get_instance()
        assert service1 is service2

    def test_get_estado_gaveta(self):
        """Testa obtenção do estado de uma gaveta"""
        estado = self.service.get_estado(1)
        # Estado pode ser True ou False
        assert isinstance(estado, bool)

    def test_get_historico(self):
        """Testa obtenção de histórico de gaveta"""
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

    def test_set_estado(self):
        """Testa definição de estado de gaveta"""
        result = self.service.set_estado(1, True, "administrador")
        assert isinstance(result, tuple)

    def test_fechar_gaveta(self):
        """Testa fechamento de gaveta"""
        result, msg = self.service.fechar_gaveta(1, "repositor", 1)
        assert isinstance(result, bool)
        assert isinstance(msg, str)

    def test_abrir_gaveta_administrador(self):
        """Testa abertura de gaveta por administrador"""
        result, msg = self.service.abrir_gaveta(1, "administrador", 1)
        assert isinstance(result, bool)
        assert isinstance(msg, str)

    def test_abrir_gaveta_vendedor(self):
        """Testa abertura de gaveta por vendedor"""
        result, msg = self.service.abrir_gaveta(2, "vendedor", 1)
        assert isinstance(result, bool)
        assert isinstance(msg, str)

    def test_abrir_gaveta_repositor(self):
        """Testa abertura de gaveta por repositor"""
        result, msg = self.service.abrir_gaveta(3, "repositor", 1)
        assert isinstance(result, bool)
        assert isinstance(msg, str)

    def test_gaveta_state_manager_alias(self):
        """Testa que GavetaStateManager é alias para GavetaService"""
        from ozempic_seguro.services.gaveta_service import GavetaStateManager

        assert GavetaStateManager is GavetaService


class TestGavetaServiceWithMocks:
    """Testes com mocks para GavetaService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup com mocks"""
        GavetaService._instance = None
        yield
        GavetaService._instance = None

    def test_abrir_gaveta_sistema_bloqueado(self):
        """Testa abertura quando sistema está bloqueado"""
        with patch.object(GavetaService, "_initialize"):
            service = GavetaService()
            service._repository = MagicMock()
            service._session_manager = MagicMock()
            service._session_manager.is_blocked.return_value = True
            service._session_manager.get_remaining_time.return_value = 300

            result, msg = service.abrir_gaveta(1, "vendedor", 1)

            assert result is False
            assert "bloqueado" in msg.lower()

    def test_abrir_gaveta_sucesso_vendedor(self):
        """Testa abertura com sucesso por vendedor"""
        with patch.object(GavetaService, "_initialize"):
            service = GavetaService()
            service._repository = MagicMock()
            service._session_manager = MagicMock()
            service._session_manager.is_blocked.return_value = False
            service._session_manager.get_user_id.return_value = 1
            service._repository.set_state.return_value = (True, "OK")

            result, msg = service.abrir_gaveta(1, "vendedor", None)

            assert result is True
            service._session_manager.block_for_minutes.assert_called_once_with(5)

    def test_abrir_gaveta_erro(self):
        """Testa abertura com erro"""
        with patch.object(GavetaService, "_initialize"):
            service = GavetaService()
            service._repository = MagicMock()
            service._session_manager = MagicMock()
            service._session_manager.is_blocked.return_value = False
            service._repository.set_state.side_effect = Exception("DB Error")

            result, msg = service.abrir_gaveta(1, "administrador", 1)

            assert result is False
            assert "erro" in msg.lower()

    def test_get_todo_historico_com_erro(self):
        """Testa get_todo_historico com erro"""
        with patch.object(GavetaService, "_initialize"):
            service = GavetaService()
            service._repository = MagicMock()
            service._repository.get_all_history.side_effect = Exception("DB Error")

            result = service.get_todo_historico()

            assert result == []
