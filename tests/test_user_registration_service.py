"""
Testes para UserRegistrationService - Serviço de registro de usuário.
"""

import uuid

import pytest

from ozempic_seguro.services.user_registration_service import (
    RegistrationResult,
    UserRegistrationService,
    get_user_registration_service,
)


class TestUserRegistrationService:
    """Testes para UserRegistrationService"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserRegistrationService()
        return

    def test_register_valid_user(self):
        """Testa registro de usuário válido"""
        unique_username = str(uuid.uuid4().int)[:8]

        result = self.service.register(
            name="Test User", username=unique_username, password="1234", user_type="vendedor"
        )

        assert isinstance(result, RegistrationResult)
        assert result.success is True

    def test_register_empty_name(self):
        """Testa registro com nome vazio"""
        result = self.service.register(
            name="", username="12345678", password="1234", user_type="vendedor"
        )

        assert result.success is False
        assert len(result.errors) > 0

    def test_register_empty_username(self):
        """Testa registro com username vazio"""
        result = self.service.register(
            name="Test User", username="", password="1234", user_type="vendedor"
        )

        assert result.success is False
        assert len(result.errors) > 0

    def test_register_empty_password(self):
        """Testa registro com senha vazia"""
        result = self.service.register(
            name="Test User", username="12345678", password="", user_type="vendedor"
        )

        assert result.success is False
        assert len(result.errors) > 0

    def test_register_name_too_long(self):
        """Testa registro com nome muito longo"""
        result = self.service.register(
            name="A" * 30,  # Mais de 26 caracteres
            username="12345678",
            password="1234",
            user_type="vendedor",
        )

        assert result.success is False
        assert any("nome" in e.lower() for e in result.errors)

    def test_register_username_too_long(self):
        """Testa registro com username muito longo"""
        result = self.service.register(
            name="Test User",
            username="123456789",  # More than 8 digits
            password="1234",
            user_type="vendedor",
        )

        assert result.success is False
        assert any("usuário" in e.lower() for e in result.errors)

    def test_register_username_not_numeric(self):
        """Testa registro com username não numérico"""
        result = self.service.register(
            name="Test User", username="abc12345", password="1234", user_type="vendedor"
        )

        assert result.success is False
        assert any("número" in e.lower() for e in result.errors)

    def test_register_password_too_short(self):
        """Testa registro com senha muito curta"""
        result = self.service.register(
            name="Test User",
            username="12345678",
            password="123",  # Less than 4 characters
            user_type="vendedor",
        )

        assert result.success is False
        assert any("mínimo" in e.lower() for e in result.errors)

    def test_register_password_too_long(self):
        """Testa registro com senha muito longa"""
        result = self.service.register(
            name="Test User",
            username="12345678",
            password="123456789",  # More than 8 digits
            user_type="vendedor",
        )

        assert result.success is False
        assert any("máximo" in e.lower() for e in result.errors)

    def test_register_password_not_numeric(self):
        """Testa registro com senha não numérica"""
        result = self.service.register(
            name="Test User", username="12345678", password="abc1", user_type="vendedor"
        )

        assert result.success is False
        assert any("número" in e.lower() for e in result.errors)

    def test_register_invalid_type(self):
        """Testa registro com tipo inválido"""
        result = self.service.register(
            name="Test User", username="12345678", password="1234", user_type="invalid_type"
        )

        assert result.success is False
        assert any("tipo" in e.lower() for e in result.errors)


class TestValidationMethods:
    """Testes para métodos de validação"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada teste"""
        self.service = UserRegistrationService()
        return

    def test_validate_name_valid(self):
        """Testa validação de nome válido"""
        assert self.service.validate_name("Test User") is True

    def test_validate_name_too_long(self):
        """Testa validação de nome muito longo"""
        assert self.service.validate_name("A" * 30) is False

    def test_validate_username_valid(self):
        """Testa validação de username válido"""
        assert self.service.validate_username("12345678") is True

    def test_validate_username_not_numeric(self):
        """Testa validação de username não numérico"""
        assert self.service.validate_username("abc12345") is False

    def test_validate_password_valid(self):
        """Testa validação de senha válida"""
        assert self.service.validate_password("1234") is True

    def test_validate_password_too_short(self):
        """Testa validação de senha muito curta"""
        assert self.service.validate_password("123") is False


class TestRegistrationResult:
    """Testes para RegistrationResult"""

    def test_success_result(self):
        """Testa criação de resultado de sucesso"""
        result = RegistrationResult(success=True, message="Usuário cadastrado com sucesso!")

        assert result.success is True
        assert result.message == "Usuário cadastrado com sucesso!"
        assert result.errors == []

    def test_failure_result(self):
        """Testa criação de resultado de falha"""
        result = RegistrationResult(
            success=False,
            message="Dados inválidos",
            errors=["Nome muito longo", "Senha muito curta"],
        )

        assert result.success is False
        assert len(result.errors) == 2


class TestGetUserRegistrationService:
    """Testes para função get_user_registration_service"""

    def test_returns_service(self):
        """Testa que retorna UserRegistrationService"""
        service = get_user_registration_service()

        assert isinstance(service, UserRegistrationService)
