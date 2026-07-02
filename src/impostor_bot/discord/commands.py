import discord
from discord import app_commands


from impostor_bot.constants import IMPOSTOR_ROLE
from impostor_bot.discord.messages import (
    build_dm_error_message,
    build_game_cancelled_message,
    build_game_created_message,
    build_game_started_message,
    build_game_status_message,
    build_help_message,
    build_player_joined_message,
    build_player_left_message,
    send_error,
    send_impostor_dm,
    send_normal_player_dm,
)
from impostor_bot.discord.state import active_games
from impostor_bot.discord.views import LobbyView
from impostor_bot.constants import IMPOSTOR_ROLE
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    GameError,
    HostCannotLeaveError,
    NotEnoughPlayersError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
)
from impostor_bot.game.session import Session
from impostor_bot.words.exceptions import WordError
from impostor_bot.words.loader import get_random_word


impostor_group = app_commands.Group(
    name="impostor",
    description="Commands for managing Impostor games.",
)


def get_channel_id(interaction: discord.Interaction) -> int:
    if interaction.channel is None:
        raise GameError("This command can only be used inside a server channel.")
    
    return interaction.channel.id


@impostor_group.command(
    name="create",
    description="Create a new Impostor game in the current channel."
)
async def create(interaction: discord.Interaction):
    try:

        channel_id = get_channel_id(interaction)
        host_id = interaction.user.id

        if channel_id in active_games:
            await send_error(
                interaction,
                "There is already an open game in this channel. "
                "Use `/impostor estado` to check it.",
            )
            return

        game = Session(host_id=host_id)
        active_games[channel_id] = game

        view = LobbyView(channel_id=channel_id)

        await interaction.response.send_message(
            content=build_game_created_message(host_id),
            view=view
        )

    except GameError as error:
        await interaction.response.send_message(
            f"[ERROR] {error}",
            ephemeral=True
        )


@impostor_group.command( 
    name="join",
    description="Join an active Impostor game in the current channel."
)
async def join(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        player_id = interaction.user.id

        game = active_games.get(channel_id)

        if game is None:
            await send_error(
                interaction,
                "There is no open game in this channel. "
                "Use `/impostor crear` to create one.",
            )
            return
        
        game.add_player(player_id)

        await interaction.response.send_message(
            build_player_joined_message(player_id, len(game.players))
        )

    except PlayerAlreadyJoinedError:
        await send_error(
            interaction,
            "You have already joined this game. "
            "Use `/impostor estado` to see the player list.",
        )

    except GameAlreadyStartedError:
        await send_error(
            interaction,
            "You cannot join because the game has already started.",
        )

    except GameError as error:
        await send_error(interaction, str(error))


@impostor_group.command(
    name="leave",
    description="Leave an active Impostor game in the current channel."
)
async def leave(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        player_id = interaction.user.id

        game = active_games.get(channel_id)

        if game is None:
            await send_error(
                interaction,
                "There is no open game in this channel.",
            )
            return

        game.remove_player(player_id)

        await interaction.response.send_message(
            build_player_left_message(player_id, len(game.players))
        )

    except HostCannotLeaveError:
        await send_error(
            interaction,
            "The host cannot leave the game. "
            "If you want to close it, use `/impostor cancelar`.",
        )

    except PlayerNotFoundError:
        await send_error(
            interaction,
            "You are not currently joined in this game.",
        )

    except GameAlreadyStartedError:
        await send_error(
            interaction,
            "You cannot leave because the game has already started.",
        )

    except GameError as error:
        await send_error(interaction, str(error))


async def status(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        game = active_games.get(channel_id)

        if game is None:
            await send_error(
                interaction,
                "There is no open game in this channel. "
                "Use `/impostor crear` to create one.",
            )
            return
        
        await interaction.response.send_message(
            build_game_status_message(game)
        )

    except GameError as error:
        await send_error(interaction, str(error))


@impostor_group.command(
    name="cancel",
    description="Cancel the Impostor game in the current channel."
)
async def cancel(interaction: discord.Interaction):
    try:
        channel_id = get_channel_id(interaction)
        user_id = interaction.user.id

        game = active_games.get(channel_id)

        if game is None:
            await send_error(
                interaction,
                "There is no open game in this channel.",
            )
            return

        if user_id != game.host_id:
            await send_error(
                interaction,
                "Only the host can cancel the game.",
            )
            return

        game.cancel()
        del active_games[channel_id]

        await interaction.response.send_message(
            build_game_cancelled_message()
        )

    except GameAlreadyStartedError:
        await send_error(
            interaction,
            "A game that has already started cannot be cancelled.",
        )

    except GameError as error:
        await send_error(interaction, str(error))


@impostor_group.command(
    name="start",
    description="Start the Impostor game in the current channel."
)
async def start(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    try:
        channel_id = get_channel_id(interaction)
        user_id = interaction.user.id

        game = active_games.get(channel_id)

        if game is None:
            await send_error(
                interaction,
                "There is no open game in this channel.",
            )
            return

        if user_id != game.host_id:
            await send_error(
                interaction,
                "Only the host can start the game.",
            )
            return

        secret_word = get_random_word()
        roles = game.start_game(secret_word)

        failed_players: list[int] = []

        for player_id, role in roles.items():
            user = await interaction.client.fetch_user(player_id)

            try:
                if role == IMPOSTOR_ROLE:
                    await send_impostor_dm(user)
                else:
                    await send_normal_player_dm(user, role)

            except discord.Forbidden:
                failed_players.append(player_id)

        if failed_players:
            await interaction.response.send_message(
                build_dm_error_message(failed_players)
            )

            del active_games[channel_id]
            return
        
        del active_games[channel_id]

        await interaction.response.send_message(
            build_game_started_message()
        )

    except NotEnoughPlayersError:
        await send_error(
            interaction,
            "The game needs at least 3 players to start. "
            "Use `/impostor estado` to check the player list.",
        )

    except WordError as error:
        await send_error(interaction, str(error))

    except GameAlreadyStartedError:
        await send_error(
            interaction,
            "This game has already started or is no longer available.",
        )

    except GameError as error:
        await send_error(interaction, str(error))


@impostor_group.command(
    name="help",
    description="Shows help about how to use the bot.",
)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        build_help_message(),
        ephemeral=True,
    )