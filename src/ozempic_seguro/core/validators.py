"""
Sistema centralizado de validação com regras de negócio.
Unifica todas as validações em um único módulo.
"""

import html
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ValidationRule:
    """Representa uma regra de validação"""

    def __init__(self, name: str, validator: Callable[[Any], bool], error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message

    def validate(self, value: Any) -> tuple[bool, str | None]:
        """Executa validação e retorna resultado"""
        try:
            if self.validator(value):
                return True, None
            return False, self.error_message
        except Exception as e:
            return False, f"Erro na validação: {e!s}"


class UserType(Enum):
    """Tipos de usuário válidos"""

    ADMINISTRADOR = "administrador"
    VENDEDOR = "vendedor"
    REPOSITOR = "repositor"
    TECNICO = "tecnico"


@dataclass
class ValidationResult:
    """Resultado de uma validação"""

    is_valid: bool
    errors: list[str]
    sanitized_value: Any | None = None

    def add_error(self, error: str) -> None:
        """Adiciona erro à lista"""
        self.errors.append(error)
        self.is_valid = False


class Validators:
    """Classe com todos os validadores centralizados"""

    # Padrões regex
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{2,50}$")
    NAME_PATTERN = re.compile(r"^[a-zA-ZÀ-ÿ\s\-\']{2,100}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^[\d\s\-\(\)\+]{10,20}$")
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    TIME_PATTERN = re.compile(r"^\d{2}:\d{2}(:\d{2})?$")

    # Caracteres perigosos para SQL/XSS
    DANGEROUS_PATTERNS = (
        r"<script[^>]*>.*?</script>",  # Scripts
        r"javascript:",  # JavaScript URLs
        r"on\w+\s*=",  # Event handlers
        r"--",  # SQL comments
        r"/\*.*?\*/",  # SQL block comments
        r"\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b",  # SQL commands
        r"xp_|sp_",  # SQL Server procedures
    )

    @classmethod
    def validate_username(cls, username: str) -> ValidationResult:
        """
        Valida nome de usuário.

        Regras:
        - 2-50 caracteres
        - Apenas letras, números e underscore
        - Sem espaços ou caracteres especiais
        """
        result = ValidationResult(is_valid=True, errors=[])

        if not username:
            result.add_error("Nome de usuário é obrigatório")
            return result

        username = username.strip()

        if len(username) < 2:
            result.add_error("Nome de usuário deve ter pelo menos 2 caracteres")
        elif len(username) > 50:
            result.add_error("Nome de usuário não pode ter mais de 50 caracteres")

        if not cls.USERNAME_PATTERN.match(username):
            result.add_error("Nome de usuário deve conter apenas letras, números e underscore")

        # Sanitiza
        if result.is_valid:
            result.sanitized_value = cls.sanitize_string(username)

        return result

    @classmethod
    def validate_password(cls, password: str, strict: bool = False) -> ValidationResult:
        """
        Valida senha.

        Regras básicas (padrão):
        - Mínimo 4 caracteres (conforme SecurityConfig.MIN_PASSWORD_LENGTH)
        - Máximo 128 caracteres
        - Sem caracteres de controle

        Regras estritas (strict=True):
        - Mínimo 8 caracteres
        - Pelo menos 1 letra maiúscula
        - Pelo menos 1 letra minúscula
        - Pelo menos 1 número
        """
        from ..config import SecurityConfig

        result = ValidationResult(is_valid=True, errors=[])

        if not password:
            result.add_error("Senha é obrigatória")
            return result

        min_length = 8 if strict else SecurityConfig.MIN_PASSWORD_LENGTH

        if len(password) < min_length:
            result.add_error(f"Senha deve ter pelo menos {min_length} caracteres")

        if len(password) > SecurityConfig.MAX_PASSWORD_LENGTH:
            result.add_error(
                f"Senha não pode ter mais de {SecurityConfig.MAX_PASSWORD_LENGTH} caracteres"
            )

        # Verifica caracteres de controle
        if any(ord(char) < 32 for char in password):
            result.add_error("Senha contém caracteres inválidos")

        # Validação estrita (opcional)
        if strict and result.is_valid:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)

            if not has_upper:
                result.add_error("Senha deve conter pelo menos uma letra maiúscula")

            if not has_lower:
                result.add_error("Senha deve conter pelo menos uma letra minúscula")

            if not has_digit:
                result.add_error("Senha deve conter pelo menos um número")

        result.sanitized_value = password if result.is_valid else None

        return result

    @classmethod
    def validate_name(cls, name: str) -> ValidationResult:
        """
        Valida nome completo.

        Regras:
        - 2-100 caracteres
        - Apenas letras, espaços, hífens e apóstrofos
        - Pelo menos duas palavras (nome e sobrenome)
        """
        result = ValidationResult(is_valid=True, errors=[])

        if not name:
            result.add_error("Nome é obrigatório")
            return result

        name = name.strip()

        if len(name) < 2:
            result.add_error("Nome deve ter pelo menos 2 caracteres")
        elif len(name) > 100:
            result.add_error("Nome não pode ter mais de 100 caracteres")

        if not cls.NAME_PATTERN.match(name):
            result.add_error("Nome deve conter apenas letras, espaços, hífens e apóstrofos")

        # Verifica se tem pelo menos duas palavras
        words = name.split()
        if len(words) < 2:
            result.add_error("Por favor, informe nome e sobrenome")

        # Sanitiza
        if result.is_valid:
            result.sanitized_value = cls.sanitize_string(name)

        return result

    @classmethod
    def validate_user_type(cls, user_type: str) -> ValidationResult:
        """Valida tipo de usuário"""
        result = ValidationResult(is_valid=True, errors=[])

        if not user_type:
            result.add_error("Tipo de usuário é obrigatório")
            return result

        user_type = user_type.lower().strip()

        valid_types = [t.value for t in UserType]
        if user_type not in valid_types:
            result.add_error(f"Tipo deve ser um dos: {', '.join(valid_types)}")
        else:
            result.sanitized_value = user_type

        return result

    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """Valida endereço de email"""
        result = ValidationResult(is_valid=True, errors=[])

        if not email:
            result.add_error("Email é obrigatório")
            return result

        email = email.strip().lower()

        if not cls.EMAIL_PATTERN.match(email):
            result.add_error("Email inválido")
        else:
            result.sanitized_value = email

        return result

    @classmethod
    def validate_phone(cls, phone: str) -> ValidationResult:
        """Valida número de telefone"""
        result = ValidationResult(is_valid=True, errors=[])

        if not phone:
            result.add_error("Telefone é obrigatório")
            return result

        phone = phone.strip()

        if not cls.PHONE_PATTERN.match(phone):
            result.add_error("Telefone inválido")
        else:
            # Remove caracteres não numéricos para armazenamento
            result.sanitized_value = re.sub(r"\D", "", phone)

        return result

    @classmethod
    def validate_date(cls, date_str: str) -> ValidationResult:
        """Valida formato de data (YYYY-MM-DD)"""
        result = ValidationResult(is_valid=True, errors=[])

        if not date_str:
            result.add_error("Data é obrigatória")
            return result

        if not cls.DATE_PATTERN.match(date_str):
            result.add_error("Data deve estar no formato YYYY-MM-DD")
            return result

        # Valida valores
        try:
            year, month, day = map(int, date_str.split("-"))

            if year < 1900 or year > 2100:
                result.add_error("Ano deve estar entre 1900 e 2100")

            if month < 1 or month > 12:
                result.add_error("Mês inválido")

            if day < 1 or day > 31:
                result.add_error("Dia inválido")

            if result.is_valid:
                result.sanitized_value = date_str

        except ValueError:
            result.add_error("Data contém valores inválidos")

        return result

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 255) -> str:
        """
        Sanitiza string removendo caracteres perigosos.

        Args:
            value: String a sanitizar
            max_length: Comprimento máximo

        Returns:
            String sanitizada
        """
        if not value:
            return ""

        # Remove caracteres de controle
        value = "".join(char for char in value if ord(char) >= 32)

        # Escape HTML
        value = html.escape(value)

        # Remove padrões perigosos
        for pattern in cls.DANGEROUS_PATTERNS:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)

        # Trunca se necessário
        if len(value) > max_length:
            value = value[:max_length]

        return value.strip()

    @classmethod
    def is_safe_for_logging(cls, value: Any) -> bool:
        """Verifica se valor é seguro para logs"""
        if not isinstance(value, str):
            return True

        # Palavras-chave sensíveis
        sensitive_keywords = [
            "password",
            "senha",
            "token",
            "secret",
            "key",
            "api",
            "credential",
            "auth",
        ]

        value_lower = str(value).lower()
        return not any(keyword in value_lower for keyword in sensitive_keywords)

    @classmethod
    def validate_id(cls, id_value: Any) -> ValidationResult:
        """Valida ID numérico"""
        result = ValidationResult(is_valid=True, errors=[])

        try:
            id_int = int(id_value)
            if id_int <= 0:
                result.add_error("ID deve ser maior que zero")
            else:
                result.sanitized_value = id_int
        except (ValueError, TypeError):
            result.add_error("ID deve ser um número inteiro válido")

        return result

    @classmethod
    def validate_batch(
        cls, validations: dict[str, tuple[Any, Callable]]
    ) -> dict[str, ValidationResult]:
        """
        Valida múltiplos campos de uma vez.

        Args:
            validations: Dict com nome_campo: (valor, função_validação)

        Returns:
            Dict com resultados de validação

        Exemplo:
            results = Validators.validate_batch({
                'username': (username, Validators.validate_username),
                'password': (password, Validators.validate_password),
                'email': (email, Validators.validate_email)
            })
        """
        results = {}

        for field_name, (value, validator_func) in validations.items():
            results[field_name] = validator_func(value)

        return results

    @classmethod
    def get_all_errors(cls, results: dict[str, ValidationResult]) -> list[str]:
        """Extrai todos os erros de um batch de validações"""
        all_errors = []

        for field_name, result in results.items():
            for error in result.errors:
                all_errors.append(f"{field_name}: {error}")

        return all_errors

    @classmethod
    def all_valid(cls, results: dict[str, ValidationResult]) -> bool:
        """Verifica se todas as validações passaram"""
        return all(result.is_valid for result in results.values())

    @classmethod
    def validate_and_sanitize_user_input(
        cls,
        username: str | None = None,
        password: str | None = None,
        name: str | None = None,
        user_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Valida e sanitiza entrada completa de usuário.

        Args:
            username: Nome de usuário
            password: Senha
            name: Nome completo
            user_type: Tipo de usuário

        Returns:
            Dict com 'valid', 'errors' e 'sanitized_data'
        """
        result = {"valid": True, "errors": [], "sanitized_data": {}}

        if username is not None:
            validation = cls.validate_username(username)
            if not validation.is_valid:
                result["valid"] = False
                result["errors"].extend([f"Usuário: {e}" for e in validation.errors])
            else:
                result["sanitized_data"]["username"] = cls.sanitize_string(username, 50)

        if password is not None:
            validation = cls.validate_password(password, strict=False)
            if not validation.is_valid:
                result["valid"] = False
                result["errors"].extend([f"Senha: {e}" for e in validation.errors])
            else:
                result["sanitized_data"]["password"] = password

        if name is not None:
            validation = cls.validate_name(name)
            if not validation.is_valid:
                result["valid"] = False
                result["errors"].extend([f"Nome: {e}" for e in validation.errors])
            else:
                result["sanitized_data"]["name"] = cls.sanitize_string(name, 100)

        if user_type is not None:
            validation = cls.validate_user_type(user_type)
            if not validation.is_valid:
                result["valid"] = False
                result["errors"].extend([f"Tipo: {e}" for e in validation.errors])
            else:
                result["sanitized_data"]["user_type"] = user_type.lower().strip()

        return result
