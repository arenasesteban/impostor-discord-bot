import discord


def interaction_log_context(interaction: discord.Interaction) -> dict[str, object]:
    return {
        "interaction_id": interaction.id,
        "guild_id": interaction.guild_id,
        "channel_id": interaction.channel_id
    }