"""
Testes para StructuredLogger - Sistema de logging estruturado.
"""

import json
import logging

from ozempic_seguro.core.structured_logger import (
    SensitiveDataFilter,
    StructuredFormatter,
    StructuredLogger,
)


class TestStructuredFormatter:
    """Testes para StructuredFormatter"""

    def test_format_basic_log(self):
        """Testa formatação básica de log"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert isinstance(result, str)
        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"

    def test_format_with_user_id(self):
        """Testa formatação com user_id"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.user_id = 123

        result = formatter.format(record)
        data = json.loads(result)

        assert data["user_id"] == 123

    def test_format_with_action(self):
        """Testa formatação com action"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.action = "LOGIN"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["action"] == "LOGIN"

    def test_format_with_ip_address(self):
        """Testa formatação com ip_address"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.ip_address = "192.168.1.1"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["ip_address"] == "192.168.1.1"

    def test_format_with_exception(self):
        """Testa formatação com exceção"""
        formatter = StructuredFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"


class TestSensitiveDataFilter:
    """Testes para SensitiveDataFilter"""

    def test_filter_allows_normal_logs(self):
        """Testa que logs normais passam"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Normal message",
            args=(),
            exc_info=None,
        )

        result = filter.filter(record)

        assert result is True

    def test_filter_masks_password(self):
        """Testa mascaramento de password"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="password=secret123",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "secret123" not in record.msg
        assert "REDACTED" in record.msg

    def test_filter_masks_senha(self):
        """Testa mascaramento de senha"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg='senha: "minhasenha"',
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "minhasenha" not in record.msg

    def test_filter_masks_token(self):
        """Testa mascaramento de token"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="token=abc123xyz",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "abc123xyz" not in record.msg

    def test_sensitive_fields_list(self):
        """Testa lista de campos sensíveis"""
        filter = SensitiveDataFilter()

        assert "password" in filter.SENSITIVE_FIELDS
        assert "senha" in filter.SENSITIVE_FIELDS
        assert "token" in filter.SENSITIVE_FIELDS
        assert "secret" in filter.SENSITIVE_FIELDS


class TestStructuredLogger:
    """Testes para StructuredLogger"""

    def test_get_logger_returns_logger(self):
        """Testa que get_logger retorna logger"""
        logger = StructuredLogger.get_logger("test_logger_1")

        assert isinstance(logger, logging.Logger)

    def test_get_logger_caches_logger(self):
        """Testa que logger é cacheado"""
        logger1 = StructuredLogger.get_logger("cached_logger")
        logger2 = StructuredLogger.get_logger("cached_logger")

        assert logger1 is logger2

    def test_get_logger_with_level(self):
        """Testa criação de logger com nível específico"""
        logger = StructuredLogger.get_logger("level_logger", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_logger_has_handlers(self):
        """Testa que logger tem handlers"""
        logger = StructuredLogger.get_logger("handler_logger")

        assert len(logger.handlers) > 0

    def test_logger_has_filter(self):
        """Testa que logger tem filtro de dados sensíveis"""
        logger = StructuredLogger.get_logger("filter_logger")

        # Verifica que pelo menos um handler tem o filtro
        has_filter = False
        for handler in logger.handlers:
            if any(isinstance(f, SensitiveDataFilter) for f in handler.filters):
                has_filter = True
                break

        assert has_filter is True

    def test_logger_info(self):
        """Testa log de info"""
        logger = StructuredLogger.get_logger("info_logger")
        # Não deve lançar exceção
        logger.info("Test info message")

    def test_logger_warning(self):
        """Testa log de warning"""
        logger = StructuredLogger.get_logger("warning_logger")
        logger.warning("Test warning message")

    def test_logger_error(self):
        """Testa log de error"""
        logger = StructuredLogger.get_logger("error_logger")
        logger.error("Test error message")


class TestMaskSensitiveData:
    """Testes para mascaramento de dados sensíveis"""

    def test_mask_quoted_value(self):
        """Testa mascaramento de valor entre aspas"""
        filter = SensitiveDataFilter()

        text = 'password: "mypassword123"'
        result = filter._mask_sensitive_data(text, "password")

        assert "mypassword123" not in result

    def test_mask_single_quoted_value(self):
        """Testa mascaramento de valor entre aspas simples"""
        filter = SensitiveDataFilter()

        text = "password: 'mypassword123'"
        result = filter._mask_sensitive_data(text, "password")

        assert "mypassword123" not in result

    def test_mask_equals_value(self):
        """Testa mascaramento de valor com igual"""
        filter = SensitiveDataFilter()

        text = "password=mypassword123"
        result = filter._mask_sensitive_data(text, "password")

        assert "mypassword123" not in result


class TestStructuredLoggerAdditional:
    """Testes adicionais para StructuredLogger"""

    def test_logger_debug(self):
        """Testa log de debug"""
        logger = StructuredLogger.get_logger("debug_logger", level=logging.DEBUG)
        logger.debug("Test debug message")

    def test_logger_critical(self):
        """Testa log de critical"""
        logger = StructuredLogger.get_logger("critical_logger")
        logger.critical("Test critical message")

    def test_logger_with_extra(self):
        """Testa log com dados extras"""
        logger = StructuredLogger.get_logger("extra_logger")
        logger.info("Test with extra", extra={"user_id": 123})

    def test_different_logger_names(self):
        """Testa loggers com nomes diferentes"""
        logger1 = StructuredLogger.get_logger("unique_name_1")
        logger2 = StructuredLogger.get_logger("unique_name_2")

        assert logger1 is not logger2

    def test_formatter_json_output(self):
        """Testa que formatter produz JSON válido"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Deve ser JSON válido
        import json

        parsed = json.loads(result)
        assert "timestamp" in parsed
        assert "level" in parsed
        assert "message" in parsed


class TestSensitiveDataFilterAdditional:
    """Testes adicionais para SensitiveDataFilter"""

    def test_filter_cpf(self):
        """Testa mascaramento de CPF"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="cpf=12345678900",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "12345678900" not in record.msg

    def test_filter_api_key(self):
        """Testa mascaramento de api_key"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="api_key=abc123xyz",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "abc123xyz" not in record.msg

    def test_filter_credential(self):
        """Testa mascaramento de credential"""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="credential=secret123",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert "secret123" not in record.msg
