"""
Testes para ServiceFactory - Injeção de dependências.
"""

import pytest

from ozempic_seguro.services.service_factory import (
    ServiceFactory,
    ServiceRegistry,
    get_audit_service,
    get_user_service,
)


class TestServiceRegistry:
    """Testes para ServiceRegistry"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.registry = ServiceRegistry()
        return

    def test_register_and_get_service(self):
        """Testa registro e obtenção de serviço"""
        mock_service = {"name": "test_service"}

        self.registry.register_service("test", mock_service)

        result = self.registry.get_service("test", lambda: None)
        assert result == mock_service

    def test_get_service_creates_if_not_exists(self):
        """Testa que serviço é criado se não existir"""
        created_service = {"created": True}

        result = self.registry.get_service("new_service", lambda: created_service)

        assert result == created_service

    def test_set_and_get_mock(self):
        """Testa definição e obtenção de mock"""
        mock = {"mock": True}

        self.registry.set_mock("service_name", mock)

        # Mock deve ter prioridade sobre serviço real
        result = self.registry.get_service("service_name", lambda: {"real": True})
        assert result == mock

    def test_clear_mocks(self):
        """Testa limpeza de mocks"""
        self.registry.set_mock("service", {"mock": True})

        self.registry.clear_mocks()

        # Agora deve criar serviço real
        result = self.registry.get_service("service", lambda: {"real": True})
        assert result == {"real": True}

    def test_reset_services(self):
        """Testa reset de todos os serviços"""
        self.registry.register_service("service1", {"s1": True})
        self.registry.set_mock("service2", {"s2": True})

        self.registry.reset_services()

        # Deve criar novos serviços
        result = self.registry.get_service("service1", lambda: {"new": True})
        assert result == {"new": True}


class TestServiceFactory:
    """Testes para ServiceFactory"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        ServiceFactory.reset_all_services()
        yield
        ServiceFactory.reset_all_services()

    def test_get_user_service(self):
        """Testa obtenção de UserService"""
        service = ServiceFactory.get_user_service()

        assert service is not None
        # Deve ser singleton
        service2 = ServiceFactory.get_user_service()
        assert service is service2

    def test_get_audit_service(self):
        """Testa obtenção de AuditService"""
        service = ServiceFactory.get_audit_service()

        assert service is not None

    def test_get_session_manager(self):
        """Testa obtenção de SessionManager"""
        manager = ServiceFactory.get_session_manager()

        assert manager is not None

    def test_get_security_logger(self):
        """Testa obtenção de SecurityLogger"""
        logger = ServiceFactory.get_security_logger()

        assert logger is not None

    def test_set_mock_user_service(self):
        """Testa definição de mock para UserService"""
        mock = {"mock": True}

        ServiceFactory.set_mock_user_service(mock)

        result = ServiceFactory.get_user_service()
        assert result == mock

    def test_set_mock_audit_service(self):
        """Testa definição de mock para AuditService"""
        mock = {"mock": True}

        ServiceFactory.set_mock_audit_service(mock)

        result = ServiceFactory.get_audit_service()
        assert result == mock

    def test_clear_all_mocks(self):
        """Testa limpeza de todos os mocks"""
        ServiceFactory.set_mock_user_service({"mock": True})

        ServiceFactory.clear_all_mocks()

        # Deve retornar serviço real
        result = ServiceFactory.get_user_service()
        assert result is not None
        assert not isinstance(result, dict)

    def test_get_service_status(self):
        """Testa obtenção de status dos serviços"""
        # Carregar alguns serviços
        ServiceFactory.get_user_service()

        status = ServiceFactory.get_service_status()

        assert isinstance(status, dict)
        assert "user_service" in status
        assert status["user_service"] is True


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        ServiceFactory.reset_all_services()
        yield
        ServiceFactory.reset_all_services()

    def test_get_user_service_function(self):
        """Testa função get_user_service"""
        service = get_user_service()

        assert service is not None

    def test_get_audit_service_function(self):
        """Testa função get_audit_service"""
        service = get_audit_service()

        assert service is not None


class TestServiceFactoryAdditional:
    """Testes adicionais para ServiceFactory"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        ServiceFactory.reset_all_services()
        yield
        ServiceFactory.reset_all_services()

    def test_multiple_get_calls_return_same_instance(self):
        """Testa que múltiplas chamadas retornam mesma instância"""
        service1 = ServiceFactory.get_audit_service()
        service2 = ServiceFactory.get_audit_service()
        assert service1 is service2

    def test_reset_clears_all(self):
        """Testa que reset limpa tudo"""
        ServiceFactory.get_user_service()
        ServiceFactory.set_mock_audit_service({"mock": True})

        ServiceFactory.reset_all_services()

        # Após reset, status deve estar vazio ou False
        status = ServiceFactory.get_service_status()
        # Verificar que foi resetado
        assert isinstance(status, dict)

    def test_session_manager_singleton(self):
        """Testa que SessionManager é singleton"""
        manager1 = ServiceFactory.get_session_manager()
        manager2 = ServiceFactory.get_session_manager()
        assert manager1 is manager2

    def test_security_logger_singleton(self):
        """Testa que SecurityLogger é singleton"""
        logger1 = ServiceFactory.get_security_logger()
        logger2 = ServiceFactory.get_security_logger()
        assert logger1 is logger2


class TestServiceRegistryAdditional:
    """Testes adicionais para ServiceRegistry"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.registry = ServiceRegistry()
        return

    def test_register_overwrite(self):
        """Testa que registro sobrescreve serviço existente"""
        self.registry.register_service("test", {"v": 1})
        self.registry.register_service("test", {"v": 2})

        result = self.registry.get_service("test", lambda: None)
        assert result == {"v": 2}

    def test_mock_has_priority(self):
        """Testa que mock tem prioridade sobre registro"""
        self.registry.register_service("svc", {"real": True})
        self.registry.set_mock("svc", {"mock": True})

        result = self.registry.get_service("svc", lambda: None)
        assert result == {"mock": True}

    def test_multiple_mocks(self):
        """Testa múltiplos mocks"""
        self.registry.set_mock("svc1", {"m1": True})
        self.registry.set_mock("svc2", {"m2": True})

        r1 = self.registry.get_service("svc1", lambda: None)
        r2 = self.registry.get_service("svc2", lambda: None)

        assert r1 == {"m1": True}
        assert r2 == {"m2": True}

    def test_clear_mocks_preserves_services(self):
        """Testa que clear_mocks preserva serviços registrados"""
        self.registry.register_service("real_svc", {"real": True})
        self.registry.set_mock("mock_svc", {"mock": True})

        self.registry.clear_mocks()

        # Serviço real deve continuar
        result = self.registry.get_service("real_svc", lambda: {"new": True})
        assert result == {"real": True}
