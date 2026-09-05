import asyncio
from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import discord
import pytest

from impostor_bot.discord.lobby import (
    close_lobby_message,
    fetch_lobby_message,
    update_lobby_message,
)
from impostor_bot.discord.state import (
    active_lobby_messages,
)
from impostor_bot.errors.infrastructure import (
    DiscordAPIError,
)
from impostor_bot.game.session_key import (
    GameSessionKey,
)


def make_discord_error(
    error_type: type[discord.HTTPException],
    status: int,
) -> discord.HTTPException:
    response = MagicMock()
    response.status = status
    response.reason = "Test"

    return error_type(
        response,
        "Test failure",
    )


def make_key() -> GameSessionKey:
    return GameSessionKey(
        guild_id=100,
        channel_id=200,
    )


def make_client():
    return SimpleNamespace(
        get_channel=MagicMock(),
        fetch_channel=AsyncMock(),
    )


def make_channel():
    return SimpleNamespace(
        fetch_message=AsyncMock(),
    )


@pytest.fixture(autouse=True)
def clear_lobby_cache():
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


@pytest.mark.asyncio
async def test_fetch_lobby_message_returns_none_without_message_reference():
    key = make_key()
    client = make_client()

    message = await fetch_lobby_message(
        client,
        key,
    )

    assert message is None

    client.get_channel.assert_not_called()
    client.fetch_channel.assert_not_awaited()


@pytest.mark.asyncio
async def test_fetch_lobby_message_uses_cached_channel():
    key = make_key()
    client = make_client()

    message = MagicMock(
        spec=discord.Message
    )

    channel = make_channel()

    channel.fetch_message.return_value = (
        message
    )

    client.get_channel.return_value = (
        channel
    )

    active_lobby_messages[key] = 999

    result = await fetch_lobby_message(
        client,
        key,
    )

    assert result is message

    client.get_channel.assert_called_once_with(
        200
    )

    client.fetch_channel.assert_not_awaited()

    channel.fetch_message.assert_awaited_once_with(
        999
    )


@pytest.mark.asyncio
async def test_fetch_lobby_message_fetches_channel_on_cache_miss():
    key = make_key()
    client = make_client()

    message = MagicMock(
        spec=discord.Message
    )

    channel = make_channel()

    channel.fetch_message.return_value = (
        message
    )

    client.get_channel.return_value = None

    client.fetch_channel.return_value = (
        channel
    )

    active_lobby_messages[key] = 999

    result = await fetch_lobby_message(
        client,
        key,
    )

    assert result is message

    client.fetch_channel.assert_awaited_once_with(
        200
    )

    channel.fetch_message.assert_awaited_once_with(
        999
    )


@pytest.mark.asyncio
async def test_fetch_lobby_message_removes_reference_when_channel_is_not_found():
    key = make_key()
    client = make_client()

    not_found = make_discord_error(
        discord.NotFound,
        404,
    )

    client.get_channel.return_value = None

    client.fetch_channel.side_effect = (
        not_found
    )

    active_lobby_messages[key] = 999

    result = await fetch_lobby_message(
        client,
        key,
    )

    assert result is None

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (
            discord.Forbidden,
            403,
        ),
        (
            discord.HTTPException,
            500,
        ),
    ],
)
@pytest.mark.asyncio
async def test_fetch_lobby_message_translates_channel_access_error(
    error_type,
    status,
):
    key = make_key()
    client = make_client()

    discord_error = make_discord_error(
        error_type,
        status,
    )

    client.get_channel.return_value = None

    client.fetch_channel.side_effect = (
        discord_error
    )

    active_lobby_messages[key] = 999

    with pytest.raises(
        DiscordAPIError
    ) as exc_info:
        await fetch_lobby_message(
            client,
            key,
        )

    assert (
        exc_info.value.__cause__
        is discord_error
    )

    assert (
        active_lobby_messages[key]
        == 999
    )


@pytest.mark.asyncio
async def test_fetch_lobby_message_removes_reference_for_non_message_channel():
    key = make_key()
    client = make_client()

    channel = SimpleNamespace()

    client.get_channel.return_value = (
        channel
    )

    active_lobby_messages[key] = 999

    result = await fetch_lobby_message(
        client,
        key,
    )

    assert result is None

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.asyncio
async def test_fetch_lobby_message_removes_reference_when_message_is_not_found():
    key = make_key()
    client = make_client()

    channel = make_channel()

    channel.fetch_message.side_effect = (
        make_discord_error(
            discord.NotFound,
            404,
        )
    )

    client.get_channel.return_value = (
        channel
    )

    active_lobby_messages[key] = 999

    result = await fetch_lobby_message(
        client,
        key,
    )

    assert result is None

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (
            discord.Forbidden,
            403,
        ),
        (
            discord.HTTPException,
            500,
        ),
    ],
)
@pytest.mark.asyncio
async def test_fetch_lobby_message_translates_message_access_error(
    error_type,
    status,
):
    key = make_key()
    client = make_client()

    discord_error = make_discord_error(
        error_type,
        status,
    )

    channel = make_channel()

    channel.fetch_message.side_effect = (
        discord_error
    )

    client.get_channel.return_value = (
        channel
    )

    active_lobby_messages[key] = 999

    with pytest.raises(
        DiscordAPIError
    ) as exc_info:
        await fetch_lobby_message(
            client,
            key,
        )

    assert (
        exc_info.value.__cause__
        is discord_error
    )

    assert (
        active_lobby_messages[key]
        == 999
    )


