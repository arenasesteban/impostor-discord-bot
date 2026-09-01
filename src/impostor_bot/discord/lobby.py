import discord

from impostor_bot.discord.messages import build_game_created_message
from impostor_bot.discord.state import active_lobby_messages
from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey


async def fetch_lobby_message(client: discord.Client, key: GameSessionKey) -> discord.Message | None:
    message_id = active_lobby_messages.get(key)

    if message_id is None:
        return None

    channel = client.get_channel(key.channel_id)

    if channel is None:
        channel = await client.fetch_channel(key.channel_id)

    if not hasattr(channel, "fetch_message"):
        return None

    try:
        return await channel.fetch_message(message_id)

    except discord.NotFound:
        active_lobby_messages.pop(key, None)
        return None

    except discord.Forbidden:
        return None



async def update_lobby_message(client: discord.Client, key: GameSessionKey, content: str, view: discord.ui.View) -> None:
    message = await fetch_lobby_message(client, key)

    if message is None:
        return

    await message.edit(
        content=content,
        view=view,
    )



async def refresh_lobby_message(client: discord.Client, key: GameSessionKey, game: Game, view: discord.ui.View) -> None:
    await update_lobby_message(
        client=client,
        key=key,
        content=build_game_created_message(game),
        view=view,
    )


async def close_lobby_message(client: discord.Client, key: GameSessionKey, content: str, view: discord.ui.View) -> None:
    message = await fetch_lobby_message(client, key)

    if message is None:
        active_lobby_messages.pop(key, None)
        return

    await message.edit(
        content=content,
        view=view,
    )

    active_lobby_messages.pop(key, None)