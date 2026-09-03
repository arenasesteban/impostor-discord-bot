import io
import json
import logging

import pytest

from impostor_bot.observability.logging import (
    JsonFormatter,
    configure_logging,
    log_error,
    log_event,
)


def create_isolated_logger(
    formatter: logging.Formatter,
) -> tuple[logging.Logger, io.StringIO]:
    stream = io.StringIO()

    handler = logging.StreamHandler(
        stream
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(
        f"test.logging.{id(stream)}"
    )
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger, stream


def read_log_output(
    stream: io.StringIO,
) -> tuple[str, dict]:
    output = stream.getvalue().strip()

    return output, json.loads(output)


def test_sensitive_context_is_redacted():
    formatter = JsonFormatter(
        sensitive_values=(
            "super-secret-token",
        )
    )

    logger, stream = create_isolated_logger(
        formatter
    )

    log_event(
        logger,
        "test_event",
        discord_token="super-secret-token",
        secret_word="pizza",
        password="hunter2",
    )

    output, payload = read_log_output(
        stream
    )

    assert "super-secret-token" not in output
    assert "pizza" not in output
    assert "hunter2" not in output

    assert payload["context"] == {
        "discord_token": "[REDACTED]",
        "secret_word": "[REDACTED]",
        "password": "[REDACTED]",
    }


def test_postgresql_url_credentials_are_redacted():
    database_url = (
        "postgresql+asyncpg://"
        "user:hunter2@localhost:5432/db"
    )

    formatter = JsonFormatter()

    logger, stream = create_isolated_logger(
        formatter
    )

    log_event(
        logger,
        "database_connection_failed",
        database_url=database_url,
        detail=(
            f"Could not connect to "
            f"{database_url}"
        ),
    )

    output, payload = read_log_output(
        stream
    )

    assert "hunter2" not in output
    assert database_url not in output

    assert (
        payload["context"]["database_url"]
        == "[REDACTED]"
    )

    assert "[REDACTED]" in (
        payload["context"]["detail"]
    )


def test_bearer_token_inside_exception_is_redacted():
    formatter = JsonFormatter()

    logger, stream = create_isolated_logger(
        formatter
    )

    try:
        raise RuntimeError(
            "Authorization: "
            "Bearer abc123-super-secret"
        )

    except RuntimeError as error:
        log_error(
            logger,
            "unexpected_error",
            error,
        )

    output, payload = read_log_output(
        stream
    )

    assert (
        "abc123-super-secret"
        not in output
    )

    assert "[REDACTED]" in output

    assert (
        payload["exception"]["type"]
        == "RuntimeError"
    )

    assert (
        "abc123-super-secret"
        not in payload["exception"][
            "message"
        ]
    )

    assert (
        "Traceback"
        in payload["exception"][
            "traceback"
        ]
    )

    assert (
        "RuntimeError"
        in payload["exception"][
            "traceback"
        ]
    )


class DangerousObject:
    def __str__(self) -> str:
        return "super-secret-token"


def test_arbitrary_objects_do_not_use_str():
    formatter = JsonFormatter(
        sensitive_values=(
            "super-secret-token",
        )
    )

    logger, stream = create_isolated_logger(
        formatter
    )

    log_event(
        logger,
        "test_event",
        object=DangerousObject(),
    )

    output, payload = read_log_output(
        stream
    )

    assert (
        "super-secret-token"
        not in output
    )

    assert (
        payload["context"]["object"]
        == "<DangerousObject>"
    )


def test_logging_configuration_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
):
    root_logger = logging.Logger(
        "isolated-root"
    )

    original_get_logger = (
        logging.getLogger
    )

    def fake_get_logger(
        name: str | None = None,
    ) -> logging.Logger:
        if name is None:
            return root_logger

        return original_get_logger(
            name
        )

    monkeypatch.setattr(
        logging,
        "getLogger",
        fake_get_logger,
    )

    configure_logging()
    configure_logging()

    assert len(
        root_logger.handlers
    ) == 1

    assert isinstance(
        root_logger.handlers[0],
        logging.StreamHandler,
    )

    assert isinstance(
        root_logger.handlers[0].formatter,
        JsonFormatter,
    )