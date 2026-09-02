import discord
import logging

from discord import app_commands

from impostor_bot.discord.views import LobbyView
from impostor_bot.discord.context import get_game_session_key
from impostor_bot.discord.role_delivery import deliver_roles
from impostor_bot.discord.error_handling import send_known_error
from impostor_bot.discord.state import (
    active_lobby_messages,
    game_repository,
    lobby_message_repository,
    session_lock_manager
)
from impostor_bot.discord.lobby import (
    close_lobby_message,
    refresh_lobby_message,
    update_lobby_message
)
from impostor_bot.discord.messages import (
    build_game_created_message,
    build_game_status_message,
    build_game_cancelled_message,
    build_game_started_message,
    build_game_finished_message,
    build_player_joined_message,
    build_player_left_message,
    build_lobby_started_message,
    build_lobby_cancelled_message,
    build_lobby_finished_message,
    build_dm_error_message,
    build_help_message
)

from impostor_bot.game.player import Player
from impostor_bot.game.exceptions import GameRuleError

from impostor_bot.application.create_game import CreateGame
from impostor_bot.application.start_game import StartGame
from impostor_bot.application.join_game import JoinGame
from impostor_bot.application.leave_game import LeaveGame
from impostor_bot.application.cancel_game import CancelGame
from impostor_bot.application.finish_game import FinishGame
from impostor_bot.application.get_game_status import GetGameStatus
from impostor_bot.application.exceptions import ApplicationError

from impostor_bot.infrastructure.random.python_random_selector import PythonRandomSelector
from impostor_bot.infrastructure.word_providers.static_word_provider import StaticWordProvider

from impostor_bot.ports.lobby_message_repository import LobbyMessageRepository

from impostor_bot.errors import InfrastructureError

from impostor_bot.observability.logging import log_event


logger = logging.getLogger(__name__)


word_provider = StaticWordProvider()
random_selector = PythonRandomSelector()

create_game_use_case = CreateGame(
    repository=game_repository,
    lock_manager=session_lock_manager
)

join_game_use_case = JoinGame(
    repository=game_repository,
    lock_manager=session_lock_manager
)

leave_game_use_case = LeaveGame(
    repository=game_repository,
    lock_manager=session_lock_manager
)

start_game_use_case = StartGame(
    repository=game_repository,
    word_provider=word_provider,
    random_selector=random_selector,
    lock_manager=session_lock_manager
)

finish_game_use_case = FinishGame(
    repository=game_repository,
    lock_manager=session_lock_manager
)

cancel_game_use_case = CancelGame(
    repository=game_repository,
    lock_manager=session_lock_manager
)

get_game_status_use_case = GetGameStatus(
    repository=game_repository
)


async def handle_create(interaction: discord.Interaction, use_case: CreateGame, lobby_repository: LobbyMessageRepository) -> None:
    await interaction.response.defer(
        thinking=True
    )

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            host_id=interaction.user.id
        )

        log_event(
            logger,
            "game_created",
            guild_id=key.guild_id,
            channel_id=key.channel_id
        )
        
        message = await interaction.edit_original_response(
            content=build_game_created_message(game),
            view=LobbyView()
        )

        await lobby_repository.save(
            key=key,
            message_id=message.id
        )

        active_lobby_messages[key] = message.id

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="create",
        )


async def handle_join(interaction: discord.Interaction, use_case: JoinGame) -> None:
    await interaction.response.defer(
        thinking=True,
        ephemeral=True
    ) 

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            player=Player(
                id=interaction.user.id
            )
        )

        log_event(
            logger,
            "player_joined",
            guild_id=key.guild_id,
            channel_id=key.channel_id,
            player_count=len(game.players)
        )

        await refresh_lobby_message(
            client=interaction.client,
            key=key,
            game=game,
            view=LobbyView()
        )

        await interaction.followup.send(
            build_player_joined_message(interaction.user.id, len(game.players)),
            ephemeral=True
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="join",
        )


async def handle_leave(interaction: discord.Interaction, use_case: LeaveGame) -> None:
    await interaction.response.defer(
        thinking=True,
        ephemeral=True
    ) 

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            player=Player(
                id=interaction.user.id
            )
        )

        log_event(
            logger,
            "player_left",
            guild_id=key.guild_id,
            channel_id=key.channel_id,
            player_count=len(game.players)
        )

        await refresh_lobby_message(
            client=interaction.client,
            key=key,
            game=game,
            view=LobbyView()
        )

        await interaction.followup.send(
            build_player_left_message(interaction.user.id, len(game.players)),
            ephemeral=True
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="leave",
        )


