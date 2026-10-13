"""Application log files (diagnostics only; the audit trail lives in the database)."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "ozempic_seguro"
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging(
    logs_dir: Path, development: bool = False, name: str = LOGGER_NAME
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logs_dir.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.DEBUG if development else logging.INFO)

    file_handler = RotatingFileHandler(
        logs_dir / "app.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if development else logging.WARNING)
    console.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(console)

    return logger
