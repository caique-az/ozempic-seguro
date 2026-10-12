"""
Testes simplificados para Services.
"""

import contextlib


class TestSimpleServices:
    """Testes básicos para serviços"""

    def test_database_manager_import(self):
        """Testa importação do DatabaseManager"""
        from ozempic_seguro.repositories.database import DatabaseManager

        assert DatabaseManager is not None

    def test_user_service_import(self):
        """Testa importação do UserService"""
        from ozempic_seguro.services.user_service import UserService

        assert UserService is not None

    def test_audit_service_import(self):
        """Testa importação do AuditService"""
        from ozempic_seguro.services.audit_service import AuditService

        assert AuditService is not None

    def test_session_manager_import(self):
        """Testa importação do SessionManager"""
        from ozempic_seguro.session.session_manager import SessionManager

        assert SessionManager is not None

    def test_database_manager_singleton(self):
        """Testa padrão singleton do DatabaseManager"""
        from ozempic_seguro.repositories.connection import DatabaseConnection
        from ozempic_seguro.repositories.database import DatabaseManager

        # Reset singletons
        DatabaseManager._instance = None
        DatabaseConnection._instance = None

        db1 = DatabaseManager()
        db2 = DatabaseManager()

        assert db1 is db2

        # Cleanup
        if hasattr(db1, "conn"):
            with contextlib.suppress(Exception):
                db1.conn.close()
        DatabaseManager._instance = None
        DatabaseConnection._instance = None

    def test_validators_import(self):
        """Testa importação dos Validators"""
        from ozempic_seguro.core.validators import Validators

        assert Validators is not None

    def test_cache_import(self):
        """Testa importação do Cache"""
        from ozempic_seguro.core.cache import MemoryCache, cached

        assert MemoryCache is not None
        assert cached is not None

    def test_security_functions(self):
        """Testa funções de segurança"""
        from ozempic_seguro.repositories.security import hash_password, verify_password

        # Testa hash
        senha = "TestPassword123"
        hashed = hash_password(senha)

        assert hashed is not None
        assert hashed != senha
        assert hashed.startswith("$2b$")

        # Testa verificação
        assert verify_password(senha, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_config_import(self):
        """Testa importação de Config"""
        from ozempic_seguro.config import Config

        assert Config is not None
        assert hasattr(Config, "Database")
        assert hasattr(Config, "Security")
        assert hasattr(Config, "UI")

    def test_session_basic_operations(self):
        """Testa operações básicas do SessionManager"""
        from ozempic_seguro.session.session_manager import SessionManager

        # Reset singleton
        SessionManager._instance = None

        session = SessionManager.get_instance()

        # Testa set/get user
        user = {"id": 1, "username": "test", "tipo": "vendedor"}
        session.set_current_user(user)

        assert session.get_current_user() == user
        assert session.is_logged_in() is True

        # Testa logout
        session.logout()
        assert session.get_current_user() is None
        assert session.is_logged_in() is False

        # Cleanup
        SessionManager._instance = None
