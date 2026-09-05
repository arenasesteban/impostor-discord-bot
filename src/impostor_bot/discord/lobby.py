import discord

from impostor_bot.discord.state import active_lobby_messages
from impostor_bot.discord.messages import build_game_created_message

from impostor_bot.game.game import Game
from impostor_bot.game.session_key import GameSessionKey

from impostor_bot.errors.infrastructure import DiscordAPIError


async def fetch_lobby_message(client: discord.Client, key: GameSessionKey) -> discord.Message | None:
    message_id = active_lobby_messages.get(key)

    if message_id is None:
        return None

    channel = client.get_channel(key.channel_id)


    if channel is None:
        try:
            channel = await client.fetch_channel(key.channel_id)

        except discord.NotFound:
            active_lobby_messages.pop(key, None)
            return None

        except (discord.Forbidden, discord.HTTPException) as error:
            raise DiscordAPIError(
                "Discord lobby channel could not be accessed."
            ) from error

    if not hasattr(channel, "fetch_message"):
        active_lobby_messages.pop(key, None)
        return None

    try:
        return await channel.fetch_message(message_id)

    except discord.NotFound:
        active_lobby_messages.pop(key, None)
        return None

    except (discord.Forbidden, discord.HTTPException) as error:
        raise DiscordAPIError(
            "Discord lobby message could not be accessed."
        ) from error


async def update_lobby_message(client: discord.Client, key: GameSessionKey, content: str, view: discord.ui.View) -> None:
    message = await fetch_lobby_message(client, key)

    if message is None:
        return

    try:
        await message.edit(
            content=content,
            view=view,
        )

    except discord.NotFound:
        active_lobby_messages.pop(key, None)

    except (discord.Forbidden, discord.HTTPException) as error:
        raise DiscordAPIError(
            "Discord lobby message could not be updated."
        ) from error

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

    try:
        await message.edit(
            content=content,
            view=view,
        )

    except discord.NotFound:
        active_lobby_messages.pop(key, None)
        return

    except (discord.Forbidden, discord.HTTPException) as error:
        raise DiscordAPIError(
            "Discord lobby message "
            "could not be closed."
        ) from error

    active_lobby_messages.pop(key, None)