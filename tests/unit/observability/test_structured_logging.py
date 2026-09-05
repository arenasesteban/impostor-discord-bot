import json
import logging

from impostor_bot.observability.logging import (
    JsonFormatter,
    log_error,
    log_event,
)


def test_json_formatter_produces_structured_log():
    record = logging.LogRecord(
        name="impostor_bot.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="game_created",
        args=(),
        exc_info=None,
    )

    record.event = "game_created"
    record.context = {
        "guild_id": 100,
        "channel_id": 200,
    }

    formatter = JsonFormatter()

    payload = json.loads(
        formatter.format(record)
    )

    assert payload["level"] == "INFO"
    assert payload["logger"] == "impostor_bot.test"
    assert payload["event"] == "game_created"

    assert payload["context"] == {
        "guild_id": 100,
        "channel_id": 200,
    }

    assert "timestamp" in payload


def test_log_event_includes_context(caplog):
    logger = logging.getLogger(
        "tests.structured_logging.event"
    )

    caplog.set_level(
        logging.INFO,
        logger=logger.name,
    )

    log_event(
        logger,
        "game_created",
        guild_id=100,
        channel_id=200,
    )

    record = next(
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "game_created"
    )

    assert record.levelno == logging.INFO

    assert record.context == {
        "guild_id": 100,
        "channel_id": 200,
    }


def test_log_error_preserves_exception_info(
    caplog,
):
    logger = logging.getLogger(
        "tests.structured_logging.error"
    )

    caplog.set_level(
        logging.ERROR,
        logger=logger.name,
    )

    try:
        raise RuntimeError(
            "database exploded"
        )

    except RuntimeError as error:
        log_error(
            logger,
            "database_error",
            error,
            guild_id=100,
        )

    record = next(
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "database_error"
    )

    assert record.levelno == logging.ERROR
    assert record.exc_info is not None

    assert record.context == {
        "guild_id": 100,
    }