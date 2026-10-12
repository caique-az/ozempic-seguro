"""
Serviço de gerenciamento de usuários - Lógica de gerenciamento separada das views.

Responsabilidades:
- Listar usuários
- Alterar senha
- Excluir usuário
- Verificar permissões
"""

from dataclasses import dataclass, field

from ..core.exceptions import (
    LastAdminError,
    UserNotFoundError,
    WeakPasswordError,
)
from ..core.logger import logger
from .user_service import UserService


@dataclass
class UserData:
    """Dados de um usuário"""

    id: int
    username: str
    full_name: str
    user_type: str
    active: bool
    created_at: str

    @property
    def is_technician(self) -> bool:
        """Verifica se é usuário técnico"""
        return self.user_type.lower() == "tecnico"

    @property
    def is_admin(self) -> bool:
        """Verifica se é administrador"""
        return self.user_type.lower() == "administrador"

    @property
    def can_be_modified(self) -> bool:
        """Verifica se pode ser modificado"""
        return not self.is_technician

    @property
    def can_be_deleted(self) -> bool:
        """Verifica se pode ser excluído"""
        return not self.is_technician

    @property
    def user_type_display(self) -> str:
        """Retorna tipo formatado para exibição"""
        return self.user_type.capitalize()

    @property
    def status_display(self) -> str:
        """Retorna status formatado para exibição"""
        return "Ativo" if self.active else "Inativo"

    @property
    def created_at_display(self) -> str:
        """Retorna data formatada para exibição"""
        try:
            if self.created_at and isinstance(self.created_at, str):
                return self.created_at.split(" ")[0] if " " in self.created_at else self.created_at
            return "N/A"
        except (ValueError, AttributeError, IndexError):
            return "N/A"


@dataclass
class OperationResult:
    """Resultado de uma operação"""

    success: bool
    message: str = ""
    errors: list[str] = field(default_factory=list)


class UserManagementService:
    """
    Serviço de gerenciamento de usuários.

    Encapsula toda a lógica de gerenciamento que estava na GerenciamentoUsuariosView.
    """

    def __init__(self):
        self._user_service = UserService()

    def get_all_users(self) -> list[UserData]:
        """
        Obtém todos os usuários.

        Returns:
            Lista de UserData
        """
        try:
            usuarios = self._user_service.get_all_users()
            return [
                UserData(
                    id=u[0],
                    username=u[1],
                    full_name=u[2],
                    user_type=u[3],
                    active=u[4],
                    created_at=u[5],
                )
                for u in usuarios
            ]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def get_user_by_id(self, user_id: int) -> UserData | None:
        """
        Obtém usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            UserData ou None
        """
        users = self.get_all_users()
        return next((u for u in users if u.id == user_id), None)

    def change_password(
        self, user_id: int, new_password: str, confirm_password: str
    ) -> OperationResult:
        """
        Altera senha de um usuário.

        Args:
            user_id: ID do usuário
            new_password: Nova senha
            confirm_password: Confirmação da senha

        Returns:
            OperationResult com o resultado
        """
        # Validar campos
        if not new_password:
            return OperationResult(
                success=False,
                message="Por favor, digite uma nova senha",
                errors=["Senha não pode ser vazia"],
            )

        if new_password != confirm_password:
            return OperationResult(
                success=False,
                message="As senhas não coincidem",
                errors=["Senha e confirmação devem ser iguais"],
            )

        # Verificar se usuário pode ser modificado
        user = self.get_user_by_id(user_id)
        if user and not user.can_be_modified:
            return OperationResult(
                success=False,
                message="Usuários técnicos não podem ser modificados",
                errors=["Operação não permitida para usuários técnicos"],
            )

        # Tentar alterar senha
        try:
            success, message = self._user_service.update_password(user_id, new_password)

            if success:
                logger.info(f"Password changed for user ID: {user_id}")
                return OperationResult(success=True, message=message)
            return OperationResult(success=False, message=message, errors=[message])

        except WeakPasswordError as e:
            return OperationResult(success=False, message="Senha muito fraca", errors=[str(e)])
        except UserNotFoundError:
            return OperationResult(
                success=False,
                message="Usuário não encontrado",
                errors=["O usuário não existe mais"],
            )
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return OperationResult(
                success=False, message=f"Erro ao alterar senha: {e!s}", errors=[str(e)]
            )

    def delete_user(self, user_id: int, current_user_id: int | None = None) -> OperationResult:
        """
        Exclui um usuário.

        Args:
            user_id: ID do usuário a excluir
            current_user_id: ID do usuário logado (para evitar auto-exclusão)

        Returns:
            OperationResult com o resultado
        """
        # Verificar se está tentando excluir a si mesmo
        if current_user_id and user_id == current_user_id:
            return OperationResult(
                success=False,
                message="Você não pode excluir sua própria conta",
                errors=["Auto-exclusão não permitida"],
            )

        # Verificar se usuário pode ser excluído
        user = self.get_user_by_id(user_id)
        if not user:
            return OperationResult(
                success=False,
                message="Usuário não encontrado",
                errors=["O usuário não existe mais"],
            )

        if not user.can_be_deleted:
            return OperationResult(
                success=False,
                message="Usuários técnicos não podem ser excluídos",
                errors=["Operação não permitida para usuários técnicos"],
            )

        # Tentar excluir
        try:
            success, message = self._user_service.delete_user(user_id)

            if success:
                logger.info(f"User deleted: {user.username} (ID: {user_id})")
                return OperationResult(success=True, message=message)
            return OperationResult(success=False, message=message, errors=[message])

        except LastAdminError:
            return OperationResult(
                success=False,
                message="Não é possível excluir o último administrador",
                errors=["O sistema precisa de pelo menos um administrador"],
            )
        except UserNotFoundError:
            return OperationResult(
                success=False,
                message="Usuário não encontrado",
                errors=["O usuário não existe mais"],
            )
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return OperationResult(
                success=False, message=f"Erro ao excluir usuário: {e!s}", errors=[str(e)]
            )

    def can_modify_user(self, user_id: int) -> tuple[bool, str]:
        """
        Verifica se um usuário pode ser modificado.

        Args:
            user_id: ID do usuário

        Returns:
            Tuple (pode_modificar, motivo)
        """
        user = self.get_user_by_id(user_id)

        if not user:
            return False, "Usuário não encontrado"

        if not user.can_be_modified:
            return False, "Usuários técnicos não podem ser modificados"

        return True, ""

    def can_delete_user(self, user_id: int, current_user_id: int | None = None) -> tuple[bool, str]:
        """
        Verifica se um usuário pode ser excluído.

        Args:
            user_id: ID do usuário
            current_user_id: ID do usuário logado

        Returns:
            Tuple (pode_excluir, motivo)
        """
        if current_user_id and user_id == current_user_id:
            return False, "Você não pode excluir sua própria conta"

        user = self.get_user_by_id(user_id)

        if not user:
            return False, "Usuário não encontrado"

        if not user.can_be_deleted:
            return False, "Usuários técnicos não podem ser excluídos"

        return True, ""


def get_user_management_service() -> UserManagementService:
    """Retorna instância do UserManagementService"""
    return UserManagementService()
