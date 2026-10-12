"""
Testes para DatabaseManager - Wrapper de banco de dados.
"""

import warnings

import pytest

from ozempic_seguro.repositories.database import DatabaseManager


class TestDatabaseManager:
    """Testes para DatabaseManager"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.db = DatabaseManager()
        return

    def test_get_connection(self):
        """Testa obtenção de conexão"""
        conn = self.db.conn

        assert conn is not None

    def test_get_cursor(self):
        """Testa obtenção de cursor"""
        cursor = self.db.cursor

        assert cursor is not None

    def test_get_usuarios_deprecated(self):
        """Testa método deprecated get_usuarios"""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            users = self.db.get_usuarios()

            assert isinstance(users, list)

    def test_get_estado_gaveta(self):
        """Testa método deprecated get_estado_gaveta"""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            state = self.db.get_estado_gaveta(1)

            assert isinstance(state, bool)

    def test_close(self):
        """Testa close"""
        # Não deve lançar exceção
        # Não chamamos close pois é singleton
        assert hasattr(self.db, "close")
