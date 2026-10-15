import logging
from datetime import datetime
from pathlib import Path

import pytest

from ozempic_seguro.domain.users import Role
from ozempic_seguro.infrastructure.logs import configure_logging
from ozempic_seguro.infrastructure.persistence.seed import ensure_default_users
from ozempic_seguro.infrastructure.settings import ConfigurationError, Settings, read_env_file
from ozempic_seguro.infrastructure.system import SystemClock


class TestSettings:
    def test_defaults_without_environment(self):
        settings = Settings.from_env({}, env_file=None)

        assert settings == Settings()
        assert settings.admin_password is None
        assert not settings.development

    def test_reads_every_variable(self):
        settings = Settings.from_env(
            {
                "OZEMPIC_ENV": "development",
                "OZEMPIC_DB_PATH": "/tmp/x.db",
                "OZEMPIC_BCRYPT_ROUNDS": "13",
                "OZEMPIC_SESSION_TIMEOUT": "15",
                "OZEMPIC_MAX_LOGIN_ATTEMPTS": "4",
                "OZEMPIC_LOCKOUT_DURATION": "7",
                "OZEMPIC_DRAWER_LOCK_MINUTES": "2",
                "OZEMPIC_ADMIN_USERNAME": "90",
                "OZEMPIC_ADMIN_PASSWORD": "1111",
                "OZEMPIC_TECNICO_USERNAME": "91",
                "OZEMPIC_TECNICO_PASSWORD": "2222",
            },
            env_file=None,
        )

        assert settings.development
        assert settings.database_path == Path("/tmp/x.db")
        assert (settings.bcrypt_rounds, settings.session_timeout_minutes) == (13, 15)
        assert (settings.max_login_attempts, settings.lockout_minutes) == (4, 7)
        assert settings.drawer_lock_minutes == 2
        assert (settings.admin_username, settings.admin_password) == ("90", "1111")
        assert (settings.technician_username, settings.technician_password) == ("91", "2222")

    def test_environment_overrides_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# comment\n\nOZEMPIC_ADMIN_USERNAME='77'\nOZEMPIC_SESSION_TIMEOUT=20\nINVALID LINE\n",
            encoding="utf-8",
        )

        settings = Settings.from_env({"OZEMPIC_SESSION_TIMEOUT": "30"}, env_file=env_file)

        assert settings.admin_username == "77"
        assert settings.session_timeout_minutes == 30

    def test_inline_comments_are_ignored(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OZEMPIC_SESSION_TIMEOUT=15        # minutos\nOZEMPIC_ADMIN_PASSWORD=12#34\n",
            encoding="utf-8",
        )

        values = read_env_file(env_file)

        assert values["OZEMPIC_SESSION_TIMEOUT"] == "15"
        assert values["OZEMPIC_ADMIN_PASSWORD"] == "12#34"

    def test_example_file_is_valid_with_every_option_enabled(self, tmp_path):
        example = Path(__file__).parents[2] / ".env.example"
        enabled = tmp_path / ".env"
        enabled.write_text(
            example.read_text(encoding="utf-8").replace("# OZEMPIC_", "OZEMPIC_"),
            encoding="utf-8",
        )

        settings = Settings.from_env({}, env_file=enabled)

        assert settings.session_timeout_minutes == 10
        assert settings.drawer_lock_minutes == 5

    def test_missing_env_file_is_ignored(self, tmp_path):
        assert read_env_file(tmp_path / "missing.env") == {}

    def test_rejects_non_numeric_values(self):
        with pytest.raises(ConfigurationError, match="OZEMPIC_SESSION_TIMEOUT"):
            Settings.from_env({"OZEMPIC_SESSION_TIMEOUT": "ten"}, env_file=None)

    @pytest.mark.parametrize(
        "overrides", [{"bcrypt_rounds": 4}, {"lockout_minutes": 0}, {"max_login_attempts": -1}]
    )
    def test_rejects_invalid_values(self, overrides):
        with pytest.raises(ConfigurationError):
            Settings(**overrides)


class TestSeed:
    def test_creates_default_accounts_once(self, users, hasher):
        settings = Settings(admin_password="1111", technician_password="2222")

        created = ensure_default_users(users, hasher, settings)
        again = ensure_default_users(users, hasher, settings)

        assert [(u.username, u.role) for u in created] == [
            ("00", Role.ADMIN),
            ("01", Role.TECHNICIAN),
        ]
        assert again == []
        assert hasher.verify("1111", users.get_password_hash(created[0].id))

    def test_uses_fallback_password_with_a_warning(self, users, hasher, caplog, monkeypatch):
        # Other code may disable propagation on the package logger; caplog needs it.
        monkeypatch.setattr(logging.getLogger("ozempic_seguro"), "propagate", True)
        caplog.set_level(logging.WARNING, logger="ozempic_seguro.infrastructure.persistence.seed")

        created = ensure_default_users(users, hasher, Settings())

        assert hasher.verify("admin@2025", users.get_password_hash(created[0].id))
        assert "No password configured" in caplog.text


class TestSystemAdapters:
    def test_clock_returns_current_time(self):
        before = datetime.now()
        assert before <= SystemClock().now() <= datetime.now()

    def test_hasher_round_trip(self, hasher):
        password_hash = hasher.hash("1234")

        assert password_hash.startswith("$2b$")
        assert hasher.verify("1234", password_hash)
        assert not hasher.verify("4321", password_hash)

    def test_hasher_rejects_malformed_hash(self, hasher):
        assert hasher.verify("1234", "not-a-bcrypt-hash") is False


class TestLogging:
    def test_writes_to_a_rotating_file_once(self, tmp_path):
        logger = configure_logging(tmp_path / "logs", name="ozempic_seguro_test")
        same = configure_logging(tmp_path / "other", name="ozempic_seguro_test")

        logger.info("hello")
        for handler in logger.handlers:
            handler.flush()

        assert same is logger
        assert len(logger.handlers) == 2
        assert "hello" in (tmp_path / "logs" / "app.log").read_text(encoding="utf-8")
        for handler in logger.handlers:
            handler.close()
