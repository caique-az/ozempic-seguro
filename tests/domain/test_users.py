import pytest

from ozempic_seguro.domain.users import CredentialPolicy, Role, User


class TestRole:
    def test_values_match_persisted_identifiers(self):
        assert [r.value for r in Role] == ["administrador", "vendedor", "repositor", "tecnico"]

    @pytest.mark.parametrize(
        ("role", "label"),
        [
            (Role.ADMIN, "Administrador"),
            (Role.SELLER, "Vendedor"),
            (Role.STOCKER, "Repositor"),
            (Role.TECHNICIAN, "Técnico"),
        ],
    )
    def test_label(self, role, label):
        assert role.label == label


class TestUser:
    def test_only_technicians_are_protected(self):
        protected = {role for role in Role if User(1, "10", "Ana", role, active=True).is_protected}
        assert protected == {Role.TECHNICIAN}


class TestPasswordPolicy:
    @pytest.mark.parametrize("password", ["1234", "12345678"])
    def test_accepts_numeric_passwords_within_limits(self, password):
        assert CredentialPolicy.password_errors(password) == []

    def test_rejects_empty_password(self):
        assert CredentialPolicy.password_errors("") == ["A senha é obrigatória"]

    @pytest.mark.parametrize("password", ["123", "123456789"])
    def test_rejects_length_outside_limits(self, password):
        assert CredentialPolicy.password_errors(password) == [
            "A senha deve ter entre 4 e 8 dígitos"
        ]

    def test_rejects_non_numeric_password(self):
        assert "A senha deve conter apenas números" in CredentialPolicy.password_errors("12ab")


class TestNewUserPolicy:
    def test_valid_data_has_no_errors(self):
        assert CredentialPolicy.new_user_errors("Maria Silva", "1234", "5678") == []

    def test_reports_every_missing_field(self):
        errors = CredentialPolicy.new_user_errors("  ", "", "")
        assert errors == [
            "O nome é obrigatório",
            "O usuário é obrigatório",
            "A senha é obrigatória",
        ]

    def test_rejects_long_name(self):
        errors = CredentialPolicy.new_user_errors("A" * 27, "1234", "5678")
        assert errors == ["O nome deve ter no máximo 26 caracteres"]

    def test_rejects_non_numeric_and_long_username(self):
        errors = CredentialPolicy.new_user_errors("Maria", "abcdefghi", "5678")
        assert errors == [
            "O usuário deve conter apenas números",
            "O usuário deve ter no máximo 8 dígitos",
        ]
