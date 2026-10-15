"""User administration performed from the admin panel."""

from ..domain.audit import AuditAction, AuditTarget
from ..domain.exceptions import (
    LastAdminError,
    ProtectedUserError,
    SelfDeletionError,
    UserNotFoundError,
    ValidationError,
)
from ..domain.permissions import Permission, require
from ..domain.ports import AuditLog, PasswordHasher, UserRepository
from ..domain.users import CredentialPolicy, Role, User
from .state import Session


class UserService:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        audit: AuditLog,
        session: Session,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._audit = audit
        self._session = session

    def list_users(self) -> list[User]:
        self._require_admin()
        return self._users.list_all()

    def register(self, full_name: str, username: str, password: str, role: Role) -> User:
        actor = self._require_admin()

        errors = CredentialPolicy.new_user_errors(full_name, username, password)
        if errors:
            raise ValidationError(errors)

        user = self._users.add(
            username.strip(), self._hasher.hash(password), full_name.strip(), role
        )
        self._audit.record(
            AuditAction.USER_CREATED,
            user_id=actor.id,
            target=AuditTarget.USER,
            target_id=user.id,
            details={"username": user.username, "role": role.value},
        )
        return user

    def change_password(self, user_id: int, new_password: str, confirmation: str) -> None:
        actor = self._require_admin()

        if new_password != confirmation:
            raise ValidationError(["As senhas não coincidem"])
        errors = CredentialPolicy.password_errors(new_password)
        if errors:
            raise ValidationError(errors)

        target = self._get_modifiable(user_id)
        self._users.set_password_hash(target.id, self._hasher.hash(new_password))
        self._audit.record(
            AuditAction.PASSWORD_CHANGED,
            user_id=actor.id,
            target=AuditTarget.USER,
            target_id=target.id,
        )

    def delete(self, user_id: int) -> None:
        """Deactivate a user.

        Users are never removed from the database: the audit trail and drawer history
        reference them, and those records must stay intact.
        """
        actor = self._require_admin()
        if user_id == actor.id:
            raise SelfDeletionError()

        target = self._get_modifiable(user_id)
        if target.role is Role.ADMIN and self._users.count_active(Role.ADMIN) <= 1:
            raise LastAdminError()

        self._users.deactivate(target.id)
        self._audit.record(
            AuditAction.USER_DELETED,
            user_id=actor.id,
            target=AuditTarget.USER,
            target_id=target.id,
            details={"username": target.username},
        )

    def _require_admin(self) -> User:
        actor = self._session.require_user()
        require(actor, Permission.MANAGE_USERS)
        return actor

    def _get_modifiable(self, user_id: int) -> User:
        user = self._users.get(user_id)
        if user is None or not user.active:
            raise UserNotFoundError()
        if user.is_protected:
            raise ProtectedUserError()
        return user
