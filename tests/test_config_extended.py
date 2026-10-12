"""
Testes estendidos para Config - Cobertura adicional.
"""

from ozempic_seguro.config import (
    AppConfig,
    Config,
    DatabaseConfig,
    EnvironmentConfig,
    LoggingConfig,
    SecurityConfig,
    UIConfig,
)


class TestSecurityConfigExtended:
    """Testes estendidos para SecurityConfig"""

    def test_max_login_attempts(self):
        """Testa MAX_LOGIN_ATTEMPTS"""
        assert isinstance(SecurityConfig.MAX_LOGIN_ATTEMPTS, int)
        assert SecurityConfig.MAX_LOGIN_ATTEMPTS > 0

    def test_lockout_duration(self):
        """Testa LOCKOUT_DURATION_MINUTES"""
        assert isinstance(SecurityConfig.LOCKOUT_DURATION_MINUTES, int)
        assert SecurityConfig.LOCKOUT_DURATION_MINUTES > 0

    def test_session_timeout(self):
        """Testa SESSION_TIMEOUT_MINUTES"""
        assert isinstance(SecurityConfig.SESSION_TIMEOUT_MINUTES, int)
        assert SecurityConfig.SESSION_TIMEOUT_MINUTES > 0

    def test_bcrypt_rounds(self):
        """Testa BCRYPT_ROUNDS"""
        assert isinstance(SecurityConfig.BCRYPT_ROUNDS, int)
        assert SecurityConfig.BCRYPT_ROUNDS >= 10


class TestDatabaseConfigExtended:
    """Testes estendidos para DatabaseConfig"""

    def test_db_name(self):
        """Testa DB_NAME"""
        assert isinstance(DatabaseConfig.DB_NAME, str)
        assert len(DatabaseConfig.DB_NAME) > 0

    def test_enable_foreign_keys(self):
        """Testa ENABLE_FOREIGN_KEYS"""
        assert isinstance(DatabaseConfig.ENABLE_FOREIGN_KEYS, bool)

    def test_enable_wal_mode(self):
        """Testa ENABLE_WAL_MODE"""
        assert isinstance(DatabaseConfig.ENABLE_WAL_MODE, bool)

    def test_cache_size(self):
        """Testa CACHE_SIZE"""
        assert isinstance(DatabaseConfig.CACHE_SIZE, int)


class TestUIConfigExtended:
    """Testes estendidos para UIConfig"""

    def test_window_width(self):
        """Testa WINDOW_WIDTH"""
        assert isinstance(UIConfig.WINDOW_WIDTH, int)
        assert UIConfig.WINDOW_WIDTH > 0

    def test_window_height(self):
        """Testa WINDOW_HEIGHT"""
        assert isinstance(UIConfig.WINDOW_HEIGHT, int)
        assert UIConfig.WINDOW_HEIGHT > 0

    def test_theme_mode(self):
        """Testa THEME_MODE"""
        assert isinstance(UIConfig.THEME_MODE, str)
        assert UIConfig.THEME_MODE in ["dark", "light", "system"]

    def test_theme_color(self):
        """Testa THEME_COLOR"""
        assert isinstance(UIConfig.THEME_COLOR, str)


class TestLoggingConfigExtended:
    """Testes estendidos para LoggingConfig"""

    def test_log_level(self):
        """Testa LOG_LEVEL"""
        assert isinstance(LoggingConfig.LOG_LEVEL, str)
        assert LoggingConfig.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_log_format(self):
        """Testa LOG_FORMAT"""
        assert isinstance(LoggingConfig.LOG_FORMAT, str)


class TestAppConfigExtended:
    """Testes estendidos para AppConfig"""

    def test_app_name(self):
        """Testa APP_NAME"""
        assert isinstance(AppConfig.APP_NAME, str)
        assert len(AppConfig.APP_NAME) > 0

    def test_data_dir(self):
        """Testa DATA_DIR"""
        assert isinstance(AppConfig.DATA_DIR, str)

    def test_migrations_dir(self):
        """Testa MIGRATIONS_DIR"""
        assert isinstance(AppConfig.MIGRATIONS_DIR, str)


class TestEnvironmentConfigExtended:
    """Testes estendidos para EnvironmentConfig"""

    def test_is_development(self):
        """Testa is_development"""
        result = EnvironmentConfig.is_development()
        assert isinstance(result, bool)

    def test_is_production(self):
        """Testa is_production"""
        result = EnvironmentConfig.is_production()
        assert isinstance(result, bool)


class TestConfigAlias:
    """Testes para alias Config"""

    def test_config_security(self):
        """Testa Config.Security"""
        assert Config.Security is SecurityConfig

    def test_config_database(self):
        """Testa Config.Database"""
        assert Config.Database is DatabaseConfig

    def test_config_ui(self):
        """Testa Config.UI"""
        assert Config.UI is UIConfig

    def test_config_logging(self):
        """Testa Config.Logging"""
        assert Config.Logging is LoggingConfig

    def test_config_app(self):
        """Testa Config.App"""
        assert Config.App is AppConfig
