"""Filesystem locations used by the application."""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent.parent

ASSETS_DIR = PACKAGE_DIR / "assets"
DATA_DIR = PACKAGE_DIR / "data"
MIGRATIONS_DIR = PACKAGE_DIR / "migrations"
LOGS_DIR = PROJECT_ROOT / "logs"
