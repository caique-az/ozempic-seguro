"""
Testes estendidos para exceções customizadas.
"""

from ozempic_seguro.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    ConfigurationError,
    DatabaseError,
    DrawerError,
    DrawerNotFoundError,
    DrawerStateError,
    IntegrityError,
    InvalidConfigError,
    InvalidCredentialsError,
    InvalidUserDataError,
    LastAdminError,
    MigrationError,
    MissingConfigError,
    OzempicError,
    SessionExpiredError,
    UserAlreadyExistsError,
    UserError,
    ValidationError,
    WeakPasswordError,
)


class TestOzempicError:
    """Testes para exceção base"""

    def test_ozempic_error_message(self):
        """Testa mensagem de erro"""
        error = OzempicError("Test error message")

        assert "Test error message" in str(error)

    def test_ozempic_error_with_details(self):
        """Testa erro com detalhes"""
        error = OzempicError("Test error", details={"key": "value"})

        assert error.details == {"key": "value"}


class TestAuthenticationErrors:
    """Testes para erros de autenticação"""

    def test_invalid_credentials_error(self):
        """Testa InvalidCredentialsError"""
        error = InvalidCredentialsError("admin")

        assert "admin" in str(error) or "INVALID_CREDENTIALS" in str(error)

    def test_session_expired_error(self):
        """Testa SessionExpiredError"""
        error = SessionExpiredError()

        assert isinstance(error, AuthenticationError)

    def test_account_locked_error(self):
        """Testa AccountLockedError"""
        error = AccountLockedError("testuser")

        assert isinstance(error, AuthenticationError)


class TestUserErrors:
    """Testes para erros de usuário"""

    def test_user_already_exists_error(self):
        """Testa UserAlreadyExistsError"""
        error = UserAlreadyExistsError("testuser")

        assert isinstance(error, UserError)

    def test_last_admin_error(self):
        """Testa LastAdminError"""
        error = LastAdminError()

        assert isinstance(error, UserError)

    def test_invalid_user_data_error(self):
        """Testa InvalidUserDataError"""
        error = InvalidUserDataError("username", "Username inválido")

        assert isinstance(error, UserError)


class TestValidationErrors:
    """Testes para erros de validação"""

    def test_validation_error(self):
        """Testa ValidationError"""
        error = ValidationError("Campo inválido")

        assert isinstance(error, OzempicError)

    def test_weak_password_error(self):
        """Testa WeakPasswordError"""
        error = WeakPasswordError(["Senha muito curta"])

        assert isinstance(error, ValidationError)


class TestDatabaseErrors:
    """Testes para erros de banco de dados"""

    def test_database_error(self):
        """Testa DatabaseError"""
        error = DatabaseError("Erro de conexão")

        assert isinstance(error, OzempicError)

    def test_migration_error(self):
        """Testa MigrationError"""
        error = MigrationError("001_initial.sql", "Erro na migração")

        assert isinstance(error, DatabaseError)

    def test_integrity_error(self):
        """Testa IntegrityError"""
        error = IntegrityError("UNIQUE constraint failed")

        assert isinstance(error, DatabaseError)


class TestDrawerErrors:
    """Testes para erros de gaveta"""

    def test_drawer_error(self):
        """Testa DrawerError"""
        error = DrawerError("Erro na gaveta")

        assert isinstance(error, OzempicError)

    def test_drawer_not_found_error(self):
        """Testa DrawerNotFoundError"""
        error = DrawerNotFoundError(1)

        assert isinstance(error, DrawerError)

    def test_drawer_state_error(self):
        """Testa DrawerStateError"""
        error = DrawerStateError(1, "aberta", "aberta")

        assert isinstance(error, DrawerError)


class TestConfigurationErrors:
    """Testes para erros de configuração"""

    def test_configuration_error(self):
        """Testa ConfigurationError"""
        error = ConfigurationError("Configuração inválida")

        assert isinstance(error, OzempicError)

    def test_missing_config_error(self):
        """Testa MissingConfigError"""
        error = MissingConfigError("DATABASE_URL")

        assert isinstance(error, ConfigurationError)

    def test_invalid_config_error(self):
        """Testa InvalidConfigError"""
        error = InvalidConfigError("MAX_ATTEMPTS", -1, "Deve ser positivo")

        assert isinstance(error, ConfigurationError)
