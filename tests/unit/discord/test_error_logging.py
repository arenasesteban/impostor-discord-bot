import logging
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import pytest

from impostor_bot.discord.error_handling import (
    handle_known_error,
    handle_unexpected_error,
)
from impostor_bot.errors import (
    DatabaseError,
)


def create_interaction_mock() -> MagicMock:
    interaction = MagicMock()

    interaction.id = 1000
    interaction.guild_id = 2000
    interaction.channel_id = 3000

    return interaction


def make_interaction():
    return SimpleNamespace(
        id=1000,
        guild_id=100,
        channel_id=200,
        response=SimpleNamespace(
            is_done=lambda: False,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )


@pytest.mark.asyncio
async def test_known_database_error_is_not_double_logged(
    caplog: pytest.LogCaptureFixture,
):
    interaction = (
        create_interaction_mock()
    )

    error = DatabaseError(
        "Database operation failed."
    )

    caplog.set_level(
        logging.ERROR,
        logger=(
            "impostor_bot.discord."
            "error_handling"
        ),
    )

    send_error_mock = AsyncMock()

    with patch(
        "impostor_bot.discord.error_handling.send_error",
        new=send_error_mock,
    ):
        await handle_known_error(
            interaction,
            error,
            operation="status",
        )

    database_records = [
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "database_error"
    ]

    unexpected_records = [
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "unexpected_error"
    ]

    assert len(
        database_records
    ) == 1

    assert (
        database_records[0].levelno
        == logging.ERROR
    )

    assert (
        database_records[0].exc_info
        is not None
    )

    assert (
        unexpected_records
        == []
    )

    send_error_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_unexpected_error_is_logged_safely(
    caplog: pytest.LogCaptureFixture,
):
    interaction = make_interaction()

    error = RuntimeError(
        "Authorization: "
        "Bearer abc123-super-secret"
    )

    caplog.set_level(
        logging.ERROR
    )

    await handle_unexpected_error(
        interaction,
        error,
    )

    records = [
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        ) == "unexpected_error"
    ]

    assert len(records) == 1
    assert records[0].exc_info is not None