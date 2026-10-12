"""
Testes para módulo de logging.
"""

import pytest

from ozempic_seguro.core.logger import (
    logger,
    log_exceptions,
    log_method_call,
    AppLogger,
)


class TestAppLogger:
    """Testes para AppLogger"""

    def test_logger_singleton(self):
        """Testa que logger é singleton"""
        logger1 = AppLogger()
        logger2 = AppLogger()

        assert logger1 is logger2

    def test_logger_has_methods(self):
        """Testa que logger tem métodos de log"""
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")

    def test_logger_debug(self):
        """Testa log de debug"""
        # Não deve lançar exceção
        logger.debug("Test debug message")

    def test_logger_info(self):
        """Testa log de info"""
        logger.info("Test info message")

    def test_logger_warning(self):
        """Testa log de warning"""
        logger.warning("Test warning message")

    def test_logger_error(self):
        """Testa log de error"""
        logger.error("Test error message")

    def test_logger_with_extra(self):
        """Testa log com dados extras"""
        logger.info("Test with extra", extra={"key": "value"})


class TestLogExceptionsDecorator:
    """Testes para decorator log_exceptions"""

    def test_log_exceptions_success(self):
        """Testa que função bem-sucedida retorna normalmente"""

        @log_exceptions("Test Operation")
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_log_exceptions_with_args(self):
        """Testa que argumentos são passados corretamente"""

        @log_exceptions("Test Operation")
        def function_with_args(a, b):
            return a + b

        result = function_with_args(1, 2)
        assert result == 3

    def test_log_exceptions_with_kwargs(self):
        """Testa que kwargs são passados corretamente"""

        @log_exceptions("Test Operation")
        def function_with_kwargs(a, b=10):
            return a + b

        result = function_with_kwargs(5, b=20)
        assert result == 25

    def test_log_exceptions_raises(self):
        """Testa que exceção é re-lançada após log"""

        @log_exceptions("Test Operation")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()


class TestLogMethodCallDecorator:
    """Testes para decorator log_method_call"""

    def test_log_method_call_success(self):
        """Testa que método é executado normalmente"""

        class TestClass:
            @log_method_call()
            def test_method(self):
                return "result"

        obj = TestClass()
        result = obj.test_method()
        assert result == "result"

    def test_log_method_call_with_args(self):
        """Testa que argumentos são passados"""

        class TestClass:
            @log_method_call(include_args=True)
            def method_with_args(self, x, y):
                return x * y

        obj = TestClass()
        result = obj.method_with_args(3, 4)
        assert result == 12


class TestLoggerAdditional:
    """Testes adicionais para logger"""

    def test_logger_critical(self):
        """Testa log critical"""
        logger.critical("Test critical message")

    def test_log_method_call_simple(self):
        """Testa log_method_call simples"""

        class TestClass:
            @log_method_call()
            def get_value(self):
                return 42

        obj = TestClass()
        result = obj.get_value()
        assert result == 42

    def test_log_exceptions_preserves_docstring(self):
        """Testa que docstring é preservada"""

        @log_exceptions("Test")
        def documented_function():
            """Esta é a documentação."""
            return True

        # functools.wraps preserva docstring
        assert documented_function() is True

    def test_log_method_call_exception(self):
        """Testa log_method_call com exceção"""

        class TestClass:
            @log_method_call()
            def failing_method(self):
                raise RuntimeError("Test error")

        obj = TestClass()
        with pytest.raises(RuntimeError):
            obj.failing_method()

    def test_multiple_log_calls(self):
        """Testa múltiplas chamadas de log"""
        for i in range(10):
            logger.debug(f"Debug message {i}")
            logger.info(f"Info message {i}")

    def test_logger_with_dict_extra(self):
        """Testa logger com dicionário extra complexo"""
        extra_data = {"user_id": 123, "action": "login", "details": {"ip": "127.0.0.1"}}
        logger.info("Complex log", extra=extra_data)
