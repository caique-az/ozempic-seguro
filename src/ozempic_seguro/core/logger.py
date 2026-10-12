"""
Sistema de logging estruturado para toda a aplicação
"""

import logging
import sys
from datetime import datetime
from functools import wraps
from typing import Any

from ..paths import LOGS_DIR


class AppLogger:
    """Sistema de logging centralizado e estruturado"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Configura o logger principal"""
        # Criar diretório de logs na raiz do projeto (não em src/)
        log_dir = LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configurar logger
        self._logger = logging.getLogger("ozempic_seguro")
        self._logger.setLevel(logging.DEBUG)

        # Evitar duplicação de handlers
        if not self._logger.handlers:
            # Handler para arquivo
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)

            # Handler para console (apenas erros críticos)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.ERROR)

            # Formatador estruturado
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def debug(self, message: str, extra: dict[str, Any] | None = None):
        """Log de debug"""
        self._log_with_context(logging.DEBUG, message, extra)

    def info(self, message: str, extra: dict[str, Any] | None = None):
        """Log informativo"""
        self._log_with_context(logging.INFO, message, extra)

    def warning(self, message: str, extra: dict[str, Any] | None = None):
        """Log de aviso"""
        self._log_with_context(logging.WARNING, message, extra)

    def error(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool = True):
        """Log de erro"""
        self._log_with_context(logging.ERROR, message, extra, exc_info)

    def critical(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool = True):
        """Log crítico"""
        self._log_with_context(logging.CRITICAL, message, extra, exc_info)

    def _log_with_context(
        self,
        level: int,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ):
        """Log com contexto adicional"""
        context_msg = message
        if extra:
            context_items = [f"{k}={v}" for k, v in extra.items()]
            context_msg = f"{message} | Context: {', '.join(context_items)}"

        self._logger.log(level, context_msg, exc_info=exc_info)


# Instância global do logger
logger = AppLogger()


def log_exceptions(operation_name: str = "Unknown Operation"):
    """
    Decorator para capturar e logar exceções automaticamente

    Args:
        operation_name: Nome da operação para contexto do log

    Usage:
        @log_exceptions("User Creation")
        def create_user(username, password):
            # código que pode gerar exceção
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {operation_name} ({func.__name__}): {e!s}",
                    extra={
                        "function": func.__name__,
                        "operation": operation_name,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                    },
                )
                raise  # Re-lança a exceção para manter o comportamento original

        return wrapper

    return decorator


def log_method_call(include_args: bool = False):
    """
    Decorator para logar chamadas de métodos

    Args:
        include_args: Se deve incluir argumentos no log
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__ if args else "Unknown"

            extra_context = {"class": class_name, "method": func.__name__}

            if include_args and len(args) > 1:
                extra_context["args"] = str(args[1:])[:100]  # Limita tamanho

            logger.debug(f"Method call: {class_name}.{func.__name__}", extra=extra_context)

            try:
                result = func(*args, **kwargs)
                logger.debug(f"Method success: {class_name}.{func.__name__}", extra=extra_context)
                return result
            except Exception as e:
                logger.error(
                    f"Method failed: {class_name}.{func.__name__}: {e!s}", extra=extra_context
                )
                raise

        return wrapper

    return decorator
