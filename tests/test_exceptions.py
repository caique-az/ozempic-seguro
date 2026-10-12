"""
Testes para exceções customizadas do sistema.

Verifica hierarquia, mensagens e serialização das exceções.
"""

import pytest

from ozempic_seguro.core.exceptions import (
    AccountLockedError,
    # Audit
    AuditError,
    AuditLogError,
    # Authentication
    AuthenticationError,
    # Configuration
    ConfigurationError,
    # Database
    DatabaseError,
    # Drawer
    DrawerError,
    DrawerNotFoundError,
    DrawerStateError,
    InsufficientPermissionsError,
    IntegrityError,
    InvalidConfigError,
    InvalidCredentialsError,
    InvalidInputError,
    InvalidUserDataError,
    InvalidUsernameError,
    LastAdminError,
    MigrationError,
    MissingConfigError,
    # Base
    OzempicError,
    SessionExpiredError,
    UserAlreadyExistsError,
    # User
    UserError,
    UserNotFoundError,
    # Validation
    ValidationError,
    WeakPasswordError,
)


class TestExceptionHierarchy:
    """Testa hierarquia de exceções"""

    def test_all_exceptions_inherit_from_ozempic_error(self):
        """Todas as exceções devem herdar de OzempicError"""
        exceptions = [
            AuthenticationError,
            InvalidCredentialsError,
            SessionExpiredError,
            AccountLockedError,
            InsufficientPermissionsError,
            UserError,
            UserNotFoundError,
            UserAlreadyExistsError,
            LastAdminError,
            InvalidUserDataError,
            ValidationError,
            InvalidUsernameError,
            WeakPasswordError,
            InvalidInputError,
            DatabaseError,
            MigrationError,
            IntegrityError,
            DrawerError,
            DrawerNotFoundError,
            DrawerStateError,
            AuditError,
            AuditLogError,
            ConfigurationError,
            MissingConfigError,
            InvalidConfigError,
        ]

        for exc_class in exceptions:
            assert issubclass(
                exc_class, OzempicError
            ), f"{exc_class.__name__} should inherit from OzempicError"

    def test_auth_exceptions_inherit_from_authentication_error(self):
        """Exceções de auth devem herdar de AuthenticationError"""
        auth_exceptions = [
            InvalidCredentialsError,
            SessionExpiredError,
            AccountLockedError,
        ]

        for exc_class in auth_exceptions:
            assert issubclass(exc_class, AuthenticationError)

    def test_user_exceptions_inherit_from_user_error(self):
        """Exceções de usuário devem herdar de UserError"""
        user_exceptions = [
            UserNotFoundError,
            UserAlreadyExistsError,
            LastAdminError,
            InvalidUserDataError,
        ]

        for exc_class in user_exceptions:
            assert issubclass(exc_class, UserError)


