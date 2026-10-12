"""
Módulo de repositórios - Camada de persistência de dados.

Fornece acesso ao banco de dados através de repositórios especializados.
"""

from .audit_repository import AuditRepository
from .connection import DatabaseConnection
from .gaveta_repository import GavetaRepository
from .security import hash_password, verify_password
from .user_repository import UserRepository

__all__ = [
    "AuditRepository",
    # Conexão
    "DatabaseConnection",
    "GavetaRepository",
    # Repositórios
    "UserRepository",
    # Segurança
    "hash_password",
    "verify_password",
]
