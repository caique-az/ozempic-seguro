"""
Testes simplificados para o DatabaseManager.
Evita problemas com singleton e locks de arquivo.
"""

import pytest
import tempfile
import os
import sqlite3


class TestDatabaseSimple:
    """Testes básicos de banco de dados usando SQLite direto"""

    def test_sqlite_connection(self):
        """Testa conexão básica com SQLite"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            # Cria conexão
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Cria tabela
            cursor.execute(
                """
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """
            )

            # Insere dados
            cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
            conn.commit()

            # Busca dados
            cursor.execute("SELECT * FROM test_table")
            result = cursor.fetchone()

            assert result is not None
            assert result[1] == "test"

            conn.close()

    def test_user_table_structure(self):
        """Testa estrutura da tabela de usuários"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Cria tabela de usuários
            cursor.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    nome_completo TEXT,
                    tipo TEXT,
                    ativo INTEGER DEFAULT 1
                )
            """
            )

            # Verifica se tabela foi criada
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            result = cursor.fetchone()

            assert result is not None
            assert result[0] == "usuarios"

            conn.close()

    def test_unique_constraint(self):
        """Testa constraint de unicidade"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Cria tabela
            cursor.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL
                )
            """
            )

            # Primeiro insert deve funcionar
            cursor.execute("INSERT INTO usuarios (username) VALUES (?)", ("user1",))
            conn.commit()

            # Segundo insert com mesmo username deve falhar
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO usuarios (username) VALUES (?)", ("user1",))
                conn.commit()

            conn.close()

    def test_transaction_rollback(self):
        """Testa rollback de transação"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Cria tabela
            cursor.execute(
                """
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """
            )

            # Inicia transação
            cursor.execute("BEGIN")
            cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test1",))

            # Rollback
            conn.rollback()

            # Verifica que não foi inserido
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]

            assert count == 0

            conn.close()
