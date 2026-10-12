"""
Exceções customizadas do sistema Ozempic Seguro.

Hierarquia de exceções por domínio para tratamento de erros consistente.

Uso:
    from ozempic_seguro.core.exceptions import UserNotFoundError, AuthenticationError

    try:
        user = user_service.get_user(user_id)
    except UserNotFoundError as e:
        logger.warning(f"User not found: {e}")
    except AuthenticationError as e:
        logger.error(f"Auth failed: {e}")
"""

from typing import Any

# =============================================================================
# Base Exception
# =============================================================================


class OzempicError(Exception):
    """
    Exceção base para todas as exceções do sistema Ozempic Seguro.

    Attributes:
        message: Mensagem de erro legível
        code: Código de erro único para identificação
        details: Detalhes adicionais do erro
    """

    def __init__(
        self,
        message: str = "Erro interno do sistema",
        code: str = "OZEMPIC_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Converte exceção para dicionário (útil para logs e APIs)"""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        if self.details:
            return f"[{self.code}] {self.message} - {self.details}"
        return f"[{self.code}] {self.message}"


# =============================================================================
# Authentication & Authorization Exceptions
# =============================================================================


class AuthenticationError(OzempicError):
    """Erro de autenticação - credenciais inválidas ou expiradas"""

    def __init__(
        self,
        message: str = "Falha na autenticação",
        code: str = "AUTH_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class InvalidCredentialsError(AuthenticationError):
    """Credenciais (usuário/senha) inválidas"""

    def __init__(self, username: str | None = None, message: str = "Usuário ou senha inválidos"):
        details = {"username": username} if username else {}
        super().__init__(message, "INVALID_CREDENTIALS", details)


class SessionExpiredError(AuthenticationError):
    """Sessão expirada por timeout ou logout"""

    def __init__(self, message: str = "Sessão expirada"):
        super().__init__(message, "SESSION_EXPIRED")


class AccountLockedError(AuthenticationError):
    """Conta bloqueada por tentativas excessivas de login"""

    def __init__(self, username: str, locked_until: str | None = None, attempts: int | None = None):
        details = {"username": username, "locked_until": locked_until, "attempts": attempts}
        message = "Conta bloqueada temporariamente"
        super().__init__(message, "ACCOUNT_LOCKED", details)


class InsufficientPermissionsError(OzempicError):
    """Usuário não tem permissão para realizar a ação"""

    def __init__(self, action: str, required_role: str | None = None, user_role: str | None = None):
        details = {"action": action, "required_role": required_role, "user_role": user_role}
        message = f"Permissão insuficiente para: {action}"
        super().__init__(message, "INSUFFICIENT_PERMISSIONS", details)


# =============================================================================
# User Domain Exceptions
# =============================================================================


class UserError(OzempicError):
    """Exceção base para erros relacionados a usuários"""

    def __init__(
        self,
        message: str = "Erro de usuário",
        code: str = "USER_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class UserNotFoundError(UserError):
    """Usuário não encontrado no sistema"""

    def __init__(self, identifier: Any, field: str = "id"):
        details = {"field": field, "value": identifier}
        message = f"Usuário não encontrado: {field}={identifier}"
        super().__init__(message, "USER_NOT_FOUND", details)


class UserAlreadyExistsError(UserError):
    """Tentativa de criar usuário que já existe"""

    def __init__(self, username: str):
        details = {"username": username}
        message = f"Usuário já existe: {username}"
        super().__init__(message, "USER_ALREADY_EXISTS", details)


class LastAdminError(UserError):
    """Tentativa de remover/desativar o último administrador"""

    def __init__(self):
        message = "Não é possível remover o último administrador do sistema"
        super().__init__(message, "LAST_ADMIN_ERROR")


class InvalidUserDataError(UserError):
    """Dados de usuário inválidos"""

    def __init__(self, field: str, reason: str):
        details = {"field": field, "reason": reason}
        message = f"Dado inválido em '{field}': {reason}"
        super().__init__(message, "INVALID_USER_DATA", details)


# =============================================================================
# Validation Exceptions
# =============================================================================


class ValidationError(OzempicError):
    """Exceção base para erros de validação"""

    def __init__(
        self,
        message: str = "Erro de validação",
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class InvalidUsernameError(ValidationError):
    """Username inválido"""

    def __init__(self, username: str, reason: str):
        details = {"username": username, "reason": reason}
        message = f"Username inválido: {reason}"
        super().__init__(message, "INVALID_USERNAME", details)


class WeakPasswordError(ValidationError):
    """Senha não atende aos requisitos de segurança"""

    def __init__(self, reasons: list[str]):
        details = {"reasons": reasons}
        message = f"Senha fraca: {', '.join(reasons)}"
        super().__init__(message, "WEAK_PASSWORD", details)


class InvalidInputError(ValidationError):
    """Entrada de dados inválida genérica"""

    def __init__(self, field: str, value: Any, reason: str):
        details = {"field": field, "value": str(value)[:50], "reason": reason}
        message = f"Entrada inválida em '{field}': {reason}"
        super().__init__(message, "INVALID_INPUT", details)


# =============================================================================
# Database Exceptions
# =============================================================================


class DatabaseError(OzempicError):
    """Exceção base para erros de banco de dados"""

    def __init__(
        self,
        message: str = "Erro de banco de dados",
        code: str = "DATABASE_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class DatabaseConnectionError(DatabaseError):
    """Erro de conexão com o banco de dados"""

    def __init__(self, db_path: str | None = None):
        details = {"db_path": db_path} if db_path else {}
        message = "Falha na conexão com o banco de dados"
        super().__init__(message, "DB_CONNECTION_ERROR", details)


class MigrationError(DatabaseError):
    """Erro durante execução de migrations"""

    def __init__(self, migration_name: str, reason: str):
        details = {"migration": migration_name, "reason": reason}
        message = f"Falha na migration '{migration_name}': {reason}"
        super().__init__(message, "MIGRATION_ERROR", details)


class IntegrityError(DatabaseError):
    """Violação de integridade (constraint, unique, foreign key)"""

    def __init__(self, constraint: str, details: dict | None = None):
        message = f"Violação de integridade: {constraint}"
        super().__init__(message, "INTEGRITY_ERROR", details or {"constraint": constraint})


# =============================================================================
# Drawer (Gaveta) Exceptions
# =============================================================================


class DrawerError(OzempicError):
    """Exceção base para erros relacionados a gavetas"""

    def __init__(
        self,
        message: str = "Erro de gaveta",
        code: str = "DRAWER_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class DrawerNotFoundError(DrawerError):
    """Gaveta não encontrada"""

    def __init__(self, drawer_id: int):
        details = {"drawer_id": drawer_id}
        message = f"Gaveta não encontrada: {drawer_id}"
        super().__init__(message, "DRAWER_NOT_FOUND", details)


class DrawerStateError(DrawerError):
    """Estado inválido da gaveta (já aberta/fechada)"""

    def __init__(self, drawer_id: int, current_state: str, requested_state: str):
        details = {
            "drawer_id": drawer_id,
            "current_state": current_state,
            "requested_state": requested_state,
        }
        message = f"Gaveta {drawer_id} já está {current_state}"
        super().__init__(message, "DRAWER_STATE_ERROR", details)


# =============================================================================
# Audit Exceptions
# =============================================================================


class AuditError(OzempicError):
    """Exceção base para erros de auditoria"""

    def __init__(
        self,
        message: str = "Erro de auditoria",
        code: str = "AUDIT_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class AuditLogError(AuditError):
    """Falha ao registrar log de auditoria"""

    def __init__(self, action: str, reason: str):
        details = {"action": action, "reason": reason}
        message = f"Falha ao registrar auditoria para '{action}'"
        super().__init__(message, "AUDIT_LOG_ERROR", details)


# =============================================================================
# Configuration Exceptions
# =============================================================================


class ConfigurationError(OzempicError):
    """Erro de configuração do sistema"""

    def __init__(
        self,
        message: str = "Erro de configuração",
        code: str = "CONFIG_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code, details)


class MissingConfigError(ConfigurationError):
    """Configuração obrigatória ausente"""

    def __init__(self, config_key: str):
        details = {"config_key": config_key}
        message = f"Configuração obrigatória ausente: {config_key}"
        super().__init__(message, "MISSING_CONFIG", details)


class InvalidConfigError(ConfigurationError):
    """Valor de configuração inválido"""

    def __init__(self, config_key: str, value: Any, reason: str):
        details = {"config_key": config_key, "value": str(value), "reason": reason}
        message = f"Configuração inválida '{config_key}': {reason}"
        super().__init__(message, "INVALID_CONFIG", details)


# =============================================================================
# Export all exceptions
# =============================================================================

__all__ = [
    "AccountLockedError",
    # Audit
    "AuditError",
    "AuditLogError",
    # Authentication
    "AuthenticationError",
    # Configuration
    "ConfigurationError",
    "DatabaseConnectionError",
    # Database
    "DatabaseError",
    # Drawer
    "DrawerError",
    "DrawerNotFoundError",
    "DrawerStateError",
    "InsufficientPermissionsError",
    "IntegrityError",
    "InvalidConfigError",
    "InvalidCredentialsError",
    "InvalidInputError",
    "InvalidUserDataError",
    "InvalidUsernameError",
    "LastAdminError",
    "MigrationError",
    "MissingConfigError",
    # Base
    "OzempicError",
    "SessionExpiredError",
    "UserAlreadyExistsError",
    # User
    "UserError",
    "UserNotFoundError",
    # Validation
    "ValidationError",
    "WeakPasswordError",
]
