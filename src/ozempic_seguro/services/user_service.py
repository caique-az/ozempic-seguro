"""
Serviço de usuários: camada de negócio isolada entre controllers e repositories.

Utiliza exceções customizadas para tratamento de erros consistente.
"""

import datetime
from typing import Any

from ..config import SecurityConfig
from ..core.base_views import BaseService
from ..core.exceptions import (
    AccountLockedError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidUserDataError,
    LastAdminError,
    UserAlreadyExistsError,
    UserNotFoundError,
    WeakPasswordError,
)
from ..core.validators import Validators
from ..repositories.audit_repository import AuditRepository
from ..repositories.security_logger import SecurityLogger
from ..repositories.user_repository import UserRepository


class UserService(BaseService):
    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self.audit_repo = AuditRepository()

    def create_user(
        self,
        name: str,
        username: str,
        password: str,
        user_type: str,
        creator_user_id: int | None = None,
    ) -> tuple[bool, str]:
        """
        Cadastra um novo usuário com validações robustas e registra log de auditoria.

        Raises:
            InvalidUserDataError: Se os dados de entrada forem inválidos
            UserAlreadyExistsError: Se o username já existir
        """
        # Validação robusta de entrada usando método da classe base
        validation_data = {"username": username, "senha": password, "nome": name, "tipo": user_type}

        if not self._validate_input(validation_data):
            raise InvalidUserDataError("input", "Dados de entrada inválidos ou incompletos")

        validation_result = Validators.validate_and_sanitize_user_input(
            username=username, password=password, name=name, user_type=user_type
        )

        if not validation_result["valid"]:
            errors = "; ".join(validation_result["errors"])
            raise InvalidUserDataError("validation", errors)

        # Usar dados sanitizados
        sanitized_data = validation_result["sanitized_data"]
        sanitized_name = sanitized_data["name"]
        sanitized_username = sanitized_data["username"]
        sanitized_type = sanitized_data["user_type"]

        try:
            new_id = self.user_repo.create_user(
                sanitized_username, password, sanitized_name, sanitized_type
            )
            if not new_id:
                raise UserAlreadyExistsError(sanitized_username)

            # Log de criação com contexto de segurança
            security_context = SecurityLogger.log_user_management(
                action="CREATE_USER",
                admin_user_id=creator_user_id or new_id,
                admin_username="system",
                target_user_id=new_id,
                target_username=sanitized_username,
                changes={
                    "nome_completo": sanitized_name,
                    "tipo": sanitized_type,
                    "data_criacao": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            self.audit_repo.create_log(
                user_id=creator_user_id or new_id,
                action="CRIAR",
                affected_table="USUARIOS",
                id_afetado=new_id,
                new_data=security_context,
                ip_address=security_context.get("ip_address"),
            )
            return True, "Usuário cadastrado com sucesso!"

        except (InvalidUserDataError, UserAlreadyExistsError):
            raise
        except Exception as e:
            raise InvalidUserDataError("database", f"Erro ao cadastrar usuário: {e!s}") from e

    def _validate_input(self, validation_data: dict) -> bool:
        """Implementação da validação de entrada obrigatória da classe base"""
        required_fields = ["username", "senha", "nome", "tipo"]

        # Verificar campos obrigatórios
        for field in required_fields:
            if not validation_data.get(field):
                return False

        # Validar tipo de usuário
        return validation_data["tipo"] in SecurityConfig.VALID_USER_TYPES

        return True

    def authenticate(
        self, username: str, password: str, ip_address: str | None = None
    ) -> dict[str, Any]:
        """
        Autentica usuário com validação robusta, controle de força bruta e logs detalhados.

        Returns:
            Dict com dados do usuário autenticado

        Raises:
            InvalidCredentialsError: Se credenciais forem inválidas
            AccountLockedError: Se conta estiver bloqueada
        """
        # Validação básica - permite usuário "00" (admin padrão)
        if not username or not password:
            raise InvalidCredentialsError(username)

        # Sanitiza entrada
        username = username.strip()

        # Permite usuário admin padrão "00" sem validação rigorosa
        if username != "00":
            # Validação robusta apenas para outros usuários
            username_result = Validators.validate_username(username)
            password_result = Validators.validate_password(password, strict=False)
            username_valid = username_result.is_valid
            username_error = username_result.errors[0] if username_result.errors else ""
            password_valid = password_result.is_valid
            password_error = password_result.errors[0] if password_result.errors else ""

            if not username_valid:
                # Log tentativa com dados inválidos
                security_context = SecurityLogger.log_security_violation(
                    violation_type="INVALID_USERNAME_FORMAT",
                    details={
                        "username": Validators.sanitize_string(username, 50),
                        "error": username_error,
                    },
                )
                self.audit_repo.create_log(
                    user_id=None,
                    action="SECURITY_VIOLATION",
                    affected_table="USUARIOS",
                    previous_data=security_context,
                    ip_address=security_context.get("ip_address"),
                )
                raise InvalidCredentialsError(username, "Formato de usuário inválido")

            if not password_valid:
                raise InvalidCredentialsError(
                    username, password_error or "Formato de senha inválido"
                )

        # Verificar se usuário está bloqueado por tentativas excessivas
        from ..session.session_manager import SessionManager

        session_manager = SessionManager.get_instance()

        if session_manager.is_user_locked(username):
            remaining_time = session_manager.get_lockout_remaining_time(username)
            security_context = SecurityLogger.log_security_violation(
                violation_type="ACCOUNT_LOCKED",
                username=username,
                details={"remaining_lockout_minutes": remaining_time},
            )
            self.audit_repo.create_log(
                user_id=None,
                action="LOGIN_BLOCKED",
                affected_table="USUARIOS",
                previous_data=security_context,
                ip_address=security_context.get("ip_address"),
            )
            raise AccountLockedError(username, locked_until=f"{remaining_time} minutos")

        user = self.user_repo.authenticate_user(username, password)

        if user:
            # Reset contador de tentativas em caso de sucesso
            session_manager.record_login_attempt(username, success=True)

            # Log de sucesso com contexto de segurança
            security_context = SecurityLogger.log_login_attempt(
                username=username, success=True, user_id=user["id"]
            )

            self.audit_repo.create_log(
                user_id=user["id"],
                action="LOGIN_SUCCESS",
                affected_table="USUARIOS",
                id_afetado=user["id"],
                new_data=security_context,
                ip_address=security_context.get("ip_address"),
            )
            return dict(user)
        # Registra tentativa falhada para controle de força bruta
        session_manager.record_login_attempt(username, success=False)

        # Log de tentativa falha com contexto de segurança
        security_context = SecurityLogger.log_login_attempt(
            username=username, success=False, failure_reason="invalid_credentials"
        )

        self.audit_repo.create_log(
            user_id=None,
            action="LOGIN_FAILED",
            affected_table="USUARIOS",
            previous_data=security_context,
            ip_address=security_context.get("ip_address"),
        )
        raise InvalidCredentialsError(username)

    def logout(self, user_id: int, username: str, ip_address: str | None = None) -> None:
        """Registra logout de usuário com contexto de segurança."""
        security_context = SecurityLogger.log_session_event(
            event_type="LOGOUT", user_id=user_id, username=username
        )

        self.audit_repo.create_log(
            user_id=user_id,
            action="LOGOUT",
            affected_table="USUARIOS",
            id_afetado=user_id,
            new_data=security_context,
            ip_address=security_context.get("ip_address", ip_address),
        )

    def delete_user(self, user_id: int) -> tuple[bool, str]:
        """
        Exclui usuário e registra auditoria.

        Raises:
            UserNotFoundError: Se usuário não existir
            InsufficientPermissionsError: Se tentar excluir técnico
            LastAdminError: Se tentar excluir único admin
        """
        # Verificar se usuário existe
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Verificar se é um técnico
        if user.get("tipo") == "tecnico":
            raise InsufficientPermissionsError(
                action="excluir_usuario", required_role="administrador", user_role="tecnico"
            )

        if self.user_repo.is_unique_admin(user_id):
            raise LastAdminError()

        success = self.user_repo.delete_user(user_id)
        if success:
            self.audit_repo.create_log(
                user_id=user_id,
                action="EXCLUIR",
                affected_table="USUARIOS",
                id_afetado=user_id,
            )
            return True, "Usuário excluído com sucesso!"
        raise UserNotFoundError(user_id)

    def get_all_users(self) -> list[dict[Any, Any]]:
        """Retorna lista de todos os usuários."""
        result = self.user_repo.get_users()
        return list(result) if result else []

    def update_password(
        self, user_id: int, new_password: str, admin_user_id: int | None = None
    ) -> tuple[bool, str]:
        """
        Atualiza senha de usuário com validação robusta e registra auditoria.

        Raises:
            UserNotFoundError: Se usuário não existir
            InsufficientPermissionsError: Se tentar alterar senha de técnico
            WeakPasswordError: Se senha não atender requisitos
        """
        # Verificar se usuário existe
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Verificar se é um técnico
        if user.get("tipo") == "tecnico":
            raise InsufficientPermissionsError(
                action="alterar_senha", required_role="administrador", user_role="tecnico"
            )

        # Validação robusta da nova senha
        password_result = Validators.validate_password(new_password, strict=False)
        password_valid = password_result.is_valid
        password_error = password_result.errors[0] if password_result.errors else ""

        if not password_valid:
            raise WeakPasswordError([password_error])

        try:
            success = self.user_repo.update_password(user_id, new_password)
            if success:
                # Log com contexto de segurança
                security_context = SecurityLogger.log_user_management(
                    action="UPDATE_PASSWORD",
                    admin_user_id=admin_user_id or user_id,
                    admin_username="system",
                    target_user_id=user_id,
                    changes={"password_updated": True},
                )

                self.audit_repo.create_log(
                    user_id=admin_user_id or user_id,
                    action="ATUALIZAR_SENHA",
                    affected_table="USUARIOS",
                    id_afetado=user_id,
                    new_data=security_context,
                    ip_address=security_context.get("ip_address"),
                )
                return True, "Senha atualizada com sucesso"
            raise UserNotFoundError(user_id)
        except (UserNotFoundError, InsufficientPermissionsError, WeakPasswordError):
            raise
        except Exception as e:
            # Log erro de segurança
            security_context = SecurityLogger.log_security_violation(
                violation_type="PASSWORD_UPDATE_ERROR",
                user_id=admin_user_id or user_id,
                details={"error": str(e), "target_user_id": user_id},
            )
            self.audit_repo.create_log(
                user_id=admin_user_id or user_id,
                action="ERRO_ATUALIZAR_SENHA",
                affected_table="USUARIOS",
                id_afetado=user_id,
                previous_data=security_context,
                ip_address=security_context.get("ip_address"),
            )
            raise InvalidUserDataError("password", f"Erro ao atualizar senha: {e!s}") from e
