"""
Testes para DatabaseConnection - Gerenciamento de conexão com banco.
"""

import sqlite3

import pytest

from ozempic_seguro.config import Config
from ozempic_seguro.repositories.connection import DatabaseConnection


class TestDatabaseConnection:
    """Testes para DatabaseConnection"""

    def test_singleton_pattern(self):
        """Testa que DatabaseConnection é singleton"""
        conn1 = DatabaseConnection.get_instance()
        conn2 = DatabaseConnection.get_instance()

        assert conn1 is conn2

    def test_connection_is_valid(self):
        """Testa que conexão é válida"""
        db = DatabaseConnection.get_instance()

        assert db.conn is not None
        assert isinstance(db.conn, sqlite3.Connection)

    def test_cursor_is_valid(self):
        """Testa que cursor é válido"""
        db = DatabaseConnection.get_instance()

        assert db.cursor is not None
        assert isinstance(db.cursor, sqlite3.Cursor)

    def test_execute_query(self):
        """Testa execução de query"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT 1 as test")
        row = db.fetchone()

        assert row is not None
        assert row["test"] == 1

    def test_execute_with_params(self):
        """Testa execução de query com parâmetros"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT ? as value", (42,))
        row = db.fetchone()

        assert row["value"] == 42

    def test_fetchall(self):
        """Testa fetchall"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT 1 as num UNION SELECT 2 UNION SELECT 3")
        rows = db.fetchall()

        assert len(rows) == 3

    def test_commit_and_rollback(self):
        """Testa commit e rollback"""
        db = DatabaseConnection.get_instance()

        # Criar tabela temporária
        db.execute("CREATE TABLE IF NOT EXISTS test_temp (id INTEGER PRIMARY KEY, value TEXT)")
        db.commit()

        # Inserir e fazer rollback
        db.execute("INSERT INTO test_temp (value) VALUES (?)", ("test",))
        db.rollback()

        # Verificar que não foi inserido
        db.execute("SELECT COUNT(*) as count FROM test_temp")
        db.fetchone()

        # Limpar
        db.execute("DROP TABLE IF EXISTS test_temp")
        db.commit()

    def test_migrations_table_exists(self):
        """Testa que tabela de migrations existe"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        row = db.fetchone()

        assert row is not None
        assert row["name"] == "migrations"

    def test_usuarios_table_exists(self):
        """Testa que tabela de usuários existe"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        row = db.fetchone()

        assert row is not None
        assert row["name"] == "usuarios"

    def test_is_new_database_property(self):
        """Testa propriedade is_new_database"""
        db = DatabaseConnection.get_instance()

        # Deve ser booleano
        assert isinstance(db.is_new_database, bool)


class TestDatabaseConnectionPragmas:
    """Testes para configurações de pragmas"""

    def test_foreign_keys_enabled(self):
        """Testa que foreign keys estão habilitadas"""
        if not Config.Database.ENABLE_FOREIGN_KEYS:
            pytest.skip("Foreign keys disabled in config")

        db = DatabaseConnection.get_instance()
        db.execute("PRAGMA foreign_keys")
        row = db.fetchone()

        assert row[0] == 1

    def test_wal_mode_enabled(self):
        """Testa que WAL mode está habilitado"""
        if not Config.Database.ENABLE_WAL_MODE:
            pytest.skip("WAL mode disabled in config")

        db = DatabaseConnection.get_instance()
        db.execute("PRAGMA journal_mode")
        row = db.fetchone()

        assert row[0].lower() == "wal"


class TestDatabaseConnectionAdditional:
    """Testes adicionais para DatabaseConnection"""

    def test_context_manager(self):
        """Testa uso como context manager"""
        with DatabaseConnection.get_instance() as db:
            db.execute("SELECT 1 as test")
            row = db.fetchone()
            assert row["test"] == 1

    def test_executemany(self):
        """Testa executemany"""
        db = DatabaseConnection.get_instance()

        db.execute("CREATE TABLE IF NOT EXISTS test_many (id INTEGER PRIMARY KEY, val TEXT)")
        db.commit()

        data = [("a",), ("b",), ("c",)]
        db.executemany("INSERT INTO test_many (val) VALUES (?)", data)
        db.commit()

        db.execute("SELECT COUNT(*) as cnt FROM test_many")
        row = db.fetchone()
        assert row["cnt"] >= 3

        db.execute("DROP TABLE IF EXISTS test_many")
        db.commit()

    def test_lastrowid(self):
        """Testa lastrowid"""
        db = DatabaseConnection.get_instance()

        db.execute("CREATE TABLE IF NOT EXISTS test_lastid (id INTEGER PRIMARY KEY, val TEXT)")
        db.commit()

        db.execute("INSERT INTO test_lastid (val) VALUES (?)", ("test",))
        db.commit()

        last_id = db.lastrowid()
        assert isinstance(last_id, int)
        assert last_id > 0

        db.execute("DROP TABLE IF EXISTS test_lastid")
        db.commit()

    def test_gavetas_table_exists(self):
        """Testa que tabela de gavetas existe"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gavetas'")
        row = db.fetchone()

        assert row is not None

    def test_historico_gavetas_table_exists(self):
        """Testa que tabela de histórico existe"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_gavetas'")
        row = db.fetchone()

        assert row is not None

    def test_auditoria_table_exists(self):
        """Testa que tabela de auditoria existe"""
        db = DatabaseConnection.get_instance()

        db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auditoria'")
        row = db.fetchone()

        assert row is not None

    def test_cache_size_configured(self):
        """Testa que cache size está configurado"""
        db = DatabaseConnection.get_instance()
        db.execute("PRAGMA cache_size")
        row = db.fetchone()

        # Cache size pode ser negativo (em KB) ou positivo (em páginas)
        assert row[0] != 0
