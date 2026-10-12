#!/usr/bin/env python
"""
Database maintenance commands.

Usage:
    python scripts/manage_db.py reset                 # drop and recreate the database
    python scripts/manage_db.py reset-admin-password  # reapply OZEMPIC_ADMIN_PASSWORD

Default users are created from the OZEMPIC_* environment variables (see .env.example).
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ozempic_seguro.config import Config
from ozempic_seguro.paths import DATA_DIR
from ozempic_seguro.repositories.user_repository import UserRepository


def reset_database() -> None:
    db_path = DATA_DIR / Config.Database.DB_NAME
    for suffix in ("", "-wal", "-shm"):
        Path(f"{db_path}{suffix}").unlink(missing_ok=True)

    # Opening the connection runs the migrations; the repository seeds the default users.
    UserRepository()
    print(f"Database recreated at {db_path}")


def reset_admin_password() -> None:
    username = os.getenv("OZEMPIC_ADMIN_USERNAME", "00")
    password = os.getenv("OZEMPIC_ADMIN_PASSWORD")
    if not password:
        sys.exit("OZEMPIC_ADMIN_PASSWORD is not set")

    repo = UserRepository()
    user = repo.get_user_by_username(username)
    if user is None:
        sys.exit(f"Admin user '{username}' not found")

    repo.update_password(user["id"], password)
    if repo.authenticate_user(username, password) is None:
        sys.exit("Password updated but login check failed")
    print(f"Password for '{username}' updated")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("command", choices=["reset", "reset-admin-password"])
    args = parser.parse_args()

    if args.command == "reset":
        answer = input("This deletes ALL data. Continue? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted")
            return
        reset_database()
    else:
        reset_admin_password()


if __name__ == "__main__":
    main()
