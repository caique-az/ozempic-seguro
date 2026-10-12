"""
Sistema de injeção de dependências robusto para serviços.

Implementa padrão Service Locator com suporte a:
- Singleton lazy loading
- Injeção de dependências configurável
- Mocks para testes
- Logging de criação de serviços
- Validação de dependências

Exemplo de uso:
    from ..services.service_factory import ServiceFactory

    # Obter serviços
    user_service = ServiceFactory.get_user_service()
    audit_service = ServiceFactory.get_audit_service()

    # Para testes - injetar mocks
    ServiceFactory.set_mock_user_service(mock_service)
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, TypeVar, cast

from ..config import Config
from ..core.logger import log_exceptions, logger

# Type variables para generic typing
T = TypeVar("T")
ServiceType = TypeVar("ServiceType")


class ServiceRegistry:
    """Registry thread-safe para gerenciar instâncias de serviços"""

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._mocks: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._config_validated = False

    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Registra uma instância de serviço"""
        with self._lock:
            self._services[service_name] = service_instance
            logger.debug(f"Service registered: {service_name}", extra={"service": service_name})

    def get_service(self, service_name: str, factory_func: Callable[[], T]) -> T:
        """Obtém um serviço, criando se necessário"""
        with self._lock:
            # Verificar mocks primeiro (para testes)
            if service_name in self._mocks:
                logger.debug(f"Returning mock service: {service_name}")
                return cast(T, self._mocks[service_name])

            # Verificar se já existe
            if service_name in self._services:
                return cast(T, self._services[service_name])

            # Validar configurações uma vez
            if not self._config_validated:
                if not Config.validate_configs():
                    raise RuntimeError("Invalid configuration detected")
                self._config_validated = True

            # Criar nova instância
            logger.info(f"Creating new service instance: {service_name}")
            try:
                service_instance = factory_func()
                self._services[service_name] = service_instance
                return service_instance
            except Exception as e:
                logger.error(f"Failed to create service {service_name}: {e!s}")
                raise

    def set_mock(self, service_name: str, mock_instance: Any) -> None:
        """Define um mock para testes"""
        with self._lock:
            self._mocks[service_name] = mock_instance
            logger.debug(f"Mock set for service: {service_name}")

    def clear_mocks(self) -> None:
        """Remove todos os mocks"""
        with self._lock:
            self._mocks.clear()
            logger.debug("All mocks cleared")

    def reset_services(self) -> None:
        """Reseta todos os serviços (útil para testes)"""
        with self._lock:
            self._services.clear()
            self._mocks.clear()
            self._config_validated = False
            logger.info("All services reset")


# Registry global
_registry = ServiceRegistry()


class ServiceFactory:
    """Factory principal para criação e acesso a serviços"""

    @staticmethod
    @log_exceptions("User Service Creation")
    def get_user_service():
        """Retorna instância singleton de UserService"""

        def create_user_service():
            from .user_service import UserService

            return UserService()

        return _registry.get_service("user_service", create_user_service)

    @staticmethod
    @log_exceptions("Audit Service Creation")
    def get_audit_service():
        """Retorna instância singleton de AuditService"""

        def create_audit_service():
            from .audit_service import AuditService

            return AuditService()

        return _registry.get_service("audit_service", create_audit_service)

    @staticmethod
    def get_session_manager():
        """Retorna instância singleton de SessionManager"""

        def create_session_manager():
            from ..session.session_manager import SessionManager

            return SessionManager.get_instance()

        return _registry.get_service("session_manager", create_session_manager)

    @staticmethod
    def get_security_logger():
        """Retorna instância singleton de SecurityLogger"""

        def create_security_logger():
            from ..repositories.security_logger import SecurityLogger

            return SecurityLogger()

        return _registry.get_service("security_logger", create_security_logger)

    @staticmethod
    @log_exceptions("Auth Service Creation")
    def get_auth_service():
        """Retorna instância singleton de AuthService"""

        def create_auth_service():
            from .auth_service import AuthService

            return AuthService()

        return _registry.get_service("auth_service", create_auth_service)

    # Métodos para testes
    @staticmethod
    def set_mock_user_service(mock_service: Any) -> None:
        """Define mock para UserService (apenas para testes)"""
        _registry.set_mock("user_service", mock_service)

    @staticmethod
    def set_mock_audit_service(mock_service: Any) -> None:
        """Define mock para AuditService (apenas para testes)"""
        _registry.set_mock("audit_service", mock_service)

    @staticmethod
    def set_mock_auth_service(mock_service: Any) -> None:
        """Define mock para AuthService (apenas para testes)"""
        _registry.set_mock("auth_service", mock_service)

    @staticmethod
    def clear_all_mocks() -> None:
        """Remove todos os mocks"""
        _registry.clear_mocks()

    @staticmethod
    def reset_all_services() -> None:
        """Reseta todos os serviços (útil para testes)"""
        _registry.reset_services()

    @staticmethod
    def get_service_status() -> dict[str, bool]:
        """Retorna status dos serviços carregados"""
        with _registry._lock:
            return {
                "user_service": "user_service" in _registry._services,
                "audit_service": "audit_service" in _registry._services,
                "database_manager": "database_manager" in _registry._services,
                "session_manager": "session_manager" in _registry._services,
                "security_logger": "security_logger" in _registry._services,
                "auth_service": "auth_service" in _registry._services,
            }


# Funções de conveniência para backwards compatibility
def get_user_service():
    """Função de conveniência para obter UserService"""
    return ServiceFactory.get_user_service()


def get_audit_service():
    """Função de conveniência para obter AuditService"""
    return ServiceFactory.get_audit_service()


def get_auth_service():
    """Função de conveniência para obter AuthService"""
    return ServiceFactory.get_auth_service()


__all__ = [
    "ServiceFactory",
    "get_audit_service",
    "get_auth_service",
    "get_user_service",
]