class TestExceptionMessages:
    """Testa mensagens e códigos das exceções"""

    def test_ozempic_error_default_message(self):
        """OzempicError deve ter mensagem padrão"""
        exc = OzempicError()
        assert exc.message == "Erro interno do sistema"
        assert exc.code == "OZEMPIC_ERROR"

    def test_invalid_credentials_error(self):
        """InvalidCredentialsError deve incluir username"""
        exc = InvalidCredentialsError(username="testuser")
        assert "testuser" in str(exc.details)
        assert exc.code == "INVALID_CREDENTIALS"

    def test_account_locked_error(self):
        """AccountLockedError deve incluir detalhes do bloqueio"""
        exc = AccountLockedError(username="testuser", locked_until="10 minutos", attempts=5)
        assert exc.details["username"] == "testuser"
        assert exc.details["locked_until"] == "10 minutos"
        assert exc.details["attempts"] == 5
        assert exc.code == "ACCOUNT_LOCKED"

    def test_user_not_found_error(self):
        """UserNotFoundError deve incluir identificador"""
        exc = UserNotFoundError(identifier=123, field="id")
        assert "123" in exc.message
        assert exc.code == "USER_NOT_FOUND"

    def test_user_already_exists_error(self):
        """UserAlreadyExistsError deve incluir username"""
        exc = UserAlreadyExistsError(username="existinguser")
        assert "existinguser" in exc.message
        assert exc.code == "USER_ALREADY_EXISTS"

    def test_last_admin_error(self):
        """LastAdminError deve ter mensagem específica"""
        exc = LastAdminError()
        assert "último administrador" in exc.message.lower()
        assert exc.code == "LAST_ADMIN_ERROR"

    def test_weak_password_error(self):
        """WeakPasswordError deve listar razões"""
        reasons = ["muito curta", "sem número", "sem maiúscula"]
        exc = WeakPasswordError(reasons=reasons)
        assert exc.details["reasons"] == reasons
        assert exc.code == "WEAK_PASSWORD"

    def test_insufficient_permissions_error(self):
        """InsufficientPermissionsError deve incluir ação e roles"""
        exc = InsufficientPermissionsError(
            action="excluir_usuario", required_role="administrador", user_role="vendedor"
        )
        assert exc.details["action"] == "excluir_usuario"
        assert exc.details["required_role"] == "administrador"
        assert exc.details["user_role"] == "vendedor"


class TestExceptionSerialization:
    """Testa serialização das exceções"""

    def test_to_dict_includes_all_fields(self):
        """to_dict deve incluir todos os campos"""
        exc = UserNotFoundError(identifier=123)
        result = exc.to_dict()

        assert "error" in result
        assert "code" in result
        assert "message" in result
        assert "details" in result

        assert result["error"] == "UserNotFoundError"
        assert result["code"] == "USER_NOT_FOUND"

    def test_str_format_with_details(self):
        """__str__ deve formatar com detalhes"""
        exc = InvalidCredentialsError(username="testuser")
        str_repr = str(exc)

        assert "[INVALID_CREDENTIALS]" in str_repr
        assert "testuser" in str_repr

    def test_str_format_without_details(self):
        """__str__ deve funcionar sem detalhes"""
        exc = OzempicError(message="Test error", code="TEST")
        str_repr = str(exc)

        assert "[TEST]" in str_repr
        assert "Test error" in str_repr


class TestExceptionRaising:
    """Testa que exceções podem ser levantadas e capturadas corretamente"""

    def test_catch_specific_exception(self):
        """Deve capturar exceção específica"""
        with pytest.raises(UserNotFoundError) as exc_info:
            raise UserNotFoundError(identifier=999)

        assert exc_info.value.code == "USER_NOT_FOUND"

    def test_catch_parent_exception(self):
        """Deve capturar exceção pai"""
        with pytest.raises(UserError):
            raise UserNotFoundError(identifier=999)

    def test_catch_base_exception(self):
        """Deve capturar exceção base"""
        with pytest.raises(OzempicError):
            raise InvalidCredentialsError(username="test")

    def test_exception_chaining(self):
        """Deve suportar encadeamento de exceções"""

        def fail():
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DatabaseError("Database failed") from e

        with pytest.raises(DatabaseError) as exc_info:
            fail()

        assert isinstance(exc_info.value.__cause__, ValueError)


class TestDatabaseExceptions:
    """Testes para exceções de banco de dados"""

    def test_migration_error(self):
        """Testa MigrationError"""
        exc = MigrationError("v1_to_v2", "syntax error")
        assert exc.code == "MIGRATION_ERROR"
        assert "v1_to_v2" in exc.message
        assert exc.details["migration"] == "v1_to_v2"
        assert exc.details["reason"] == "syntax error"

    def test_integrity_error(self):
        """Testa IntegrityError"""
        exc = IntegrityError("unique_username")
        assert exc.code == "INTEGRITY_ERROR"
        assert "unique_username" in exc.message


