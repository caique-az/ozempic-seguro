"""Runtime configuration read from environment variables and an optional .env file."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ..paths import DATA_DIR, LOGS_DIR, PROJECT_ROOT

DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"

# Used only when no password is configured, so a fresh checkout can still log in.
# The application logs a warning whenever it seeds a user with one of these.
FALLBACK_ADMIN_PASSWORD = "admin@2025"
FALLBACK_TECHNICIAN_PASSWORD = "tecnico@2025"


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path = DATA_DIR / "ozempic_seguro.db"
    logs_dir: Path = LOGS_DIR
    development: bool = False
    bcrypt_rounds: int = 12
    session_timeout_minutes: int = 10
    max_login_attempts: int = 3
    lockout_minutes: int = 5
    drawer_lock_minutes: int = 5
    admin_username: str = "00"
    admin_password: str | None = None
    technician_username: str = "01"
    technician_password: str | None = None

    def __post_init__(self) -> None:
        if not 10 <= self.bcrypt_rounds <= 16:
            raise ConfigurationError("OZEMPIC_BCRYPT_ROUNDS deve estar entre 10 e 16")
        for name in (
            "session_timeout_minutes",
            "max_login_attempts",
            "lockout_minutes",
            "drawer_lock_minutes",
        ):
            if getattr(self, name) <= 0:
                raise ConfigurationError(f"{name} deve ser maior que zero")

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        env_file: Path | None = DEFAULT_ENV_FILE,
    ) -> "Settings":
        """Build settings from the environment; values in `environ` win over the .env file."""
        values = dict(read_env_file(env_file)) if env_file else {}
        values.update(os.environ if environ is None else environ)

        def text(key: str) -> str | None:
            value = values.get(key, "").strip()
            return value or None

        def number(key: str, default: int) -> int:
            raw = text(key)
            if raw is None:
                return default
            try:
                return int(raw)
            except ValueError as e:
                raise ConfigurationError(f"{key} deve ser um número inteiro: {raw!r}") from e

        defaults = cls()
        database = text("OZEMPIC_DB_PATH")
        return cls(
            database_path=Path(database) if database else defaults.database_path,
            development=(text("OZEMPIC_ENV") or "production").lower() == "development",
            bcrypt_rounds=number("OZEMPIC_BCRYPT_ROUNDS", defaults.bcrypt_rounds),
            session_timeout_minutes=number(
                "OZEMPIC_SESSION_TIMEOUT", defaults.session_timeout_minutes
            ),
            max_login_attempts=number("OZEMPIC_MAX_LOGIN_ATTEMPTS", defaults.max_login_attempts),
            lockout_minutes=number("OZEMPIC_LOCKOUT_DURATION", defaults.lockout_minutes),
            drawer_lock_minutes=number("OZEMPIC_DRAWER_LOCK_MINUTES", defaults.drawer_lock_minutes),
            admin_username=text("OZEMPIC_ADMIN_USERNAME") or defaults.admin_username,
            admin_password=text("OZEMPIC_ADMIN_PASSWORD"),
            technician_username=text("OZEMPIC_TECNICO_USERNAME") or defaults.technician_username,
            technician_password=text("OZEMPIC_TECNICO_PASSWORD"),
        )


def read_env_file(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE lines, ignoring blanks, comments and surrounding quotes."""
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'\"")
    return values
