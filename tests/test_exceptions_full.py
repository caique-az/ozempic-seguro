"""
Testes completos para exceções customizadas.
"""

import pytest

from ozempic_seguro.core.exceptions import (
    OzempicError,
    DatabaseError,
    DatabaseConnectionError,
    AuthenticationError,
    InvalidCredentialsError,
    AccountLockedError,
    SessionExpiredError,
    ValidationError,
    InvalidUserDataError,
    WeakPasswordError,
    UserNotFoundError,
    UserAlreadyExistsError,
    LastAdminError,
    DrawerError,
    DrawerNotFoundError,
    DrawerStateError,
    ConfigurationError,
    MissingConfigError,
    InvalidConfigError,
)


class TestBaseExceptions:
    """Testes para exceções base"""

    def test_ozempic_error(self):
        """Testa exceção base"""
        with pytest.raises(OzempicError):
            raise OzempicError("Test error")

    def test_ozempic_error_message(self):
        """Testa mensagem da exceção base"""
        try:
            raise OzempicError("Custom message")
        except OzempicError as e:
            assert "Custom message" in str(e)

    def test_ozempic_error_to_dict(self):
        """Testa conversão para dict"""
        error = OzempicError("Test", "TEST_CODE", {"key": "value"})
        result = error.to_dict()

        assert result["error"] == "OzempicError"
        assert result["code"] == "TEST_CODE"
        assert result["message"] == "Test"


class TestDatabaseExceptions:
    """Testes para exceções de banco de dados"""

    def test_database_error(self):
        """Testa DatabaseError"""
        with pytest.raises(DatabaseError):
            raise DatabaseError("DB error")

    def test_connection_error(self):
        """Testa DatabaseConnectionError"""
        with pytest.raises(DatabaseConnectionError):
            raise DatabaseConnectionError()

    def test_database_error_inheritance(self):
        """Testa herança de DatabaseError"""
        with pytest.raises(OzempicError):
            raise DatabaseError("DB error")


class TestAuthenticationExceptions:
    """Testes para exceções de autenticação"""

    def test_authentication_error(self):
        """Testa AuthenticationError"""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Auth failed")

    def test_invalid_credentials_error(self):
        """Testa InvalidCredentialsError"""
        with pytest.raises(InvalidCredentialsError):
            raise InvalidCredentialsError("testuser")

    def test_account_locked_error(self):
        """Testa AccountLockedError"""
        with pytest.raises(AccountLockedError):
            raise AccountLockedError("testuser")

    def test_session_expired_error(self):
        """Testa SessionExpiredError"""
        with pytest.raises(SessionExpiredError):
            raise SessionExpiredError()

    def test_auth_error_inheritance(self):
        """Testa herança de AuthenticationError"""
        with pytest.raises(OzempicError):
            raise InvalidCredentialsError()


class TestValidationExceptions:
    """Testes para exceções de validação"""

    def test_validation_error(self):
        """Testa ValidationError"""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_invalid_user_data_error(self):
        """Testa InvalidUserDataError"""
        with pytest.raises(InvalidUserDataError):
            raise InvalidUserDataError("username", "too short")

    def test_weak_password_error(self):
        """Testa WeakPasswordError"""
        with pytest.raises(WeakPasswordError):
            raise WeakPasswordError(["too short", "no numbers"])

    def test_validation_error_inheritance(self):
        """Testa herança de ValidationError"""
        with pytest.raises(OzempicError):
            raise WeakPasswordError(["weak"])


class TestUserExceptions:
    """Testes para exceções de usuário"""

    def test_user_not_found_error(self):
        """Testa UserNotFoundError"""
        with pytest.raises(UserNotFoundError):
            raise UserNotFoundError(123)

    def test_user_already_exists_error(self):
        """Testa UserAlreadyExistsError"""
        with pytest.raises(UserAlreadyExistsError):
            raise UserAlreadyExistsError("testuser")

    def test_last_admin_error(self):
        """Testa LastAdminError"""
        with pytest.raises(LastAdminError):
            raise LastAdminError()


class TestDrawerExceptions:
    """Testes para exceções de gaveta"""

    def test_drawer_error(self):
        """Testa DrawerError"""
        with pytest.raises(DrawerError):
            raise DrawerError("Drawer error")

    def test_drawer_not_found_error(self):
        """Testa DrawerNotFoundError"""
        with pytest.raises(DrawerNotFoundError):
            raise DrawerNotFoundError(1)

    def test_drawer_state_error(self):
        """Testa DrawerStateError"""
        with pytest.raises(DrawerStateError):
            raise DrawerStateError(1, "aberta", "aberta")


class TestConfigurationExceptions:
    """Testes para exceções de configuração"""

    def test_configuration_error(self):
        """Testa ConfigurationError"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")

    def test_missing_config_error(self):
        """Testa MissingConfigError"""
        with pytest.raises(MissingConfigError):
            raise MissingConfigError("DB_PATH")

    def test_invalid_config_error(self):
        """Testa InvalidConfigError"""
        with pytest.raises(InvalidConfigError):
            raise InvalidConfigError("TIMEOUT", -1, "must be positive")
