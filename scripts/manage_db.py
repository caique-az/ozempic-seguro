#!/usr/bin/env python
"""
Database maintenance commands.

Usage:
    python scripts/manage_db.py reset                 # drop and recreate the database
    python scripts/manage_db.py reset-admin-password  # reapply OZEMPIC_ADMIN_PASSWORD

Configuration comes from the OZEMPIC_* variables and .env (see .env.example).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ozempic_seguro.infrastructure.persistence.database import Database
from ozempic_seguro.infrastructure.persistence.seed import ensure_default_users
from ozempic_seguro.infrastructure.persistence.user_repository import SqliteUserRepository
from ozempic_seguro.infrastructure.settings import Settings
from ozempic_seguro.infrastructure.system import BcryptPasswordHasher


def reset_database(settings: Settings) -> None:
    for suffix in ("", "-wal", "-shm"):
        Path(f"{settings.database_path}{suffix}").unlink(missing_ok=True)

    db = Database(settings.database_path)
    hasher = BcryptPasswordHasher(settings.bcrypt_rounds)
    created = ensure_default_users(SqliteUserRepository(db), hasher, settings)
    db.close()
    print(f"Database recreated at {settings.database_path}")
    print("Default users: " + ", ".join(f"{u.username} ({u.role.label})" for u in created))


def reset_admin_password(settings: Settings) -> None:
    if not settings.admin_password:
        sys.exit("OZEMPIC_ADMIN_PASSWORD is not set")

    db = Database(settings.database_path)
    users = SqliteUserRepository(db)
    hasher = BcryptPasswordHasher(settings.bcrypt_rounds)
    admin = users.get_by_username(settings.admin_username)
    if admin is None:
        db.close()
        sys.exit(f"Admin user '{settings.admin_username}' not found")

    users.set_password_hash(admin.id, hasher.hash(settings.admin_password))
    db.close()
    print(f"Password for '{admin.username}' updated")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("command", choices=["reset", "reset-admin-password"])
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "reset":
        answer = input("This deletes ALL data. Continue? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted")
            return
        reset_database(settings)
    else:
        reset_admin_password(settings)


if __name__ == "__main__":
    main()
