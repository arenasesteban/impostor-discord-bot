import discord

from impostor_bot.game.exceptions import GameError
from impostor_bot.game.session_key import GameSessionKey


def get_channel_id(interaction: discord.Interaction) -> int:
    if interaction.channel is None:
        raise GameError(
            "This command can only be used inside a server channel."
        )
    
    return interaction.channel.id


def get_game_session_key(interaction: discord.Interaction) -> GameSessionKey:
    channel_id = get_channel_id(interaction)

    if interaction.guild_id is None:
        raise GameError(
            "This command can only be used inside a Discord server."
        )

    return GameSessionKey(
        guild_id=interaction.guild_id,
        channel_id=channel_id,
    )