import json
import logging

from typing import Any
from datetime import (
    UTC,
    datetime
)

from impostor_bot.observability.sanitization import (
    redact_string,
    sanitize_value
)


class JsonFormatter(logging.Formatter):
    def __init__(self, *, sensitive_values: tuple[str, ...] = ()) -> None:
        super().__init__()

        self._sensitive_values = sensitive_values

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=UTC,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": sanitize_value(
                getattr(record, "event", record.getMessage()),
                sensitive_values=self._sensitive_values
            )
        }

        context = getattr(record, "context", None)

        if context:
            payload["context"] = (
                sanitize_value(
                    context,
                    sensitive_values=self._sensitive_values
                )
            )

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info

            traceback_text = self.formatException(record.exc_info)

            payload["exception"] = {
                "type":  exc_type.__name__,
                "message": redact_string(str(exc_value), self._sensitive_values),
                "traceback": redact_string(traceback_text, self._sensitive_values)
            }

        return json.dumps(
            payload,
            ensure_ascii=False
        )


def configure_logging(*, level: int = logging.INFO, sensitive_values: tuple[str, ...] = ()) -> None:
    root_logger = logging.getLogger()

    for handler in tuple(root_logger.handlers):
        root_logger.removeHandler(handler)

        handler.close()

    handler = logging.StreamHandler()

    handler.setLevel(level)

    handler.setFormatter(
        JsonFormatter(
            sensitive_values=sensitive_values
        )
    )

    root_logger.addHandler(handler)

    root_logger.setLevel(level)


def log_event(logger: logging.Logger, event: str, *, level: int = logging.INFO, **context: object) -> None:
    logger.log(
        level,
        event,
        extra={
            "event": event,
            "context": context
        }
    )


def log_error(logger: logging.Logger, event: str, error: BaseException, *, level: int = logging.ERROR, **context: object) -> None:
    logger.log(
        level,
        event,
        extra={
            "event": event,
            "context": context
        },
        exc_info=(
            type(error),
            error,
            error.__traceback__
        )
    )
