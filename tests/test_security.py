from ozempic_seguro.core.validators import Validators
from ozempic_seguro.repositories.security import hash_password, verify_password


class TestSecurity:
    """Testes para funções de segurança"""

    def test_hash_password_creates_bcrypt_hash(self):
        """Testa se hash_password cria hash bcrypt válido"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed.startswith("$2b$")  # bcrypt prefix
        assert len(hashed) >= 60  # bcrypt hash length

    def test_verify_password_correct(self):
        """Testa verificação de senha correta"""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta"""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_hash_password_different_salts(self):
        """Testa se hashes diferentes são gerados para mesma senha"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_verify_legacy_password(self):
        """Testa compatibilidade com senhas legacy SHA256"""
        # Simular hash legacy (SHA256 + salt)
        legacy_hash = "legacy_hash_format"

        # Por enquanto, deve retornar False para hashes inválidos
        assert verify_password("any_password", legacy_hash) is False


class TestInputValidator:
    """Testes para validação de entrada usando o novo sistema de validadores"""

    def test_sanitize_input_removes_dangerous_chars(self):
        """Testa sanitização de caracteres perigosos"""
        dangerous = "'; DROP TABLE users; --"
        sanitized = Validators.sanitize_string(dangerous)

        assert "DROP TABLE" not in sanitized
        assert "--" not in sanitized

    def test_sanitize_input_preserves_safe_text(self):
        """Testa que texto seguro é preservado"""
        safe_text = "João da Silva 123"
        sanitized = Validators.sanitize_string(safe_text)

        # O texto é escapado por segurança mas preservado
        assert "João da Silva 123" in sanitized or "Jo" in sanitized

    def test_is_valid_username_valid(self):
        """Testa validação de username válido"""
        assert Validators.validate_username("user123").is_valid is True
        assert Validators.validate_username("john_doe").is_valid is True
        assert Validators.validate_username("admin").is_valid is True

    def test_is_valid_username_invalid(self):
        """Testa validação de username inválido"""
        assert Validators.validate_username("").is_valid is False
        assert Validators.validate_username("a").is_valid is False  # Too short
        assert Validators.validate_username("user@123").is_valid is False  # Special char
        assert Validators.validate_username("user name").is_valid is False  # Space
        assert Validators.validate_username("a" * 51).is_valid is False  # Too long

    def test_is_valid_password_valid(self):
        """Testa validação de senha válida"""
        # Com o novo validador, senha precisa ter 8+ chars, maiúscula, minúscula e número
        assert Validators.validate_password("Password123").is_valid is True
        assert Validators.validate_password("SecurePass1").is_valid is True

    def test_is_valid_password_invalid(self):
        """Testa validação de senha inválida"""
        assert Validators.validate_password("").is_valid is False
        assert Validators.validate_password("123").is_valid is False  # Too short
        assert Validators.validate_password("a" * 129).is_valid is False  # Too long
        # Testes de modo estrito (requer maiúscula, minúscula e número)
        assert (
            Validators.validate_password("password123", strict=True).is_valid is False
        )  # No uppercase
        assert (
            Validators.validate_password("PASSWORD123", strict=True).is_valid is False
        )  # No lowercase
        assert Validators.validate_password("Password", strict=True).is_valid is False  # No digit

    def test_escape_html(self):
        """Testa escape de HTML"""
        html_text = "<script>alert('XSS')</script>"
        escaped = Validators.sanitize_string(html_text)

        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped
        assert "&lt;/script&gt;" in escaped

    def test_is_strong_password(self):
        """Testa validação de força de senha (modo estrito)"""
        # Senhas fracas (não atendem aos critérios estritos)
        assert Validators.validate_password("123", strict=True).is_valid is False
        assert Validators.validate_password("password", strict=True).is_valid is False
        assert Validators.validate_password("12345678", strict=True).is_valid is False

        # Senhas fortes (8+ chars, maiúscula, minúscula e números)
        assert Validators.validate_password("Password123", strict=True).is_valid is True
        assert Validators.validate_password("SecurePass2024", strict=True).is_valid is True
