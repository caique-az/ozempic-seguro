"""
Testes para módulo de configuração.
"""

from ozempic_seguro.config import (
    AppConfig,
    Config,
    DatabaseConfig,
    EnvironmentConfig,
    LoggingConfig,
    SecurityConfig,
    UIConfig,
    validate_config,
)


class TestSecurityConfig:
    """Testes para SecurityConfig"""

    def test_bcrypt_rounds_minimum(self):
        """Testa que BCRYPT_ROUNDS é pelo menos 10"""
        assert SecurityConfig.BCRYPT_ROUNDS >= 10

    def test_session_timeout_positive(self):
        """Testa que SESSION_TIMEOUT_MINUTES é positivo"""
        assert SecurityConfig.SESSION_TIMEOUT_MINUTES > 0

    def test_max_login_attempts_positive(self):
        """Testa que MAX_LOGIN_ATTEMPTS é positivo"""
        assert SecurityConfig.MAX_LOGIN_ATTEMPTS > 0

    def test_lockout_duration_positive(self):
        """Testa que LOCKOUT_DURATION_MINUTES é positivo"""
        assert SecurityConfig.LOCKOUT_DURATION_MINUTES > 0

    def test_password_length_constraints(self):
        """Testa constraints de tamanho de senha"""
        assert SecurityConfig.MIN_PASSWORD_LENGTH >= 4
        assert SecurityConfig.MAX_PASSWORD_LENGTH > SecurityConfig.MIN_PASSWORD_LENGTH

    def test_username_length_constraints(self):
        """Testa constraints de tamanho de username"""
        assert SecurityConfig.MIN_USERNAME_LENGTH >= 2
        assert SecurityConfig.MAX_USERNAME_LENGTH > SecurityConfig.MIN_USERNAME_LENGTH

    def test_valid_user_types(self):
        """Testa que tipos de usuário válidos estão definidos"""
        assert "administrador" in SecurityConfig.VALID_USER_TYPES
        assert "vendedor" in SecurityConfig.VALID_USER_TYPES
        assert "repositor" in SecurityConfig.VALID_USER_TYPES
        assert "tecnico" in SecurityConfig.VALID_USER_TYPES


class TestDatabaseConfig:
    """Testes para DatabaseConfig"""

    def test_db_name_defined(self):
        """Testa que nome do banco está definido"""
        assert DatabaseConfig.DB_NAME is not None
        assert len(DatabaseConfig.DB_NAME) > 0

    def test_db_timeout_positive(self):
        """Testa que timeout é positivo"""
        assert DatabaseConfig.DB_TIMEOUT > 0

    def test_cache_size_positive(self):
        """Testa que cache size é positivo"""
        assert DatabaseConfig.CACHE_SIZE > 0


class TestUIConfig:
    """Testes para UIConfig"""

    def test_window_dimensions_positive(self):
        """Testa que dimensões da janela são positivas"""
        assert UIConfig.WINDOW_WIDTH > 0
        assert UIConfig.WINDOW_HEIGHT > 0
        assert UIConfig.WINDOW_MIN_WIDTH > 0
        assert UIConfig.WINDOW_MIN_HEIGHT > 0

    def test_font_sizes_positive(self):
        """Testa que tamanhos de fonte são positivos"""
        assert UIConfig.FONT_SIZE > 0
        assert UIConfig.FONT_SIZE_SMALL > 0
        assert UIConfig.FONT_SIZE_LARGE > 0

    def test_login_layout_defined(self):
        """Testa que layout de login está definido"""
        assert UIConfig.LOGIN_FRAME_X >= 0
        assert UIConfig.LOGIN_FRAME_Y >= 0
        assert UIConfig.LOGIN_KEYBOARD_X >= 0
        assert UIConfig.LOGIN_KEYBOARD_Y >= 0

    def test_colors_defined(self):
        """Testa que cores estão definidas"""
        assert UIConfig.PRIMARY_BG_COLOR is not None
        assert UIConfig.SUCCESS_COLOR is not None
        assert UIConfig.ERROR_COLOR is not None
        assert UIConfig.WARNING_COLOR is not None


