import discord
from discord import app_commands

from impostor_bot.bot.commands import impostor_group


class ImpostorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(impostor_group)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot is ready. Logged in as {self.user} (ID: {self.user.id})")


def create_bot() -> ImpostorBot:
    return ImpostorBot()