"""Adapters for the machine the application runs on: clock and password hashing."""

from datetime import datetime

import bcrypt


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()


class BcryptPasswordHasher:
    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self._rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except ValueError:
            # Not a bcrypt hash (corrupted row or legacy format): never authenticate.
            return False
