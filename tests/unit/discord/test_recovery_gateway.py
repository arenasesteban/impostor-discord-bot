from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

import discord
import pytest

from impostor_bot.discord.recovery_gateway import (
    DiscordPySessionRecoveryGateway,
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


def make_client():
    client = MagicMock(
        spec=discord.Client
    )

    client.get_channel = MagicMock()
    client.fetch_channel = AsyncMock()
    client.add_view = MagicMock()

    return client


def make_text_channel(
    guild_id: int,
):
    channel = MagicMock(
        spec=discord.TextChannel
    )

    channel.guild = SimpleNamespace(
        id=guild_id
    )

    channel.fetch_message = AsyncMock()

    return channel


def make_key() -> GameSessionKey:
    return GameSessionKey(
        guild_id=100,
        channel_id=200,
    )


@pytest.mark.asyncio
async def test_channel_exists_uses_cached_channel():
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=100
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = await gateway.channel_exists(
        key
    )

    assert exists is True

    client.get_channel.assert_called_once_with(
        200
    )

    client.fetch_channel.assert_not_awaited()


@pytest.mark.asyncio
async def test_channel_exists_fetches_channel_on_cache_miss():
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=100
    )

    client.get_channel.return_value = None

    client.fetch_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = await gateway.channel_exists(
        key
    )

    assert exists is True

    client.fetch_channel.assert_awaited_once_with(
        200
    )


@pytest.mark.asyncio
async def test_channel_exists_returns_false_when_channel_is_not_found():
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

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = await gateway.channel_exists(
        key
    )

    assert exists is False


@pytest.mark.asyncio
async def test_channel_exists_returns_false_for_different_guild():
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=999
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = await gateway.channel_exists(
        key
    )

    assert exists is False


@pytest.mark.asyncio
async def test_channel_exists_returns_false_for_non_messageable_channel():
    key = make_key()
    client = make_client()

    channel = SimpleNamespace(
        guild=SimpleNamespace(
            id=100
        )
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = await gateway.channel_exists(
        key
    )

    assert exists is False


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
async def test_channel_exists_translates_discord_access_error(
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

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    with pytest.raises(
        DiscordAPIError
    ) as exc_info:
        await gateway.channel_exists(
            key
        )

    assert (
        exc_info.value.__cause__
        is discord_error
    )


@pytest.mark.asyncio
async def test_lobby_message_exists_returns_true_for_existing_message():
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=100
    )

    channel.fetch_message.return_value = (
        object()
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = (
        await gateway.lobby_message_exists(
            key,
            999,
        )
    )

    assert exists is True

    channel.fetch_message.assert_awaited_once_with(
        999
    )


@pytest.mark.asyncio
async def test_lobby_message_exists_returns_false_when_channel_is_missing():
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

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = (
        await gateway.lobby_message_exists(
            key,
            999,
        )
    )

    assert exists is False


@pytest.mark.asyncio
async def test_lobby_message_exists_returns_false_when_message_is_not_found():
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=100
    )

    message_error = make_discord_error(
        discord.NotFound,
        404,
    )

    channel.fetch_message.side_effect = (
        message_error
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    exists = (
        await gateway.lobby_message_exists(
            key,
            999,
        )
    )

    assert exists is False


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
async def test_lobby_message_exists_translates_discord_access_error(
    error_type,
    status,
):
    key = make_key()
    client = make_client()

    channel = make_text_channel(
        guild_id=100
    )

    discord_error = make_discord_error(
        error_type,
        status,
    )

    channel.fetch_message.side_effect = (
        discord_error
    )

    client.get_channel.return_value = (
        channel
    )

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    with pytest.raises(
        DiscordAPIError
    ) as exc_info:
        await gateway.lobby_message_exists(
            key,
            999,
        )

    assert (
        exc_info.value.__cause__
        is discord_error
    )


def test_register_lobby_view_is_idempotent():
    client = make_client()

    gateway = (
        DiscordPySessionRecoveryGateway(
            client
        )
    )

    view = object()

    with patch(
        "impostor_bot.discord."
        "recovery_gateway.LobbyView",
        return_value=view,
    ) as lobby_view:
        gateway.register_lobby_view(
            999
        )

        gateway.register_lobby_view(
            999
        )

    lobby_view.assert_called_once_with()

    client.add_view.assert_called_once_with(
        view,
        message_id=999,
    )