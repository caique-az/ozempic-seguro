"""Errors raised when a business rule is violated.

Messages are written for the end user (Portuguese), since the UI shows them as-is.
"""


class DomainError(Exception):
    """Base class for every business rule violation."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    """Input data does not satisfy the business constraints."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class NotAuthenticatedError(DomainError):
    def __init__(self) -> None:
        super().__init__("Nenhum usuário autenticado")


class PermissionDeniedError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    def __init__(self, remaining_attempts: int) -> None:
        if remaining_attempts > 0:
            message = f"Usuário ou senha inválidos. {remaining_attempts} tentativa(s) restante(s)"
        else:
            message = "Usuário ou senha inválidos"
        super().__init__(message)
        self.remaining_attempts = remaining_attempts


class AccountLockedError(DomainError):
    def __init__(self, remaining_seconds: int) -> None:
        minutes, seconds = divmod(remaining_seconds, 60)
        super().__init__(
            f"Muitas tentativas incorretas. Tente novamente em {minutes}:{seconds:02d}"
        )
        self.remaining_seconds = remaining_seconds


class SystemLockedError(DomainError):
    def __init__(self, remaining_seconds: int) -> None:
        minutes, seconds = divmod(remaining_seconds, 60)
        super().__init__(
            f"Sistema bloqueado por {minutes}:{seconds:02d} após a abertura de uma gaveta"
        )
        self.remaining_seconds = remaining_seconds


class UserNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Usuário não encontrado")


class UsernameTakenError(DomainError):
    def __init__(self, username: str) -> None:
        super().__init__(f"O usuário '{username}' já está em uso")
        self.username = username


class LastAdminError(DomainError):
    def __init__(self) -> None:
        super().__init__("O sistema precisa de pelo menos um administrador ativo")


class ProtectedUserError(DomainError):
    def __init__(self) -> None:
        super().__init__("Usuários técnicos não podem ser alterados pelo painel")


class SelfDeletionError(DomainError):
    def __init__(self) -> None:
        super().__init__("Você não pode excluir sua própria conta")


class DrawerStateError(DomainError):
    pass
