"""
Serviço de registro de usuário - Lógica de cadastro separada das views.

Responsabilidades:
- Validar dados de cadastro
- Criar usuário
- Retornar resultado estruturado
"""

from dataclasses import dataclass, field

from ..core.exceptions import (
    InvalidUserDataError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from ..core.logger import logger
from .user_service import UserService


@dataclass
class RegistrationResult:
    """Resultado de uma tentativa de registro"""

    success: bool
    message: str = ""
    errors: list[str] = field(default_factory=list)
    user_id: int | None = None


class UserRegistrationService:
    """
    Serviço de registro de usuário.

    Encapsula toda a lógica de cadastro que estava na CadastroUsuarioView.
    """

    # Constantes de validação
    MAX_NAME_LENGTH = 26
    MAX_USERNAME_LENGTH = 8
    MAX_PASSWORD_LENGTH = 8
    MIN_PASSWORD_LENGTH = 4

    def __init__(self):
        self._user_service = UserService()

    def register(
        self, name: str, username: str, password: str, user_type: str
    ) -> RegistrationResult:
        """
        Registra um novo usuário.

        Args:
            name: Full name of the user
            username: Username (numbers only)
            password: Password (numbers only)
            user_type: User type (vendedor, repositor, administrador, tecnico)

        Returns:
            RegistrationResult com o resultado do registro
        """
        # Validar dados
        validation_errors = self._validate_registration_data(name, username, password, user_type)

        if validation_errors:
            logger.warning(f"Registration validation failed: {validation_errors}")
            return RegistrationResult(
                success=False, message="Dados inválidos", errors=validation_errors
            )

        # Tentar criar usuário
        try:
            success, message = self._user_service.create_user(
                name=name, username=username, password=password, user_type=user_type
            )

            if success:
                logger.info(f"User registered successfully: {username}")
                return RegistrationResult(
                    success=True, message=f"Usuário '{name}' cadastrado com sucesso!"
                )
            logger.warning(f"User registration failed: {message}")
            return RegistrationResult(success=False, message=message, errors=[message])

        except UserAlreadyExistsError:
            logger.warning(f"User already exists: {username}")
            return RegistrationResult(
                success=False,
                message="Usuário já existe",
                errors=["Este nome de usuário já está em uso"],
            )
        except (InvalidUserDataError, WeakPasswordError) as e:
            logger.warning(f"Invalid user data: {e}")
            return RegistrationResult(success=False, message=str(e), errors=[str(e)])
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            return RegistrationResult(
                success=False, message="Erro inesperado ao cadastrar usuário", errors=[str(e)]
            )

    def _validate_registration_data(
        self, name: str, username: str, password: str, user_type: str
    ) -> list[str]:
        """
        Valida dados de registro.

        Returns:
            Lista de erros de validação (vazia se válido)
        """
        errors = []

        # Validar campos obrigatórios
        if not name or not name.strip():
            errors.append("Nome é obrigatório")

        if not username or not username.strip():
            errors.append("Usuário é obrigatório")

        if not password:
            errors.append("Senha é obrigatória")

        if errors:
            return errors

        # Validar tamanho do nome
        if len(name) > self.MAX_NAME_LENGTH:
            errors.append(f"O nome deve ter no máximo {self.MAX_NAME_LENGTH} caracteres")

        # Validar tamanho do usuário
        if len(username) > self.MAX_USERNAME_LENGTH:
            errors.append(f"O usuário deve ter no máximo {self.MAX_USERNAME_LENGTH} dígitos")

        # Validar que usuário é numérico
        if not username.isdigit():
            errors.append("O usuário deve conter apenas números")

        # Validar tamanho da senha
        if len(password) > self.MAX_PASSWORD_LENGTH:
            errors.append(f"A senha deve ter no máximo {self.MAX_PASSWORD_LENGTH} dígitos")

        if len(password) < self.MIN_PASSWORD_LENGTH:
            errors.append(f"A senha deve ter no mínimo {self.MIN_PASSWORD_LENGTH} caracteres")

        # Validar que senha é numérica
        if not password.isdigit():
            errors.append("A senha deve conter apenas números")

        # Validar tipo de usuário
        valid_types = ["vendedor", "repositor", "administrador", "tecnico"]
        if user_type not in valid_types:
            errors.append(f"Tipo de usuário inválido. Deve ser: {', '.join(valid_types)}")

        return errors

    def validate_name(self, name: str) -> bool:
        """Valida se o nome é válido"""
        return len(name) <= self.MAX_NAME_LENGTH

    def validate_username(self, username: str) -> bool:
        """Valida se o username é válido"""
        return len(username) <= self.MAX_USERNAME_LENGTH and username.isdigit()

    def validate_password(self, password: str) -> bool:
        """Valida se a senha é válida"""
        return (
            self.MIN_PASSWORD_LENGTH <= len(password) <= self.MAX_PASSWORD_LENGTH
            and password.isdigit()
        )


def get_user_registration_service() -> UserRegistrationService:
    """Retorna instância do UserRegistrationService"""
    return UserRegistrationService()