async def handle_start(interaction: discord.Interaction, use_case: StartGame, cancel_use_case: CancelGame) -> None:
    await interaction.response.defer(
        ephemeral=True,
        thinking=True
    )

    try:
        key = get_game_session_key(interaction)

        result = await use_case.execute(
            key=key,
            requester_id=interaction.user.id
        )

        log_event(
            logger,
            "game_started",
            guild_id=key.guild_id,
            channel_id=key.channel_id,
            player_count=len(result.game.players)
        )

        failed_players = await deliver_roles(
            client=interaction.client,
            roles=result.roles
        )

        disabled_view = LobbyView(
            disabled=True
        )

        if failed_players:
            cancelled_game = await cancel_use_case.execute(
                key=key,
                requester_id=interaction.user.id
            )

            log_event(
                logger,
                "game_cancelled",
                guild_id=key.guild_id,
                channel_id=key.channel_id,
                reason="role_delivery_failed",
            )

            await close_lobby_message(
                client=interaction.client,
                key=key,
                content=build_lobby_cancelled_message(cancelled_game),
                view=disabled_view
            )

            await interaction.followup.send(
                build_dm_error_message(failed_players),
                ephemeral=True
            )

            return

        await update_lobby_message(
            client=interaction.client,
            key=key,
            content=build_lobby_started_message(result.game),
            view=disabled_view
        )

        await interaction.followup.send(
            build_game_started_message(),
            ephemeral=False
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="start",
        )


async def handle_finish(interaction: discord.Interaction, use_case: FinishGame) -> None:
    await interaction.response.defer(
        thinking=True
    ) 

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            requester_id=interaction.user.id
        )

        log_event(
            logger,
            "game_finished",
            guild_id=key.guild_id,
            channel_id=key.channel_id
        )

        disabled_view = LobbyView(
            disabled=True
        )

        await close_lobby_message(
            client=interaction.client,
            key=key,
            content=build_lobby_finished_message(game),
            view=disabled_view
        )

        await interaction.followup.send(
            build_game_finished_message(),
            ephemeral=False
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="finish",
        )


async def handle_cancel(interaction: discord.Interaction, use_case: CancelGame) -> None:
    await interaction.response.defer(
        thinking=True
    ) 

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            requester_id=interaction.user.id
        )

        log_event(
            logger,
            "game_cancelled",
            guild_id=key.guild_id,
            channel_id=key.channel_id,
            reason="host_requested"
        )

        disabled_view = LobbyView(
            disabled=True
        )

        await close_lobby_message(
            client=interaction.client,
            key=key,
            content=build_lobby_cancelled_message(game),
            view=disabled_view
        )

        await interaction.followup.send(
            build_game_cancelled_message(),
            ephemeral=False
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="cancel",
        )


async def handle_status(interaction: discord.Interaction, use_case: GetGameStatus) -> None:
    await interaction.response.defer(
        ephemeral=True,
        thinking=True
    )

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key
        )

        await interaction.followup.send(
            build_game_status_message(game),
            ephemeral=True
        )

    except (ApplicationError, GameRuleError, InfrastructureError) as error:
        await send_known_error(
            interaction,
            error,
            operation="status",
        )


impostor_group = app_commands.Group(
    name="impostor",
    description="Commands for managing Impostor games."
)


@impostor_group.command(
    name="create",
    description="Create a new Impostor game in the current channel."
)
async def create(interaction: discord.Interaction):
    await handle_create(
        interaction=interaction,
        use_case=create_game_use_case,
        lobby_repository=lobby_message_repository
    )


@impostor_group.command(
    name="join",
    description="Join an active Impostor game in the current channel."
)
async def join(interaction: discord.Interaction):
    await handle_join(
        interaction=interaction,
        use_case=join_game_use_case
    )


@impostor_group.command(
    name="leave",
    description="Leave an active Impostor game in the current channel."
)
async def leave(interaction: discord.Interaction):
    await handle_leave(
        interaction=interaction,
        use_case=leave_game_use_case
    )


@impostor_group.command(
    name="start",
    description="Starts the game and sends secret roles by direct message.",
)
async def start(interaction: discord.Interaction):
    await handle_start(
        interaction=interaction,
        use_case=start_game_use_case,
        cancel_use_case=cancel_game_use_case
    )


@impostor_group.command(
    name="finish",
    description="Finishes the active Impostor game.",
)
async def finish(interaction: discord.Interaction):
    await handle_finish(
        interaction=interaction,
        use_case=finish_game_use_case
    )


@impostor_group.command(
    name="cancel",
    description="Cancels the active Impostor game.",
)
async def cancel(
    interaction: discord.Interaction,
):
    await handle_cancel(
        interaction=interaction,
        use_case=cancel_game_use_case,
    )


@impostor_group.command(
    name="status",
    description="Shows the current game status.",
)
async def status(interaction: discord.Interaction):
    await handle_status(
        interaction=interaction,
        use_case=get_game_status_use_case,
    )


@impostor_group.command(
    name="help",
    description="Shows help about how to use the bot.",
)
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        build_help_message(),
        ephemeral=True
    )