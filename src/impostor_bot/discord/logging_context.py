from typing import TypedDict

import discord


class InteractionLogContext(TypedDict):
    interaction_id: int
    guild_id: int | None
    channel_id: int | None


def interaction_log_context(
    interaction: discord.Interaction,
) -> InteractionLogContext:
    return {
        "interaction_id": interaction.id,
        "guild_id": interaction.guild_id,
        "channel_id": interaction.channel_id,
    }