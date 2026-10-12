"""
Sistema de logging estruturado para melhor observabilidade.
Usa formato JSON para facilitar análise e monitoramento.
"""

import json
import logging
import sys
import traceback
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from typing import ClassVar


class StructuredFormatter(logging.Formatter):
    """Formatter que produz logs em formato JSON estruturado"""

    def format(self, record: logging.LogRecord) -> str:
        """Formata log record como JSON"""
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adiciona contexto extra se disponível
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "action"):
            log_data["action"] = record.action

        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        # Adiciona stack trace se for erro
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Adiciona campos extras genéricos
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]
        }

        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data, ensure_ascii=False, default=str)


class SensitiveDataFilter(logging.Filter):
    """Filtro para remover dados sensíveis dos logs"""

    SENSITIVE_FIELDS = (
        "password",
        "senha",
        "token",
        "secret",
        "api_key",
        "credential",
        "auth",
        "ssn",
        "cpf",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        """Filtra dados sensíveis do log record"""
        # Mascara mensagem se contém dados sensíveis
        message_lower = record.getMessage().lower()

        for field in self.SENSITIVE_FIELDS:
            if field in message_lower:
                # Substitui valores sensíveis por asteriscos
                record.msg = self._mask_sensitive_data(record.msg, field)

        # Mascara campos extras
        for attr_name in dir(record):
            if any(field in attr_name.lower() for field in self.SENSITIVE_FIELDS):
                setattr(record, attr_name, "***REDACTED***")

        return True

    def _mask_sensitive_data(self, text: str, field: str) -> str:
        """Mascara dados sensíveis em texto"""
        import re

        # Padrões para encontrar valores após o campo
        patterns = [
            rf'{field}\s*[:=]\s*"([^"]+)"',  # field: "value" ou field="value"
            rf"{field}\s*[:=]\s*\'([^\']+)\'",  # field: 'value' ou field='value'
            rf"{field}\s*[:=]\s*([^\s,;]+)",  # field: value ou field=value
        ]

        for pattern in patterns:
            text = re.sub(pattern, f"{field}=***REDACTED***", text, flags=re.IGNORECASE)

        return text


class StructuredLogger:
    """Logger estruturado com contexto e filtros de segurança"""

    _loggers: ClassVar[dict[str, logging.Logger]] = {}

    @classmethod
    def get_logger(
        cls, name: str, level: int = logging.INFO, log_file: str | None = None
    ) -> logging.Logger:
        """
        Obtém ou cria um logger estruturado.

        Args:
            name: Nome do logger
            level: Nível de log
            log_file: Arquivo de log opcional

        Returns:
            Logger configurado
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        # Remove handlers existentes
        logger.handlers.clear()

        # Console handler com formato estruturado
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        console_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(console_handler)

        # File handler se especificado
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(StructuredFormatter())
            file_handler.addFilter(SensitiveDataFilter())
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def log_with_context(cls, logger: logging.Logger, level: int, message: str, **context) -> None:
        """
        Loga mensagem com contexto adicional.

        Args:
            logger: Logger a usar
            level: Nível do log
            message: Mensagem
            **context: Contexto adicional
        """
        logger.log(level, message, extra=context)


def log_execution(
    logger: logging.Logger | None = None,
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator para logar execução de funções.

    Args:
        logger: Logger a usar (padrão: logger do módulo)
        level: Nível de log
        include_args: Se deve incluir argumentos
        include_result: Se deve incluir resultado
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = StructuredLogger.get_logger(func.__module__)

            # Log de entrada
            log_data = {
                "event": "function_start",
                "function": func.__name__,
            }

            if include_args:
                # Filtra argumentos sensíveis
                safe_args = [
                    (
                        arg
                        if not any(
                            s in str(arg).lower() for s in SensitiveDataFilter.SENSITIVE_FIELDS
                        )
                        else "***REDACTED***"
                    )
                    for arg in args
                ]
                safe_kwargs = {
                    k: (
                        v
                        if not any(
                            s in k.lower() or s in str(v).lower()
                            for s in SensitiveDataFilter.SENSITIVE_FIELDS
                        )
                        else "***REDACTED***"
                    )
                    for k, v in kwargs.items()
                }

                log_data["args"] = safe_args
                log_data["kwargs"] = safe_kwargs

            logger.log(level, f"Starting {func.__name__}", extra=log_data)

            try:
                # Executa função
                result = func(*args, **kwargs)

                # Log de sucesso
                log_data = {"event": "function_end", "function": func.__name__, "status": "success"}

                if include_result:
                    # Filtra resultado sensível
                    safe_result = result
                    if any(s in str(result).lower() for s in SensitiveDataFilter.SENSITIVE_FIELDS):
                        safe_result = "***REDACTED***"

                    log_data["result"] = safe_result

                logger.log(level, f"Completed {func.__name__}", extra=log_data)

                return result

            except Exception as e:
                # Log de erro
                logger.error(
                    f"Error in {func.__name__}: {e!s}",
                    exc_info=True,
                    extra={
                        "event": "function_error",
                        "function": func.__name__,
                        "status": "error",
                        "error_type": type(e).__name__,
                    },
                )
                raise

        return wrapper

    return decorator


# Logger padrão da aplicação
app_logger = StructuredLogger.get_logger(
    "ozempic_seguro", level=logging.INFO, log_file="logs/ozempic_seguro.json"
)


# Funções de conveniência
def log_info(message: str, **context):
    """Log de informação com contexto"""
    StructuredLogger.log_with_context(app_logger, logging.INFO, message, **context)


def log_warning(message: str, **context):
    """Log de warning com contexto"""
    StructuredLogger.log_with_context(app_logger, logging.WARNING, message, **context)


def log_error(message: str, **context):
    """Log de erro com contexto"""
    StructuredLogger.log_with_context(app_logger, logging.ERROR, message, **context)


def log_security_event(action: str, user_id: int | None = None, **details):
    """Log específico para eventos de segurança"""
    security_logger = StructuredLogger.get_logger(
        "ozempic_seguro.security", level=logging.INFO, log_file="logs/security.json"
    )

    StructuredLogger.log_with_context(
        security_logger,
        logging.INFO,
        f"Security event: {action}",
        action=action,
        user_id=user_id,
        ip_address="127.0.0.1",  # Sempre local
        **details,
    )
