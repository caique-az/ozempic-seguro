from unittest.mock import Mock, patch

import pytest

from ozempic_seguro.repositories.database import DatabaseManager
from ozempic_seguro.services.audit_service import AuditService
from ozempic_seguro.services.user_service import UserService
from ozempic_seguro.session.session_manager import SessionManager


@pytest.fixture
def temp_db(tmp_path):
    """Cria um banco de dados temporário isolado para testes"""
    from ozempic_seguro.repositories.connection import DatabaseConnection

    db_path = str(tmp_path / "test_ozempic.db")

    # Reset singletons antes de criar novo
    DatabaseManager._instance = None
    DatabaseConnection._instance = None

    # Configurar DatabaseConnection para usar DB temporário
    with patch.object(DatabaseConnection, "_get_db_path", return_value=db_path):
        db_manager = DatabaseManager()

        yield db_manager

        # Fechar conexão antes de limpar
        if hasattr(db_manager, "conn"):
            db_manager.conn.close()

        # Reset singletons após teste
        DatabaseManager._instance = None
        DatabaseConnection._instance = None


@pytest.fixture
def mock_db():
    """Mock do DatabaseManager para testes que não precisam de DB real"""
    mock = Mock(spec=DatabaseManager)
    mock.execute_query.return_value = True
    mock.fetch_one.return_value = None
    mock.fetch_all.return_value = []
    return mock


@pytest.fixture
def user_service(temp_db):
    """Fixture para UserService com DB temporário"""
    with patch("ozempic_seguro.services.user_service.DatabaseManager") as mock_db_class:
        mock_db_class.return_value = temp_db
        return UserService()


@pytest.fixture
def audit_service(temp_db):
    """Fixture para AuditService com DB temporário"""
    with patch("ozempic_seguro.services.audit_service.DatabaseManager") as mock_db_class:
        mock_db_class.return_value = temp_db
        return AuditService()


@pytest.fixture
def session_manager():
    """Fixture para SessionManager limpo"""
    # Reset singleton
    SessionManager._instance = None
    session = SessionManager.get_instance()
    yield session
    # Cleanup
    session.cleanup()
    SessionManager._instance = None


@pytest.fixture
def sample_user():
    """Dados de usuário de exemplo para testes"""
    return {
        "id": 1,
        "username": "test_user",
        "nome_completo": "Usuário de Teste",
        "tipo": "vendedor",
        "ativo": True,
        "data_criacao": "2025-08-31 10:00:00",
    }


@pytest.fixture
def admin_user():
    """Dados de usuário administrador para testes"""
    return {
        "id": 2,
        "username": "admin",
        "nome_completo": "Administrador",
        "tipo": "administrador",
        "ativo": True,
        "data_criacao": "2025-08-31 10:00:00",
    }


@pytest.fixture
def mock_bcrypt():
    """Mock do bcrypt para testes de senha"""
    with patch("ozempic_seguro.repositories.security.bcrypt") as mock:
        mock.hashpw.return_value = b"$2b$12$mocked_hash"
        mock.checkpw.return_value = True
        yield mock


@pytest.fixture
def mock_datetime():
    """Mock do datetime para testes que dependem de tempo"""
    from datetime import datetime

    with patch("ozempic_seguro.session.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 8, 31, 12, 0, 0)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset de todos os singletons antes de cada teste para isolamento"""
    from ozempic_seguro.repositories.connection import DatabaseConnection
    from ozempic_seguro.services.service_factory import _registry

    # Reset registry
    _registry.reset_services()

    yield

    # Cleanup após teste
    _registry.reset_services()

    # Reset singletons de conexão usando método seguro
    if hasattr(DatabaseConnection, "reset_instance"):
        DatabaseConnection.reset_instance()
    else:
        DatabaseConnection._instance = None

    DatabaseManager._instance = None

    # Cleanup SessionManager
    if SessionManager._instance is not None:
        SessionManager._instance.cleanup()
        SessionManager._instance = None


@pytest.fixture
def mock_customtkinter():
    """Mock do CustomTkinter para testes de UI"""
    with (
        patch("customtkinter.CTk") as mock_ctk,
        patch("customtkinter.CTkFrame") as mock_frame,
        patch("customtkinter.CTkButton") as mock_button,
    ):
        yield {"CTk": mock_ctk, "CTkFrame": mock_frame, "CTkButton": mock_button}
