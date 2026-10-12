"""
Módulo core - Componentes fundamentais do sistema.

Fornece utilitários, validadores, cache, logging e exceções customizadas.
"""

from .cache import MemoryCache, cached
from .exceptions import (
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
from .logger import logger
from .validators import ValidationResult, Validators

__all__ = [
    "AccountLockedError",
    # Exceptions - Audit
    "AuditError",
    "AuditLogError",
    # Exceptions - Auth
    "AuthenticationError",
    # Exceptions - Config
    "ConfigurationError",
    # Exceptions - Database
    "DatabaseError",
    # Exceptions - Drawer
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
    # Cache
    "MemoryCache",
    "MigrationError",
    "MissingConfigError",
    # Exceptions - Base
    "OzempicError",
    "SessionExpiredError",
    "UserAlreadyExistsError",
    # Exceptions - User
    "UserError",
    "UserNotFoundError",
    # Exceptions - Validation
    "ValidationError",
    "ValidationResult",
    # Validators
    "Validators",
    "WeakPasswordError",
    "cached",
    # Logger
    "logger",
]
