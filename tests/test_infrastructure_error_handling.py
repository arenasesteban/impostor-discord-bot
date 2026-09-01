from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from impostor_bot.discord.error_handling import (
    handle_infrastructure_error,
)
from impostor_bot.errors.infrastructure import (
    DatabaseUnavailableError,
)


def make_interaction():
    return SimpleNamespace(
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
        response=SimpleNamespace(
            is_done=lambda: True,
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

    await handle_infrastructure_error(
        interaction,
        error,
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

    await handle_infrastructure_error(
        interaction,
        DatabaseUnavailableError(
            "sensitive internal message"
        ),
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

    await handle_infrastructure_error(
        interaction,
        DatabaseUnavailableError(
            "internal"
        ),
    )

    interaction.response.send_message.assert_not_awaited()

    interaction.followup.send.assert_awaited_once()