import discord
from discord import app_commands

from config import DISCORD_TOKEN
from game.session import Session
from game.exceptions import (
    GameError,
    GameAlreadyStartedError, 
    PlayerAlreadyJoinedError,
    HostCannotLeaveError,
    PlayerNotFoundError
)


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

active_sessions: dict[int, Session] = {}


def format_player_list(player_ids: list[int]) -> str:
    if not player_ids:
        return "No players have joined yet."
    
    return "\n".join(f"- <@{player_id}>" for player_id in player_ids)


def get_channel_id(interaction: discord.Interaction) -> int:
    if interaction.channel is None:
        raise GameError("This command can only be used in a server channel.")
    
    return interaction.channel.id


impostor_group = app_commands.Group(
    name="impostor",
    description="Commands for managing the Impostor game sessions.",
)


@impostor_group.command(
    name="create",
    description="Create a new Impostor game session in the current channel."
)
async def create(interaction: discord.Interaction):
    try:

        channel_id = get_channel_id(interaction)
        host_id = interaction.user.id

        if channel_id in active_sessions:
            await interaction.response.send_message(
                "A game session is already active in this channel.",
                ephemeral=True
            )
            return

        game = Session(host_id=host_id)
        active_sessions[channel_id] = game

        await interaction.response.send_message(
            "**🎭 Impostor game session created!**\n\n"
            f"Host: <@{host_id}>\n\n"
            "Players can join the game using the `/impostor join` command.\n"
            "The host can start the game using the `/impostor start` command."
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


@impostor_group.command( 
    name="join",
    description="Join an active Impostor game session in the current channel."
)
async def join(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        player_id = interaction.user.id

        game = active_sessions.get(channel_id)

        if game is None:
            await interaction.response.send_message(
                "No active game session found in this channel.",
                ephemeral=True
            )
            return
        
        game.add_player(player_id)

        await interaction.response.send_message(
            f"✅ <@{player_id}> has joined the game!\n\n"
            f"Current players: **{len(game.players)}**"
        )

    except PlayerAlreadyJoinedError:
        await interaction.response.send_message(
            "You have already joined the game.",
            ephemeral=True
        )

    except GameAlreadyStartedError:
        await interaction.response.send_message(
            "The game has already started. You cannot join now.",
            ephemeral=True
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


@impostor_group.command(
    name="leave",
    description="Leave an active Impostor game session in the current channel."
)
async def leave(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        player_id = interaction.user.id

        game = active_sessions.get(channel_id)

        if game is None:
            await interaction.response.send_message(
                "No active game session found in this channel.",
                ephemeral=True
            )
            return

        game.remove_player(player_id)

        await interaction.response.send_message(
            f"🚪 <@{player_id}> has left the game!\n\n"
            f"Current players: **{len(game.players)}**"
        )

    except HostCannotLeaveError:
        await interaction.response.send_message(
            "The host cannot leave the game. Use `/impostor cancel` to end the session.",
            ephemeral=True
        )

    except PlayerNotFoundError:
        await interaction.response.send_message(
            "You are not in the game.",
            ephemeral=True
        )
    
    except GameAlreadyStartedError:
        await interaction.response.send_message(
            "The game has already started. You cannot leave now.",
            ephemeral=True
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


@impostor_group.command(
    name="status",
    description="Show the current status of the Impostor game session in the current channel."
)
async def status(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        game = active_sessions.get(channel_id)

        if game is None:
            await interaction.response.send_message(
                "No active game session found in this channel.",
                ephemeral=True
            )
            return

        player_list = format_player_list(game.players)

        await interaction.response.send_message(
            f"**🎭 Impostor Game Session Status**\n\n"
            f"Status: {game.status}\n"
            f"Host: <@{game.host_id}>\n"
            f"Current Players **{len(game.players)}**\n\n"
            f"{player_list}"
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


@impostor_group.command(
    name="cancel",
    description="Cancel the Impostor game session in the current channel."
)
async def cancel(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        player_id = interaction.user.id

        game = active_sessions.get(channel_id)

        if game is None:
            await interaction.response.send_message(
                "No active game session found in this channel.",
                ephemeral=True
            )
            return

        if player_id != game.host_id:
            await interaction.response.send_message(
                "Only the host can cancel the game session.",
                ephemeral=True
            )
            return

        game.cancel()
        del active_sessions[channel_id]

        await interaction.response.send_message(
            "**❌ Impostor game session has been canceled by the host.**"
        )

    except GameAlreadyStartedError:
        await interaction.response.send_message(
            "The game has already started. You cannot cancel it now.",
            ephemeral=True
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


bot = ImpostorBot()


@bot.tree.command(
    name="ping", 
    description="Check if the bot is alive."
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong!")


bot.run(DISCORD_TOKEN)