import pytest

from ozempic_seguro.domain.audit import AuditAction
from ozempic_seguro.domain.exceptions import (
    LastAdminError,
    PermissionDeniedError,
    ProtectedUserError,
    SelfDeletionError,
    UsernameTakenError,
    UserNotFoundError,
    ValidationError,
)
from ozempic_seguro.domain.users import Role


@pytest.fixture
def admin(app):
    return app.login_as(Role.ADMIN)


class TestRegister:
    def test_creates_user_with_hashed_password(self, app, admin):
        user = app.users.register(" Maria ", "123", "5678", Role.SELLER)

        assert (user.full_name, user.username, user.role) == ("Maria", "123", Role.SELLER)
        assert app.users_repo.get_password_hash(user.id) == "hashed:5678"
        record = app.audit_log.records[-1]
        assert record.action is AuditAction.USER_CREATED
        assert (record.user_id, record.target_id) == (admin.id, user.id)

    def test_validates_input(self, app, admin):
        with pytest.raises(ValidationError) as error:
            app.users.register("", "abc", "12", Role.SELLER)

        assert error.value.errors == [
            "O nome é obrigatório",
            "O usuário deve conter apenas números",
            "A senha deve ter entre 4 e 8 dígitos",
        ]

    def test_rejects_taken_username(self, app, admin):
        with pytest.raises(UsernameTakenError):
            app.users.register("Outro", "10", "5678", Role.SELLER)

    def test_requires_admin(self, app):
        app.login_as(Role.SELLER)

        with pytest.raises(PermissionDeniedError):
            app.users.register("Maria", "123", "5678", Role.SELLER)


class TestChangePassword:
    def test_updates_the_hash(self, app, admin):
        seller = app.accounts[Role.SELLER]

        app.users.change_password(seller.id, "9876", "9876")

        assert app.users_repo.get_password_hash(seller.id) == "hashed:9876"
        assert app.audit_log.actions()[-1] is AuditAction.PASSWORD_CHANGED

    def test_confirmation_must_match(self, app, admin):
        with pytest.raises(ValidationError, match="não coincidem"):
            app.users.change_password(app.accounts[Role.SELLER].id, "9876", "9875")

    def test_applies_password_policy(self, app, admin):
        with pytest.raises(ValidationError, match="apenas números"):
            app.users.change_password(app.accounts[Role.SELLER].id, "abcd", "abcd")

    def test_technician_is_protected(self, app, admin):
        with pytest.raises(ProtectedUserError):
            app.users.change_password(app.accounts[Role.TECHNICIAN].id, "9876", "9876")

    def test_unknown_user(self, app, admin):
        with pytest.raises(UserNotFoundError):
            app.users.change_password(999, "9876", "9876")


class TestDelete:
    def test_deactivates_instead_of_removing(self, app, admin):
        seller = app.accounts[Role.SELLER]

        app.users.delete(seller.id)

        assert app.users_repo.get(seller.id).active is False
        assert app.audit_log.actions()[-1] is AuditAction.USER_DELETED

    def test_deleted_user_cannot_be_deleted_again(self, app, admin):
        seller = app.accounts[Role.SELLER]
        app.users.delete(seller.id)

        with pytest.raises(UserNotFoundError):
            app.users.delete(seller.id)

    def test_cannot_delete_yourself(self, app, admin):
        with pytest.raises(SelfDeletionError):
            app.users.delete(admin.id)

    def test_technician_is_protected(self, app, admin):
        with pytest.raises(ProtectedUserError):
            app.users.delete(app.accounts[Role.TECHNICIAN].id)

    def test_can_delete_another_admin(self, app, admin):
        other = app.users.register("Admin 2", "02", "1234", Role.ADMIN)

        app.users.delete(other.id)

        assert app.users_repo.count_active(Role.ADMIN) == 1

    def test_keeps_at_least_one_active_admin(self, app, admin):
        # The logged-in admin was deactivated elsewhere, leaving "02" as the only
        # active admin: removing it would lock everyone out of the admin panel.
        other = app.users.register("Admin 2", "02", "1234", Role.ADMIN)
        app.users_repo.deactivate(admin.id)

        with pytest.raises(LastAdminError):
            app.users.delete(other.id)


class TestListUsers:
    def test_lists_everyone_for_admin(self, app, admin):
        assert {u.username for u in app.users.list_users()} == {"00", "10", "20", "01"}

    def test_requires_admin(self, app):
        app.login_as(Role.STOCKER)

        with pytest.raises(PermissionDeniedError):
            app.users.list_users()
