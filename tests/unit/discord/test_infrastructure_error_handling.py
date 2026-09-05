import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from impostor_bot.discord.error_handling import (
    handle_known_error,
    handle_unexpected_error,
)
from impostor_bot.errors import (
    DatabaseError,
)
from impostor_bot.errors.infrastructure import (
    DatabaseUnavailableError,
)


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

def make_responded_interaction():
    return SimpleNamespace(
        id=1000,
        guild_id=100,
        channel_id=200,
        response=SimpleNamespace(
            is_done=lambda: True,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )

def create_interaction():
    return SimpleNamespace(
        id=500,
        guild_id=100,
        channel_id=200,
        channel=SimpleNamespace(
            id=200,
        ),
        response=SimpleNamespace(
            is_done=lambda: False,
            send_message=AsyncMock(),
        ),
        followup=SimpleNamespace(
            send=AsyncMock(),
        ),
    )


@pytest.mark.asyncio
async def test_infrastructure_error_does_not_expose_internal_message():
    interaction = make_interaction()

    error = DatabaseUnavailableError(
        "postgresql://admin:secret-password"
        "@production-db.example.com/impostor"
    )

    await handle_known_error(
        interaction,
        error,
        operation="status",
    )

    interaction.response.send_message.assert_awaited_once()

    sent_message = (
        interaction.response
        .send_message
        .call_args.args[0]
    )

    assert "secret-password" not in sent_message
    assert "postgresql" not in sent_message
    assert "production-db" not in sent_message
    assert "admin" not in sent_message


@pytest.mark.asyncio
async def test_infrastructure_error_returns_safe_service_message():
    interaction = make_interaction()

    await handle_known_error(
        interaction,
        DatabaseUnavailableError(
            "sensitive internal message"
        ),
        operation="status",
    )

    sent_message = (
        interaction.response
        .send_message
        .call_args.args[0]
    )

    assert sent_message
    assert isinstance(
        sent_message,
        str,
    )


@pytest.mark.asyncio
async def test_infrastructure_error_uses_followup_when_interaction_is_done():
    interaction = (
        make_responded_interaction()
    )

    await handle_known_error(
        interaction,
        DatabaseUnavailableError(
            "internal"
        ),
        operation="status",
    )

    interaction.response.send_message.assert_not_awaited()

    interaction.followup.send.assert_awaited_once()


def test_database_error_is_logged_and_returns_safe_response(
    caplog,
):
    interaction = create_interaction()

    error = DatabaseError(
        "postgresql+asyncpg://user:"
        "SECRET@localhost/database"
    )

    caplog.set_level(logging.ERROR)

    asyncio.run(
        handle_known_error(
            interaction,
            error,
            operation="status",
        )
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

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200

    interaction.response.send_message.assert_awaited_once()

    sent_message = (
        interaction
        .response
        .send_message
        .await_args
        .args[0]
    )

    assert "SECRET" not in sent_message
    assert "postgresql" not in sent_message


def test_unexpected_error_is_logged_and_returns_safe_response(
    caplog,
):
    interaction = create_interaction()

    error = RuntimeError(
        "unexpected internal bug"
    )

    caplog.set_level(logging.ERROR)

    asyncio.run(
        handle_unexpected_error(
            interaction,
            error,
        )
    )

    record = next(
        record
        for record in caplog.records
        if getattr(
            record,
            "event",
            None,
        )
        == "unexpected_error"
    )

    assert record.levelno == logging.ERROR
    assert record.exc_info is not None

    assert record.context[
        "guild_id"
    ] == 100

    assert record.context[
        "channel_id"
    ] == 200

    interaction.response.send_message.assert_awaited_once()

    sent_message = (
        interaction
        .response
        .send_message
        .await_args
        .args[0]
    )

    assert (
        "unexpected internal bug"
        not in sent_message
    )