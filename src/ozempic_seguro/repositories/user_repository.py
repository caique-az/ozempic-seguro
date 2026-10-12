"""
Repositório de usuários: operações CRUD e autenticação.

Implementa IUserRepository com lógica de persistência para usuários.
"""

import os
import sqlite3
from typing import Any

from ..core.logger import logger
from .connection import DatabaseConnection
from .interfaces import IUserRepository
from .security import hash_password, verify_password


class UserRepository(IUserRepository):
    """
    Repositório para operações de usuários no banco de dados.

    Responsabilidades:
    - CRUD de usuários
    - Autenticação
    - Verificações de regras de negócio (único admin, etc.)
    """

    def __init__(self):
        self._db = DatabaseConnection.get_instance()
        self._ensure_default_users()

    def _ensure_default_users(self) -> None:
        """Garante que usuários padrão existam"""
        if self._db.is_new_database:
            self._create_default_admin()
            self._create_default_tecnico()
        else:
            # Verifica se existem
            self._db.execute(
                "SELECT COUNT(*) FROM usuarios WHERE username = ?",
                (os.getenv("OZEMPIC_ADMIN_USERNAME", "00"),),
            )
            if self._db.fetchone()[0] == 0:
                self._create_default_admin()

            self._db.execute(
                "SELECT COUNT(*) FROM usuarios WHERE username = ?",
                (os.getenv("OZEMPIC_TECNICO_USERNAME", "01"),),
            )
            if self._db.fetchone()[0] == 0:
                self._create_default_tecnico()

    def _create_default_admin(self) -> None:
        """Cria usuário administrador padrão"""
        username = os.getenv("OZEMPIC_ADMIN_USERNAME", "00")
        password = os.getenv("OZEMPIC_ADMIN_PASSWORD", "admin@2025")
        password_hash = hash_password(password)

        try:
            self._db.execute(
                "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo, ativo) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, "ADMINISTRADOR", "administrador", 1),
            )
            self._db.commit()
            logger.info(f"Default admin user created: {username}")
        except sqlite3.IntegrityError:
            self._db.rollback()

    def _create_default_tecnico(self) -> None:
        """Cria usuário técnico padrão"""
        username = os.getenv("OZEMPIC_TECNICO_USERNAME", "01")
        password = os.getenv("OZEMPIC_TECNICO_PASSWORD", "tecnico@2025")
        password_hash = hash_password(password)

        try:
            self._db.execute(
                "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo, ativo) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, "TÉCNICO", "tecnico", 1),
            )
            self._db.commit()
            logger.info(f"Default tecnico user created: {username}")
        except sqlite3.IntegrityError:
            self._db.rollback()

    def create_user(
        self, username: str, password: str, full_name: str, user_type: str
    ) -> int | None:
        """
        Cria um usuário e retorna seu ID.

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: Full name of the user
            user_type: User type (administrador, vendedor, repositor, tecnico)

        Returns:
            ID do usuário criado ou None se falhar
        """
        password_hash = hash_password(password)
        try:
            self._db.execute(
                "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo) VALUES (?, ?, ?, ?)",
                (username, password_hash, full_name, user_type),
            )
            self._db.commit()
            return self._db.lastrowid()
        except sqlite3.IntegrityError:
            logger.warning(f"Username already exists: {username}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Database error creating user: {e}")
            self._db.rollback()
            return None

    def authenticate_user(self, username: str, password: str) -> dict[str, Any] | None:
        """
        Autentica usuário e retorna dados se bem-sucedido.

        Args:
            username: Nome de usuário
            password: Senha em texto plano

        Returns:
            Dicionário com dados do usuário ou None se falhar
        """
        self._db.execute(
            "SELECT id, username, senha_hash, nome_completo, tipo FROM usuarios WHERE username = ? AND ativo = 1",
            (username,),
        )
        row = self._db.fetchone()

        if row and verify_password(password, row[2]):
            return {"id": row[0], "username": row[1], "nome_completo": row[3], "tipo": row[4]}
        return None

    def delete_user(self, user_id: int) -> bool:
        """
        Exclui usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            True se excluído com sucesso
        """
        # Verifica se existe
        self._db.execute("SELECT id FROM usuarios WHERE id = ?", (user_id,))
        if not self._db.fetchone():
            return False

        # Verifica se é único admin
        if self.is_unique_admin(user_id):
            logger.warning(f"Cannot delete last admin: {user_id}")
            return False

        self._db.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        self._db.commit()
        return self._db.cursor.rowcount > 0

    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Atualiza senha do usuário.

        Args:
            user_id: ID do usuário
            new_password: Nova senha em texto plano

        Returns:
            True se atualizado com sucesso
        """
        password_hash = hash_password(new_password)
        self._db.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?", (password_hash, user_id)
        )
        self._db.commit()
        return self._db.cursor.rowcount > 0

    def is_unique_admin(self, user_id: int) -> bool:
        """
        Verifica se é o único administrador restante.

        Args:
            user_id: ID do usuário a verificar

        Returns:
            True se for o único admin
        """
        # Verifica se é admin
        self._db.execute("SELECT tipo FROM usuarios WHERE id = ?", (user_id,))
        row = self._db.fetchone()

        if not row or row[0] != "administrador":
            return False

        # Conta admins
        self._db.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'administrador'")
        total = self._db.fetchone()[0]

        return total <= 1

    def get_users(self) -> list[tuple]:
        """
        Obtém lista de todos os usuários.

        Returns:
            Lista de tuplas com dados dos usuários
        """
        self._db.execute(
            """
            SELECT id, username, nome_completo, tipo, ativo, data_criacao
            FROM usuarios
            ORDER BY data_criacao DESC
        """
        )
        return self._db.fetchall()

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """
        Obtém um usuário específico pelo ID.

        Args:
            user_id: ID do usuário

        Returns:
            Dicionário com dados do usuário ou None
        """
        self._db.execute(
            "SELECT id, username, nome_completo, tipo, ativo FROM usuarios WHERE id = ?", (user_id,)
        )
        row = self._db.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "nome_completo": row[2],
                "tipo": row[3],
                "ativo": row[4],
            }
        return None

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """
        Obtém um usuário pelo username.

        Args:
            username: Nome de usuário

        Returns:
            Dicionário com dados do usuário ou None
        """
        self._db.execute(
            "SELECT id, username, nome_completo, tipo, ativo FROM usuarios WHERE username = ?",
            (username,),
        )
        row = self._db.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "nome_completo": row[2],
                "tipo": row[3],
                "ativo": row[4],
            }
        return None

    # Métodos da interface IRepository
    def find_by_id(self, entity_id: int) -> dict[str, Any] | None:
        """Implementação de IRepository.find_by_id"""
        return self.get_user_by_id(entity_id)

    def find_all(self) -> list[dict[str, Any]]:
        """Implementação de IRepository.find_all"""
        users = self.get_users()
        return [
            {
                "id": u[0],
                "username": u[1],
                "nome_completo": u[2],
                "tipo": u[3],
                "ativo": u[4],
                "data_criacao": u[5],
            }
            for u in users
        ]

    def save(self, entity: dict[str, Any]) -> bool:
        """Implementação de IRepository.save"""
        if entity.get("id"):
            # Update
            return (
                self.update_password(entity["id"], entity.get("senha", ""))
                if "senha" in entity
                else True
            )
        # Create
        result = self.create_user(
            entity.get("username", ""),
            entity.get("senha", ""),
            entity.get("nome_completo", ""),
            entity.get("tipo", "vendedor"),
        )
        return result is not None

    def delete(self, entity_id: int) -> bool:
        """Implementação de IRepository.delete"""
        return self.delete_user(entity_id)

    def exists(self, entity_id: int) -> bool:
        """Implementação de IRepository.exists"""
        return self.get_user_by_id(entity_id) is not None

    # Métodos da interface IUserRepository
    def find_by_username(self, username: str) -> dict[str, Any] | None:
        """Implementação de IUserRepository.find_by_username"""
        return self.get_user_by_username(username)

    def find_by_type(self, user_type: str) -> list[dict[str, Any]]:
        """Implementação de IUserRepository.find_by_type"""
        self._db.execute(
            "SELECT id, username, nome_completo, tipo, ativo FROM usuarios WHERE tipo = ?",
            (user_type,),
        )
        return [
            {"id": r[0], "username": r[1], "nome_completo": r[2], "tipo": r[3], "ativo": r[4]}
            for r in self._db.fetchall()
        ]

    def find_active_users(self) -> list[dict[str, Any]]:
        """Implementação de IUserRepository.find_active_users"""
        self._db.execute(
            "SELECT id, username, nome_completo, tipo, ativo FROM usuarios WHERE ativo = 1"
        )
        return [
            {"id": r[0], "username": r[1], "nome_completo": r[2], "tipo": r[3], "ativo": r[4]}
            for r in self._db.fetchall()
        ]

    def update_status(self, user_id: int, active: bool) -> bool:
        """Implementação de IUserRepository.update_status"""
        self._db.execute(
            "UPDATE usuarios SET ativo = ? WHERE id = ?", (1 if active else 0, user_id)
        )
        self._db.commit()
        return self._db.cursor.rowcount > 0
