"""Default accounts that must exist for the device to be operated at all."""

import logging

from ...domain.ports import PasswordHasher, UserRepository
from ...domain.users import Role, User
from ..settings import FALLBACK_ADMIN_PASSWORD, FALLBACK_TECHNICIAN_PASSWORD, Settings

logger = logging.getLogger(__name__)


def ensure_default_users(
    users: UserRepository, hasher: PasswordHasher, settings: Settings
) -> list[User]:
    """Create the default admin and technician if they do not exist yet."""
    accounts = [
        (
            settings.admin_username,
            settings.admin_password,
            FALLBACK_ADMIN_PASSWORD,
            "ADMINISTRADOR",
            Role.ADMIN,
        ),
        (
            settings.technician_username,
            settings.technician_password,
            FALLBACK_TECHNICIAN_PASSWORD,
            "TÉCNICO",
            Role.TECHNICIAN,
        ),
    ]
    created = []
    for username, password, fallback, full_name, role in accounts:
        if users.get_by_username(username) is not None:
            continue
        if password is None:
            logger.warning(
                "No password configured for default %s '%s'; using the documented fallback. "
                "Set it in .env before using the device in production.",
                role.value,
                username,
            )
        created.append(users.add(username, hasher.hash(password or fallback), full_name, role))
    return created
