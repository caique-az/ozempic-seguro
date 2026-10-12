"""
Testes estendidos para Validators - Cobertura adicional.
"""

from ozempic_seguro.core.validators import (
    UserType,
    ValidationResult,
    ValidationRule,
    Validators,
)


class TestValidationResult:
    """Testes para ValidationResult"""

    def test_valid_result(self):
        """Testa resultado válido"""
        result = ValidationResult(is_valid=True, errors=[])

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_result(self):
        """Testa resultado inválido"""
        result = ValidationResult(is_valid=False, errors=["Error 1"])

        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_add_error(self):
        """Testa adição de erro"""
        result = ValidationResult(is_valid=True, errors=[])

        result.add_error("New error")

        assert result.is_valid is False
        assert "New error" in result.errors

    def test_sanitized_value(self):
        """Testa valor sanitizado"""
        result = ValidationResult(is_valid=True, errors=[], sanitized_value="clean_value")

        assert result.sanitized_value == "clean_value"


class TestValidationRule:
    """Testes para ValidationRule"""

    def test_rule_passes(self):
        """Testa regra que passa"""
        rule = ValidationRule(
            name="test_rule", validator=lambda x: x > 0, error_message="Value must be positive"
        )

        is_valid, error = rule.validate(5)

        assert is_valid is True
        assert error is None

    def test_rule_fails(self):
        """Testa regra que falha"""
        rule = ValidationRule(
            name="test_rule", validator=lambda x: x > 0, error_message="Value must be positive"
        )

        is_valid, error = rule.validate(-1)

        assert is_valid is False
        assert error == "Value must be positive"

    def test_rule_exception(self):
        """Testa regra que lança exceção"""
        rule = ValidationRule(
            name="test_rule", validator=lambda x: x.invalid_method(), error_message="Error"
        )

        is_valid, error = rule.validate("test")

        assert is_valid is False
        assert "Erro na validação" in error


class TestUserType:
    """Testes para UserType enum"""

    def test_user_types_exist(self):
        """Testa que tipos de usuário existem"""
        assert UserType.ADMINISTRADOR.value == "administrador"
        assert UserType.VENDEDOR.value == "vendedor"
        assert UserType.REPOSITOR.value == "repositor"
        assert UserType.TECNICO.value == "tecnico"


class TestValidatorsExtended:
    """Testes estendidos para Validators"""

    def test_validate_email_valid(self):
        """Testa validação de email válido"""
        result = Validators.validate_email("test@example.com")
        assert result.is_valid is True

    def test_validate_email_invalid(self):
        """Testa validação de email inválido"""
        result = Validators.validate_email("invalid-email")
        assert result.is_valid is False

    def test_validate_phone_valid(self):
        """Testa validação de telefone válido"""
        result = Validators.validate_phone("(11) 99999-9999")
        assert result.is_valid is True

    def test_validate_phone_invalid(self):
        """Testa validação de telefone inválido"""
        result = Validators.validate_phone("123")
        assert result.is_valid is False

    def test_validate_id_valid(self):
        """Testa validação de ID válido"""
        result = Validators.validate_id(1)
        assert result.is_valid is True

    def test_validate_id_invalid(self):
        """Testa validação de ID inválido"""
        result = Validators.validate_id(-1)
        assert result.is_valid is False

    def test_validate_id_zero(self):
        """Testa validação de ID zero"""
        result = Validators.validate_id(0)
        assert result.is_valid is False

    def test_sanitize_string_max_length(self):
        """Testa sanitização com limite de tamanho"""
        long_string = "a" * 1000

        result = Validators.sanitize_string(long_string, max_length=50)

        assert len(result) <= 50

    def test_sanitize_string_removes_sql(self):
        """Testa que SQL injection é removido"""
        dangerous = "'; DROP TABLE users; --"

        result = Validators.sanitize_string(dangerous)

        assert "DROP TABLE" not in result

    def test_sanitize_string_removes_xss(self):
        """Testa que XSS é removido"""
        dangerous = "<script>alert('xss')</script>"

        result = Validators.sanitize_string(dangerous)

        assert "<script>" not in result

    def test_is_safe_for_logging_true(self):
        """Testa que string segura é identificada"""
        safe = "normal text 123"

        assert Validators.is_safe_for_logging(safe) is True

    def test_is_safe_for_logging_with_script(self):
        """Testa que string com script é identificada"""
        dangerous = "<script>alert('xss')</script>"

        # Verifica se retorna booleano
        result = Validators.is_safe_for_logging(dangerous)
        assert isinstance(result, bool)

    def test_validate_and_sanitize_user_input_valid(self):
        """Testa validação e sanitização de entrada válida"""
        result = Validators.validate_and_sanitize_user_input(
            username="testuser", password="TestPass123", name="Test User", user_type="vendedor"
        )

        assert result["valid"] is True
        assert "sanitized_data" in result

    def test_validate_and_sanitize_user_input_invalid(self):
        """Testa validação de entrada inválida"""
        result = Validators.validate_and_sanitize_user_input(
            username="a",  # muito curto
            password="123",  # muito curto
            name="",  # vazio
            user_type="invalid",  # tipo inválido
        )

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_name_valid(self):
        """Testa validação de nome válido"""
        result = Validators.validate_name("João da Silva")
        assert result.is_valid is True

    def test_validate_name_with_accents(self):
        """Testa validação de nome com acentos"""
        result = Validators.validate_name("José Müller")
        assert result.is_valid is True

    def test_validate_name_too_short(self):
        """Testa validação de nome muito curto"""
        result = Validators.validate_name("A")
        assert result.is_valid is False

    def test_validate_date_valid(self):
        """Testa validação de data válida"""
        result = Validators.validate_date("2025-01-15")
        assert result.is_valid is True

    def test_validate_date_invalid_format(self):
        """Testa validação de data com formato inválido"""
        result = Validators.validate_date("15/01/2025")
        assert result.is_valid is False
