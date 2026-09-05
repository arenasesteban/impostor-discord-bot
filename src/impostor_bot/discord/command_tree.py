import discord
from discord import app_commands

from impostor_bot.discord.error_handling import handle_unexpected_error


class ImpostorCommandTree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        original_error: BaseException = error

        if isinstance(error, app_commands.CommandInvokeError):
            original_error = error.original

        await handle_unexpected_error(interaction, original_error)
