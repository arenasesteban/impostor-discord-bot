import json
import logging
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", record.getMessage())
        }

        context = getattr(record, "context", None)

        if context:
            payload["context"] = context

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str
        )


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()

    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    **context: object
) -> None:
    logger.log(
        level,
        event,
        extra={
            "event": event,
            "context": context
        },
    )


def log_error(
    logger: logging.Logger,
    event: str,
    error: BaseException,
    **context: object
) -> None:
    logger.error(
        event,
        extra={
            "event": event,
            "context": context
        },
        exc_info=(
            type(error),
            error,
            error.__traceback__
        ),
    )