class TestLoggingConfig:
    """Testes para LoggingConfig"""

    def test_log_level_valid(self):
        """Testa que nível de log é válido"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert LoggingConfig.LOG_LEVEL in valid_levels

    def test_log_format_defined(self):
        """Testa que formato de log está definido"""
        assert LoggingConfig.LOG_FORMAT is not None
        assert len(LoggingConfig.LOG_FORMAT) > 0

    def test_log_file_max_size_positive(self):
        """Testa que tamanho máximo de arquivo é positivo"""
        assert LoggingConfig.LOG_FILE_MAX_SIZE > 0


class TestAppConfig:
    """Testes para AppConfig"""

    def test_app_name_defined(self):
        """Testa que nome da aplicação está definido"""
        assert AppConfig.APP_NAME is not None
        assert len(AppConfig.APP_NAME) > 0

    def test_app_version_format(self):
        """Testa que versão tem formato válido"""
        version = AppConfig.APP_VERSION
        assert version is not None
        # Versão deve ter pelo menos um ponto (ex: 1.0)
        assert "." in version or version.isdigit()

    def test_directories_defined(self):
        """Testa que diretórios estão definidos"""
        assert AppConfig.DATA_DIR is not None
        assert AppConfig.LOGS_DIR is not None
        assert AppConfig.BACKUP_DIR is not None


class TestConfig:
    """Testes para classe Config agregadora"""

    def test_config_aggregates_all(self):
        """Testa que Config agrega todas as configurações"""
        assert Config.Security is SecurityConfig
        assert Config.Database is DatabaseConfig
        assert Config.UI is UIConfig
        assert Config.Logging is LoggingConfig
        assert Config.App is AppConfig

    def test_get_all_configs(self):
        """Testa obtenção de todas as configurações"""
        all_configs = Config.get_all_configs()

        assert isinstance(all_configs, dict)
        assert "security" in all_configs
        assert "database" in all_configs
        assert "ui" in all_configs
        assert "logging" in all_configs
        assert "app" in all_configs

    def test_validate_configs_success(self):
        """Testa validação de configurações"""
        result = Config.validate_configs()
        assert result is True


class TestValidateConfig:
    """Testes para função validate_config"""

    def test_validate_config_success(self):
        """Testa que validate_config retorna True para configs válidas"""
        result = validate_config()
        assert result is True


class TestEnvironmentConfig:
    """Testes para EnvironmentConfig"""

    def test_is_development_returns_bool(self):
        """Testa que is_development retorna booleano"""
        result = EnvironmentConfig.is_development()
        assert isinstance(result, bool)

    def test_is_production_returns_bool(self):
        """Testa que is_production retorna booleano"""
        result = EnvironmentConfig.is_production()
        assert isinstance(result, bool)

    def test_is_development_and_production_exclusive(self):
        """Testa que development e production são mutuamente exclusivos"""
        is_dev = EnvironmentConfig.is_development()
        is_prod = EnvironmentConfig.is_production()
        assert is_dev != is_prod

    def test_get_config_returns_dict(self):
        """Testa que get_config retorna dicionário"""
        config = EnvironmentConfig.get_config()

        assert isinstance(config, dict)
        assert "log_level" in config
        assert "detailed_logging" in config
        assert "session_timeout" in config


class TestConfigAdditional:
    """Testes adicionais para configurações"""

    def test_security_name_length_constraints(self):
        """Testa constraints de tamanho de nome"""
        assert SecurityConfig.MIN_NAME_LENGTH >= 2
        assert SecurityConfig.MAX_NAME_LENGTH > SecurityConfig.MIN_NAME_LENGTH

    def test_security_audit_settings(self):
        """Testa configurações de auditoria"""
        assert isinstance(SecurityConfig.ENABLE_DETAILED_LOGGING, bool)
        assert isinstance(SecurityConfig.LOG_IP_ADDRESSES, bool)
        assert isinstance(SecurityConfig.LOG_SYSTEM_INFO, bool)

    def test_security_backup_settings(self):
        """Testa configurações de backup"""
        assert isinstance(SecurityConfig.BACKUP_ENABLED, bool)
        assert SecurityConfig.BACKUP_RETENTION_DAYS > 0

    def test_database_wal_mode(self):
        """Testa configuração WAL mode"""
        assert isinstance(DatabaseConfig.ENABLE_WAL_MODE, bool)

    def test_database_foreign_keys(self):
        """Testa configuração foreign keys"""
        assert isinstance(DatabaseConfig.ENABLE_FOREIGN_KEYS, bool)

    def test_database_auto_backup(self):
        """Testa configuração de auto backup"""
        assert isinstance(DatabaseConfig.AUTO_BACKUP, bool)
        assert DatabaseConfig.BACKUP_INTERVAL_HOURS > 0

    def test_ui_theme_settings(self):
        """Testa configurações de tema"""
        assert UIConfig.THEME_MODE in ["light", "dark"]
        assert UIConfig.THEME_COLOR is not None

    def test_ui_font_family(self):
        """Testa configuração de fonte"""
        assert UIConfig.FONT_FAMILY is not None
        assert len(UIConfig.FONT_FAMILY) > 0

    def test_ui_sidebar_width(self):
        """Testa largura do sidebar"""
        assert UIConfig.SIDEBAR_WIDTH > 0

    def test_ui_content_padding(self):
        """Testa padding de conteúdo"""
        assert UIConfig.CONTENT_PADDING >= 0

    def test_ui_login_colors(self):
        """Testa cores de login"""
        assert UIConfig.LOGIN_FRAME_COLOR is not None
        assert UIConfig.LOGIN_FRAME_COLOR.startswith("#")

    def test_ui_login_entry_dimensions(self):
        """Testa dimensões de entrada de login"""
        assert UIConfig.LOGIN_ENTRY_WIDTH > 0
        assert UIConfig.LOGIN_ENTRY_HEIGHT > 0

    def test_ui_status_colors(self):
        """Testa cores de status"""
        assert UIConfig.SUCCESS_BG is not None
        assert UIConfig.SUCCESS_TEXT is not None
        assert UIConfig.WARNING_BG is not None
        assert UIConfig.WARNING_TEXT is not None
        assert UIConfig.ERROR_BG is not None
        assert UIConfig.ERROR_TEXT is not None

    def test_ui_text_colors(self):
        """Testa cores de texto"""
        assert UIConfig.TEXT_PRIMARY is not None
        assert UIConfig.TEXT_SECONDARY is not None
        assert UIConfig.TEXT_LIGHT is not None

    def test_ui_border_colors(self):
        """Testa cores de borda"""
        assert UIConfig.BORDER_COLOR is not None
        assert UIConfig.BORDER_LIGHT is not None

    def test_ui_toast_settings(self):
        """Testa configurações de toast"""
        assert UIConfig.TOAST_START_X > 0
        assert UIConfig.TOAST_END_X > 0
        assert UIConfig.TOAST_Y >= 0
        assert UIConfig.TOAST_ANIMATION_STEP > 0
        assert UIConfig.TOAST_ANIMATION_INTERVAL > 0
        assert UIConfig.TOAST_DEFAULT_DURATION > 0

    def test_ui_transition_color(self):
        """Testa cor de transição"""
        assert UIConfig.TRANSITION_OVERLAY_COLOR is not None

    def test_logging_console_level(self):
        """Testa nível de log de console"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert LoggingConfig.CONSOLE_LOG_LEVEL in valid_levels

    def test_logging_rotation(self):
        """Testa configuração de rotação de logs"""
        assert isinstance(LoggingConfig.LOG_ROTATION, bool)

    def test_logging_colors(self):
        """Testa configuração de cores de console"""
        assert isinstance(LoggingConfig.ENABLE_CONSOLE_COLORS, bool)

    def test_logging_backup_count(self):
        """Testa contagem de backup de logs"""
        assert LoggingConfig.LOG_FILE_BACKUP_COUNT > 0

    def test_app_debug_mode(self):
        """Testa modo debug"""
        assert isinstance(AppConfig.ENABLE_DEBUG_MODE, bool)

    def test_app_update_check(self):
        """Testa verificação de updates"""
        assert isinstance(AppConfig.CHECK_FOR_UPDATES, bool)

    def test_app_caching(self):
        """Testa configuração de cache"""
        assert isinstance(AppConfig.ENABLE_CACHING, bool)
        assert AppConfig.CACHE_TTL_SECONDS > 0

    def test_app_migrations_dir(self):
        """Testa diretório de migrações"""
        assert AppConfig.MIGRATIONS_DIR is not None
