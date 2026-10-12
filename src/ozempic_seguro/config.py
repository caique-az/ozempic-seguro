"""
Configurações centralizadas do sistema Ozempic Seguro
"""

import logging
import os

# Logger para este módulo (não usa core.logger para evitar dependência circular)
_config_logger = logging.getLogger(__name__)


class SecurityConfig:
    """Configurações de segurança"""

    # Configurações de hash de senha
    BCRYPT_ROUNDS = 12

    # Configurações de sessão
    SESSION_TIMEOUT_MINUTES = 10

    # Configurações de tentativas de login
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 5  # Reduzido de 10 para 5 minutos

    # Configurações de validação
    MIN_PASSWORD_LENGTH = 4
    MAX_PASSWORD_LENGTH = 128
    MIN_USERNAME_LENGTH = 2
    MAX_USERNAME_LENGTH = 50
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100

    # Lista de tipos de usuário válidos
    VALID_USER_TYPES = ("administrador", "vendedor", "repositor", "tecnico")

    # Configurações de auditoria
    ENABLE_DETAILED_LOGGING = True
    LOG_IP_ADDRESSES = True
    LOG_SYSTEM_INFO = True

    # Configurações de backup
    BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30


class DatabaseConfig:
    """Configurações de banco de dados"""

    # Configurações de conexão
    DB_NAME = "ozempic_seguro.db"
    DB_TIMEOUT = 30.0
    DB_CHECK_SAME_THREAD = False

    # Configurações de performance
    ENABLE_WAL_MODE = True
    ENABLE_FOREIGN_KEYS = True
    CACHE_SIZE = 2000

    # Configurações de backup
    AUTO_BACKUP = True
    BACKUP_INTERVAL_HOURS = 24


class UIConfig:
    """Configurações da interface do usuário"""

    # Configurações de tema
    THEME_MODE = "light"
    THEME_COLOR = "blue"

    # Configurações de janela
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600

    # Configurações de fonte
    FONT_SIZE = 12
    FONT_FAMILY = "Arial"
    FONT_SIZE_SMALL = 11
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_MEDIUM = 13
    FONT_SIZE_LARGE = 14
    FONT_SIZE_TITLE = 16
    FONT_SIZE_HEADER = 24

    # Configurações de layout
    SIDEBAR_WIDTH = 250
    CONTENT_PADDING = 20

    # Layout da tela de login
    LOGIN_FRAME_X = 40
    LOGIN_FRAME_Y = 100
    LOGIN_KEYBOARD_X = 500
    LOGIN_KEYBOARD_Y = 100
    LOGIN_FRAME_COLOR = "#346172"
    LOGIN_ENTRY_WIDTH = 300
    LOGIN_ENTRY_HEIGHT = 40
    LOGIN_ENTRY_PADY = 10

    # Cores principais
    PRIMARY_BG_COLOR = "#3B6A7D"
    SECONDARY_BG_COLOR = "#2C5364"
    WHITE = "#FFFFFF"

    # Cores de status
    SUCCESS_COLOR = "#28A745"
    SUCCESS_BG = "#E8F5E9"
    SUCCESS_TEXT = "#2E7D32"

    WARNING_COLOR = "#FFC107"
    WARNING_BG = "#FFF3CD"
    WARNING_TEXT = "#856404"

    ERROR_COLOR = "#DC3545"
    ERROR_BG = "#FFEBEE"
    ERROR_TEXT = "#C62828"

    INFO_COLOR = "#2E86C1"

    # Cores de texto
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#666666"
    TEXT_LIGHT = "#999999"

    # Cores de borda
    BORDER_COLOR = "#E0E0E0"
    BORDER_LIGHT = "#CCCCCC"

    # Configurações de toast
    TOAST_START_X = 1.3
    TOAST_END_X = 0.98
    TOAST_Y = 0.02
    TOAST_ANIMATION_STEP = 0.04
    TOAST_ANIMATION_INTERVAL = 15  # ms
    TOAST_DEFAULT_DURATION = 3000  # ms

    # Configurações de transição
    TRANSITION_OVERLAY_COLOR = "#3B6A7D"


class LoggingConfig:
    """Configurações de logging"""

    # Configurações gerais
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Configurações de arquivo
    LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    LOG_ROTATION = True

    # Configurações de console
    CONSOLE_LOG_LEVEL = "ERROR"
    ENABLE_CONSOLE_COLORS = True