@pytest.mark.asyncio
async def test_update_lobby_message_removes_reference_when_message_disappears():
    key = make_key()

    client = make_client()

    view = MagicMock(
        spec=discord.ui.View
    )

    message = MagicMock(
        spec=discord.Message
    )

    message.edit = AsyncMock(
        side_effect=make_discord_error(
            discord.NotFound,
            404,
        )
    )

    active_lobby_messages[key] = 999

    with patch(
        "impostor_bot.discord.lobby."
        "fetch_lobby_message",
        new=AsyncMock(
            return_value=message
        ),
    ):
        await update_lobby_message(
            client=client,
            key=key,
            content="updated",
            view=view,
        )

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (
            discord.Forbidden,
            403,
        ),
        (
            discord.HTTPException,
            500,
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_lobby_message_translates_edit_error(
    error_type,
    status,
):
    key = make_key()

    client = make_client()

    view = MagicMock(
        spec=discord.ui.View
    )

    discord_error = make_discord_error(
        error_type,
        status,
    )

    message = MagicMock(
        spec=discord.Message
    )

    message.edit = AsyncMock(
        side_effect=discord_error
    )

    active_lobby_messages[key] = 999

    with patch(
        "impostor_bot.discord.lobby."
        "fetch_lobby_message",
        new=AsyncMock(
            return_value=message
        ),
    ):
        with pytest.raises(
            DiscordAPIError
        ) as exc_info:
            await update_lobby_message(
                client=client,
                key=key,
                content="updated",
                view=view,
            )

    assert (
        exc_info.value.__cause__
        is discord_error
    )

    assert (
        active_lobby_messages[key]
        == 999
    )


@pytest.mark.asyncio
async def test_close_lobby_message_removes_reference_when_message_is_missing():
    key = make_key()

    client = make_client()

    view = MagicMock(
        spec=discord.ui.View
    )

    active_lobby_messages[key] = 999

    with patch(
        "impostor_bot.discord.lobby."
        "fetch_lobby_message",
        new=AsyncMock(
            return_value=None
        ),
    ):
        await close_lobby_message(
            client=client,
            key=key,
            content="closed",
            view=view,
        )

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.asyncio
async def test_close_lobby_message_removes_reference_when_message_disappears():
    key = make_key()

    client = make_client()

    view = MagicMock(
        spec=discord.ui.View
    )

    message = MagicMock(
        spec=discord.Message
    )

    message.edit = AsyncMock(
        side_effect=make_discord_error(
            discord.NotFound,
            404,
        )
    )

    active_lobby_messages[key] = 999

    with patch(
        "impostor_bot.discord.lobby."
        "fetch_lobby_message",
        new=AsyncMock(
            return_value=message
        ),
    ):
        await close_lobby_message(
            client=client,
            key=key,
            content="closed",
            view=view,
        )

    assert (
        key
        not in active_lobby_messages
    )


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (
            discord.Forbidden,
            403,
        ),
        (
            discord.HTTPException,
            500,
        ),
    ],
)
@pytest.mark.asyncio
async def test_close_lobby_message_translates_edit_error(
    error_type,
    status,
):
    key = make_key()

    client = make_client()

    view = MagicMock(
        spec=discord.ui.View
    )

    discord_error = make_discord_error(
        error_type,
        status,
    )

    message = MagicMock(
        spec=discord.Message
    )

    message.edit = AsyncMock(
        side_effect=discord_error
    )

    active_lobby_messages[key] = 999

    with patch(
        "impostor_bot.discord.lobby."
        "fetch_lobby_message",
        new=AsyncMock(
            return_value=message
        ),
    ):
        with pytest.raises(
            DiscordAPIError
        ) as exc_info:
            await close_lobby_message(
                client=client,
                key=key,
                content="closed",
                view=view,
            )

    assert (
        exc_info.value.__cause__
        is discord_error
    )

    assert (
        active_lobby_messages[key]
        == 999
    )