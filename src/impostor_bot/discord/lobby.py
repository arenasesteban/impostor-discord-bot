import discord

from impostor_bot.discord.messages import build_game_created_message
from impostor_bot.discord.state import active_lobby_messages
from impostor_bot.game.game import Game


async def fetch_lobby_message(client: discord.Client, channel_id: int) -> discord.Message | None:
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


async def refresh_lobby_message(client: discord.Client, channel_id: int, game: Game, view: discord.ui.View) -> None:
    message = await fetch_lobby_message(client, channel_id)

    if message is None:
        return

    await message.edit(
        content=build_game_created_message(game),
        view=view,
    )


async def close_lobby_message(client: discord.Client, channel_id: int, content: str, view: discord.ui.View) -> None:
    message = await fetch_lobby_message(client, channel_id)

    if message is None:
        active_lobby_messages.pop(channel_id, None)
        return

    await message.edit(
        content=content,
        view=view,
    )

    active_lobby_messages.pop(channel_id, None)