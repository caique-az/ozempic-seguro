"""
Testes para módulo security - Hash de senhas.
"""

from ozempic_seguro.repositories.security import (
    hash_password,
    is_bcrypt_hash,
    verify_password,
)


class TestPasswordFunctions:
    """Testes para funções de senha"""

    def test_hash_password(self):
        """Testa hash de senha"""
        password = "TestPassword123"

        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password

    def test_verify_password_correct(self):
        """Testa verificação de senha correta"""
        password = "TestPassword123"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta"""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)

        result = verify_password(wrong_password, hashed)

        assert result is False

    def test_hash_is_unique(self):
        """Testa que hashes são únicos (salt diferente)"""
        password = "TestPassword123"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes devem ser diferentes devido ao salt
        assert hash1 != hash2

    def test_verify_both_hashes(self):
        """Testa que ambos os hashes verificam corretamente"""
        password = "TestPassword123"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_is_bcrypt_hash_valid(self):
        """Testa identificação de hash bcrypt válido"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert is_bcrypt_hash(hashed) is True

    def test_is_bcrypt_hash_invalid(self):
        """Testa identificação de hash não-bcrypt"""
        invalid_hash = "not_a_bcrypt_hash"

        assert is_bcrypt_hash(invalid_hash) is False

    def test_verify_invalid_hash_format(self):
        """Testa verificação com formato de hash inválido"""
        password = "TestPassword123"
        invalid_hash = "invalid_hash"

        result = verify_password(password, invalid_hash)

        assert result is False