def _get_version() -> str:
    """Obtém versão do pacote via importlib.metadata ou setuptools-scm"""
    try:
        from importlib.metadata import version

        return version("ozempic-seguro")
    except Exception:
        try:
            from ._version import version as scm_version

            return scm_version
        except Exception:
            return "1.3.4"  # Fallback


class AppConfig:
    """Configurações gerais da aplicação"""

    # Informações da aplicação
    APP_NAME = "Ozempic Seguro"
    APP_VERSION = _get_version()
    APP_AUTHOR = "Caique Azevedo"

    # Configurações de sistema
    ENABLE_DEBUG_MODE = False
    CHECK_FOR_UPDATES = True

    # Configurações de diretórios
    DATA_DIR = "data"
    LOGS_DIR = "logs"
    BACKUP_DIR = "backups"
    MIGRATIONS_DIR = "migrations"

    # Configurações de performance
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 300  # 5 minutos


# Classe principal que agrega todas as configurações
class Config:
    """Configuração principal que agrega todas as outras"""

    Security = SecurityConfig
    Database = DatabaseConfig
    UI = UIConfig
    Logging = LoggingConfig
    App = AppConfig

    @classmethod
    def get_all_configs(cls) -> dict:
        """Retorna todas as configurações como dicionário"""
        return {
            "security": cls.Security.__dict__,
            "database": cls.Database.__dict__,
            "ui": cls.UI.__dict__,
            "logging": cls.Logging.__dict__,
            "app": cls.App.__dict__,
        }

    @classmethod
    def validate_configs(cls) -> bool:
        """Valida se todas as configurações estão corretas"""
        try:
            # Validações básicas
            assert cls.Security.SESSION_TIMEOUT_MINUTES > 0
            assert cls.Security.MAX_LOGIN_ATTEMPTS > 0
            assert cls.Security.BCRYPT_ROUNDS >= 10
            assert cls.Database.DB_TIMEOUT > 0
            assert cls.UI.WINDOW_WIDTH > 0
            assert cls.UI.WINDOW_HEIGHT > 0
            return True
        except AssertionError:
            return False


def validate_config() -> bool:
    """
    Valida todas as configurações na inicialização

    Returns:
        bool: True se todas as configurações são válidas
    """
    try:
        # Validar configurações de segurança
        assert SecurityConfig.BCRYPT_ROUNDS >= 10, "BCRYPT_ROUNDS deve ser >= 10"
        assert SecurityConfig.SESSION_TIMEOUT_MINUTES > 0, "SESSION_TIMEOUT_MINUTES deve ser > 0"
        assert SecurityConfig.MAX_LOGIN_ATTEMPTS > 0, "MAX_LOGIN_ATTEMPTS deve ser > 0"
        assert SecurityConfig.MIN_PASSWORD_LENGTH >= 4, "MIN_PASSWORD_LENGTH deve ser >= 4"

        # Validar configurações de UI
        assert UIConfig.WINDOW_WIDTH > 0, "WINDOW_WIDTH deve ser > 0"
        assert UIConfig.WINDOW_HEIGHT > 0, "WINDOW_HEIGHT deve ser > 0"

        return True

    except AssertionError as e:
        _config_logger.error(f"Erro de configuração: {e}")
        return False
    except Exception as e:
        _config_logger.error(f"Erro inesperado na validação de configuração: {e}")
        return False


# Configurações para diferentes ambientes
class EnvironmentConfig:
    """Configurações específicas por ambiente"""

    @staticmethod
    def is_development():
        return os.getenv("OZEMPIC_ENV", "production").lower() == "development"

    @staticmethod
    def is_production():
        return not EnvironmentConfig.is_development()

    @staticmethod
    def get_config():
        """Retorna configurações baseadas no ambiente"""
        if EnvironmentConfig.is_development():
            return {
                "log_level": "DEBUG",
                "detailed_logging": True,
                "session_timeout": 60,  # 1 hora em dev
            }
        return {
            "log_level": "INFO",
            "detailed_logging": SecurityConfig.ENABLE_DETAILED_LOGGING,
            "session_timeout": SecurityConfig.SESSION_TIMEOUT_MINUTES,
        }
