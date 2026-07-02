import discord

from impostor_bot.discord.messages import build_game_created_message
from impostor_bot.discord.state import active_games, active_lobby_messages
from impostor_bot.game.exceptions import GameError


def join_lobby(channel_id: int, player_id: int):
    game = active_games.get(channel_id)

    if game is None:
        raise GameError("There is no open game in this channel.")

    if player_id == game.host_id:
        raise GameError("You are the host and you are already part of this game.")

    game.add_player(player_id)

    return game


def leave_lobby(channel_id: int, player_id: int):
    game = active_games.get(channel_id)

    if game is None:
        raise GameError("There is no open game in this channel.")

    game.remove_player(player_id)

    return game


async def fetch_lobby_message(
    client: discord.Client,
    channel_id: int,
) -> discord.Message | None:
    message_id = active_lobby_messages.get(channel_id)

    if message_id is None:
        return None

    channel = client.get_channel(channel_id)

    if channel is None:
        channel = await client.fetch_channel(channel_id)

    if not hasattr(channel, "fetch_message"):
        return None

    try:
        return await channel.fetch_message(message_id)

    except discord.NotFound:
        active_lobby_messages.pop(channel_id, None)
        return None

    except discord.Forbidden:
        return None


async def refresh_lobby_message(
    client: discord.Client,
    channel_id: int,
    view: discord.ui.View,
) -> None:
    game = active_games.get(channel_id)

    if game is None:
        return

    message = await fetch_lobby_message(client, channel_id)

    if message is None:
        return

    await message.edit(
        content=build_game_created_message(game),
        view=view,
    )


async def close_lobby_message(
    client: discord.Client,
    channel_id: int,
    content: str,
    view: discord.ui.View,
) -> None:
    message = await fetch_lobby_message(client, channel_id)

    if message is None:
        active_lobby_messages.pop(channel_id, None)
        return

    await message.edit(
        content=content,
        view=view,
    )

    active_lobby_messages.pop(channel_id, None)