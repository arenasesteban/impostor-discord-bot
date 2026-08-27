import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from impostor_bot.discord.lobby import (
    close_lobby_message,
    update_lobby_message,
)
from impostor_bot.discord.state import active_lobby_messages


def test_update_lobby_message_preserves_message_reference():
    channel_id = 200
    message_id = 999

    active_lobby_messages[channel_id] = message_id

    message = SimpleNamespace(
        edit=AsyncMock(),
    )

    client = SimpleNamespace()

    with patch(
        "impostor_bot.discord.lobby.fetch_lobby_message",
        new=AsyncMock(
            return_value=message,
        ),
    ):
        asyncio.run(
            update_lobby_message(
                client=client,
                channel_id=channel_id,
                content="Game started",
                view=SimpleNamespace(),
            )
        )

    message.edit.assert_awaited_once()

    assert active_lobby_messages[channel_id] == message_id

    active_lobby_messages.pop(
        channel_id,
        None,
    )


def test_close_lobby_message_removes_message_reference():
    channel_id = 200
    message_id = 999

    active_lobby_messages[channel_id] = message_id

    message = SimpleNamespace(
        edit=AsyncMock(),
    )

    client = SimpleNamespace()

    with patch(
        "impostor_bot.discord.lobby.fetch_lobby_message",
        new=AsyncMock(
            return_value=message,
        ),
    ):
        asyncio.run(
            close_lobby_message(
                client=client,
                channel_id=channel_id,
                content="Game finished",
                view=SimpleNamespace(),
            )
        )

    message.edit.assert_awaited_once()

    assert channel_id not in active_lobby_messages