class TestDrawerExceptions:
    """Testes para exceções de gaveta"""

    def test_drawer_not_found_error(self):
        """Testa DrawerNotFoundError"""
        exc = DrawerNotFoundError(5)
        assert exc.code == "DRAWER_NOT_FOUND"
        assert exc.details["drawer_id"] == 5
        assert "5" in exc.message

    def test_drawer_state_error(self):
        """Testa DrawerStateError"""
        exc = DrawerStateError(1, "aberta", "abrir")
        assert exc.code == "DRAWER_STATE_ERROR"
        assert exc.details["drawer_id"] == 1
        assert exc.details["current_state"] == "aberta"
        assert exc.details["requested_state"] == "abrir"


class TestAuditExceptions:
    """Testes para exceções de auditoria"""

    def test_audit_log_error(self):
        """Testa AuditLogError"""
        exc = AuditLogError("LOGIN", "database unavailable")
        assert exc.code == "AUDIT_LOG_ERROR"
        assert exc.details["action"] == "LOGIN"
        assert exc.details["reason"] == "database unavailable"


class TestConfigExceptions:
    """Testes para exceções de configuração"""

    def test_missing_config_error(self):
        """Testa MissingConfigError"""
        exc = MissingConfigError("DATABASE_URL")
        assert exc.code == "MISSING_CONFIG"
        assert exc.details["config_key"] == "DATABASE_URL"
        assert "DATABASE_URL" in exc.message

    def test_invalid_config_error(self):
        """Testa InvalidConfigError"""
        exc = InvalidConfigError("TIMEOUT", -1, "must be positive")
        assert exc.code == "INVALID_CONFIG"
        assert exc.details["config_key"] == "TIMEOUT"
        assert exc.details["reason"] == "must be positive"


class TestValidationExceptions:
    """Testes para exceções de validação"""

    def test_invalid_username_error(self):
        """Testa InvalidUsernameError"""
        exc = InvalidUsernameError("ab@c", "contains special chars")
        assert exc.code == "INVALID_USERNAME"
        assert exc.details["username"] == "ab@c"
        assert exc.details["reason"] == "contains special chars"

    def test_invalid_input_error(self):
        """Testa InvalidInputError"""
        exc = InvalidInputError("email", "not@valid", "invalid format")
        assert exc.code == "INVALID_INPUT"
        assert exc.details["field"] == "email"
        assert exc.details["reason"] == "invalid format"

    def test_invalid_user_data_error(self):
        """Testa InvalidUserDataError"""
        exc = InvalidUserDataError("nome", "cannot be empty")
        assert exc.code == "INVALID_USER_DATA"
        assert exc.details["field"] == "nome"
        assert exc.details["reason"] == "cannot be empty"


class TestSessionExceptions:
    """Testes para exceções de sessão"""

    def test_session_expired_error(self):
        """Testa SessionExpiredError"""
        exc = SessionExpiredError()
        assert exc.code == "SESSION_EXPIRED"
        assert "expirada" in exc.message.lower()

    def test_session_expired_error_custom_message(self):
        """Testa SessionExpiredError com mensagem customizada"""
        exc = SessionExpiredError("Sessão encerrada por inatividade")
        assert "inatividade" in exc.message


class TestBaseExceptionFeatures:
    """Testes para features da exceção base"""

    def test_ozempic_error_with_details(self):
        """Testa OzempicError com detalhes"""
        details = {"key": "value", "number": 42}
        exc = OzempicError("Test", "TEST_CODE", details)
        assert exc.details == details

    def test_to_dict_error_class_name(self):
        """Testa que to_dict inclui nome da classe"""
        exc = LastAdminError()
        result = exc.to_dict()
        assert result["error"] == "LastAdminError"

    def test_inheritance_preserves_details(self):
        """Testa que herança preserva detalhes"""
        exc = AccountLockedError("user1", "2025-01-01", 3)
        assert "user1" in str(exc)
        assert exc.details["username"] == "user1"
