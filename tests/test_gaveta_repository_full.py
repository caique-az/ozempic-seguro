"""
Testes completos para GavetaRepository.
"""

import pytest

from ozempic_seguro.repositories.gaveta_repository import GavetaRepository


class TestGavetaRepositoryGetState:
    """Testes para get_state"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = GavetaRepository()
        yield

    def test_get_state_returns_bool(self):
        """Testa que get_state retorna bool"""
        result = self.repo.get_state(1)
        assert isinstance(result, bool)

    def test_get_state_different_drawers(self):
        """Testa get_state para diferentes gavetas"""
        for i in range(1, 6):
            result = self.repo.get_state(i)
            assert isinstance(result, bool)


class TestGavetaRepositorySetState:
    """Testes para set_state"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = GavetaRepository()
        yield

    def test_set_state_open(self):
        """Testa abertura de gaveta"""
        result = self.repo.set_state(1, "aberta", "repositor")
        assert result is not None

    def test_set_state_closed(self):
        """Testa fechamento de gaveta"""
        result = self.repo.set_state(1, "fechada", "repositor")
        assert result is not None

    def test_set_state_with_user_id(self):
        """Testa set_state com user_id"""
        result = self.repo.set_state(1, "fechada", "repositor", 1)
        assert result is not None


class TestGavetaRepositoryHistory:
    """Testes para histórico"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.repo = GavetaRepository()
        yield

    def test_get_history(self):
        """Testa obtenção de histórico"""
        result = self.repo.get_history(1)
        assert isinstance(result, list)

    def test_get_history_with_limit(self):
        """Testa histórico com limite"""
        result = self.repo.get_history(1, limit=5)
        assert isinstance(result, list)
        assert len(result) <= 5
