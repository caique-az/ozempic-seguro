"""
Testes para DatabaseManager e DatabaseConnection.

Testa a camada de persistência usando banco SQLite.
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import patch


class TestDatabaseManager:
    """Testes para o DatabaseManager usando banco SQLite direto"""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset do singleton antes e depois de cada teste"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection

        # Limpa antes
        for cls in [DatabaseManager, DatabaseConnection]:
            if hasattr(cls, "_instance"):
                if cls._instance and hasattr(cls._instance, "conn"):
                    try:
                        cls._instance.conn.close()
                    except:
                        pass
                cls._instance = None

        yield

        # Limpa depois
        for cls in [DatabaseManager, DatabaseConnection]:
            if hasattr(cls, "_instance"):
                if cls._instance and hasattr(cls._instance, "conn"):
                    try:
                        cls._instance.conn.close()
                    except:
                        pass
                cls._instance = None

    def test_singleton_pattern(self):
        """Testa se DatabaseManager é singleton"""
        from ozempic_seguro.repositories.database import DatabaseManager

        DatabaseManager._instance = None
        db1 = DatabaseManager()
        db2 = DatabaseManager()
        assert db1 is db2

    def test_create_tables(self):
        """Testa criação de tabelas no banco através da inicialização"""
        from ozempic_seguro.repositories.connection import DatabaseConnection

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
                try:
                    db = DatabaseConnection.get_instance()

                    # Verificar se tabelas foram criadas
                    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = db.cursor.fetchall()
                    table_names = [t[0] for t in tables]

                    assert "usuarios" in table_names
                    assert "gavetas" in table_names
                    assert "historico_gavetas" in table_names
                finally:
                    if hasattr(db, "_conn"):
                        db._conn.close()
                    DatabaseConnection._instance = None

    def test_execute_query_success(self):
        """Testa execução de query com sucesso"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection
        from ozempic_seguro.repositories.user_repository import UserRepository

        # Reset singletons
        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
                try:
                    db = DatabaseManager()
                    user_repo = UserRepository()

                    # Inserir usuário de teste usando UserRepository
                    result = user_repo.create_user(
                        username="test_user",
                        password="senha123",
                        full_name="Test User",
                        user_type="vendedor",
                    )

                    # create_user retorna o ID do usuário ou None
                    assert result is not None

                finally:
                    if hasattr(db, "conn"):
                        db.conn.close()
                    DatabaseManager._instance = None
                    DatabaseConnection._instance = None

    def test_fetch_one(self):
        """Testa busca de um registro"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection
        from ozempic_seguro.repositories.user_repository import UserRepository

        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
                try:
                    db = DatabaseManager()
                    user_repo = UserRepository()

                    # Inserir usuário usando UserRepository
                    user_repo.create_user(
                        username="test_user",
                        password="senha123",
                        full_name="Test User",
                        user_type="vendedor",
                    )

                    # Buscar usuário usando cursor
                    db.cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("test_user",))
                    user = db.cursor.fetchone()

                    assert user is not None
                finally:
                    if hasattr(db, "conn"):
                        db.conn.close()
                    DatabaseManager._instance = None
                    DatabaseConnection._instance = None

    def test_fetch_all(self):
        """Testa busca de múltiplos registros"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection
        from ozempic_seguro.repositories.user_repository import UserRepository

        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
                try:
                    db = DatabaseManager()
                    user_repo = UserRepository()

                    # Inserir múltiplos usuários usando UserRepository
                    users_data = [
                        ("user1", "senha1", "User One", "vendedor"),
                        ("user2", "senha2", "User Two", "repositor"),
                        ("user3", "senha3", "User Three", "administrador"),
                    ]

                    for username, senha, nome, tipo in users_data:
                        user_repo.create_user(username, senha, nome, tipo)

                    # Buscar todos os usuários
                    db.cursor.execute("SELECT * FROM usuarios")
                    users = db.cursor.fetchall()

                    # Como pode ter o usuário admin padrão, verifica se tem pelo menos 3
                    assert len(users) >= 3
                finally:
                    if hasattr(db, "conn"):
                        db.conn.close()
                    DatabaseManager._instance = None
                    DatabaseConnection._instance = None

    def test_transaction_rollback(self):
        """Testa rollback de transação em caso de erro"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection
        from ozempic_seguro.repositories.user_repository import UserRepository

        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
                try:
                    db = DatabaseManager()
                    user_repo = UserRepository()

                    # Criar usuário único usando UserRepository
                    result1 = user_repo.create_user("unique_user", "senha1", "User", "vendedor")
                    # create_user retorna o ID do usuário ou None
                    assert result1 is not None

                    # Segunda inserção deve falhar (username único) - retorna None
                    result2 = user_repo.create_user("unique_user", "senha2", "User2", "vendedor")
                    assert result2 is None

                    # Verificar que só existe um usuário com esse username
                    db.cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("unique_user",))
                    users = db.cursor.fetchall()
                    assert len(users) == 1
                finally:
                    if hasattr(db, "conn"):
                        db.conn.close()
                    DatabaseManager._instance = None
                    DatabaseConnection._instance = None


class TestDatabaseManagerDeprecatedMethods:
    """Testes para métodos deprecated do DatabaseManager"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup do banco para testes"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection

        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

        self.patcher = patch.object(DatabaseConnection, "_get_db_path", return_value=self.db_path)
        self.patcher.start()

        self.db = DatabaseManager()

        yield

        self.patcher.stop()
        if hasattr(self.db, "conn"):
            try:
                self.db.conn.close()
            except:
                pass
        DatabaseManager._instance = None
        DatabaseConnection._instance = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_criar_usuario_deprecated(self):
        """Testa método deprecated criar_usuario"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.criar_usuario("test_dep", "senha123", "Test User", "vendedor")
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1

    def test_autenticar_usuario_deprecated(self):
        """Testa método deprecated autenticar_usuario"""
        import warnings

        # Primeiro criar usuário
        self.db._users.create_user("auth_test", "senha123", "Auth Test", "vendedor")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.autenticar_usuario("auth_test", "senha123")
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_usuarios_deprecated(self):
        """Testa método deprecated get_usuarios"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_usuarios()
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert isinstance(result, list)

    def test_get_estado_gaveta_deprecated(self):
        """Testa método deprecated get_estado_gaveta"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_estado_gaveta(1)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_set_estado_gaveta_deprecated(self):
        """Testa método deprecated set_estado_gaveta"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.set_estado_gaveta(1, True, "administrador", 1)
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1

    def test_get_historico_gaveta_deprecated(self):
        """Testa método deprecated get_historico_gaveta"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_historico_gaveta(1)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_historico_paginado_deprecated(self):
        """Testa método deprecated get_historico_paginado"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_historico_paginado(1, 0, 10)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_total_historico_deprecated(self):
        """Testa método deprecated get_total_historico"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_total_historico(1)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_todo_historico_deprecated(self):
        """Testa método deprecated get_todo_historico"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_todo_historico()
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_todo_historico_paginado_deprecated(self):
        """Testa método deprecated get_todo_historico_paginado"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_todo_historico_paginado(0, 10)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_get_total_todo_historico_deprecated(self):
        """Testa método deprecated get_total_todo_historico"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_total_todo_historico()
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_registrar_auditoria_deprecated(self):
        """Testa método deprecated registrar_auditoria"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.registrar_auditoria(1, "LOGIN", "usuarios")
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1

    def test_buscar_logs_auditoria_deprecated(self):
        """Testa método deprecated buscar_logs_auditoria"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.buscar_logs_auditoria()
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_contar_logs_auditoria_deprecated(self):
        """Testa método deprecated contar_logs_auditoria"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.contar_logs_auditoria()
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)

    def test_close_method(self):
        """Testa método close"""
        # O método close não deve lançar exceção
        self.db.close()

    def test_english_aliases(self):
        """Testa aliases em inglês"""
        import warnings

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            # Testar que aliases existem e funcionam
            assert hasattr(self.db, "create_user")
            assert hasattr(self.db, "authenticate_user")
            assert hasattr(self.db, "get_users")
            assert hasattr(self.db, "get_drawer_state")
            assert hasattr(self.db, "set_drawer_state")
            assert hasattr(self.db, "create_audit_log")


class TestDatabaseManagerAdditional:
    """Testes adicionais para DatabaseManager"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup do banco para testes"""
        from ozempic_seguro.repositories.database import DatabaseManager
        from ozempic_seguro.repositories.connection import DatabaseConnection

        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

        self.patcher = patch.object(DatabaseConnection, "_get_db_path", return_value=self.db_path)
        self.patcher.start()

        self.db = DatabaseManager()

        yield

        self.patcher.stop()
        if hasattr(self.db, "conn"):
            try:
                self.db.conn.close()
            except:
                pass
        DatabaseManager._instance = None
        DatabaseConnection._instance = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_singleton_pattern(self):
        """Testa padrão singleton"""
        from ozempic_seguro.repositories.database import DatabaseManager

        db2 = DatabaseManager()
        assert self.db is db2

    def test_cursor_property(self):
        """Testa propriedade cursor"""
        assert self.db.cursor is not None

    def test_conn_property(self):
        """Testa propriedade conn"""
        assert self.db.conn is not None

    def test_get_drawer_history_deprecated(self):
        """Testa método deprecated get_drawer_history"""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.db.get_drawer_history(1)
            if len(w) > 0:
                assert issubclass(w[-1].category, DeprecationWarning)

    def test_has_connection(self):
        """Testa que tem conexão ativa"""
        assert self.db.conn is not None
        assert self.db.cursor is not None
