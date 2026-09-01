import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from impostor_bot.discord.lobby import (
    close_lobby_message,
    update_lobby_message,
)
from impostor_bot.discord.state import (
    active_lobby_messages,
)
from impostor_bot.game.session_key import GameSessionKey


@pytest.fixture(autouse=True)
def clear_lobby_message_cache():
    active_lobby_messages.clear()

    yield

    active_lobby_messages.clear()


def test_update_lobby_message_preserves_message_reference():
    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    message_id = 999

    active_lobby_messages[key] = message_id

    message = SimpleNamespace(
        edit=AsyncMock(),
    )

    client = SimpleNamespace()

    view = SimpleNamespace()

    with patch(
        "impostor_bot.discord.lobby.fetch_lobby_message",
        new=AsyncMock(
            return_value=message,
        ),
    ):
        asyncio.run(
            update_lobby_message(
                client=client,
                key=key,
                content="Game started",
                view=view,
            )
        )

    message.edit.assert_awaited_once_with(
        content="Game started",
        view=view,
    )

    assert active_lobby_messages[key] == message_id


def test_close_lobby_message_removes_message_reference():
    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    message_id = 999

    active_lobby_messages[key] = message_id

    message = SimpleNamespace(
        edit=AsyncMock(),
    )

    client = SimpleNamespace()

    view = SimpleNamespace()

    with patch(
        "impostor_bot.discord.lobby.fetch_lobby_message",
        new=AsyncMock(
            return_value=message,
        ),
    ):
        asyncio.run(
            close_lobby_message(
                client=client,
                key=key,
                content="Game finished",
                view=view,
            )
        )

    message.edit.assert_awaited_once_with(
        content="Game finished",
        view=view,
    )

    assert key not in active_lobby_messages