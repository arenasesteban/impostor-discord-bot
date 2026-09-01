import discord

from impostor_bot.discord.context import get_game_session_key
from impostor_bot.discord.error_handling import send_known_error
from impostor_bot.discord.state import (
    game_repository,
    session_lock_manager,
)

from impostor_bot.discord.error_handling import send_known_error
from impostor_bot.discord.messages import (
    build_game_created_message,
    build_player_joined_message,
    build_player_left_message,
    send_error,
)

from impostor_bot.application.join_game import JoinGame
from impostor_bot.application.leave_game import LeaveGame
from impostor_bot.application.exceptions import ApplicationError

from impostor_bot.game.player import Player
from impostor_bot.game.exceptions import GameRuleError

from impostor_bot.errors import InfrastructureError


join_game_use_case = JoinGame(
    repository=game_repository,
    lock_manager=session_lock_manager,
)

leave_game_use_case = LeaveGame(
    repository=game_repository,
    lock_manager=session_lock_manager,
)


async def handle_join_button(interaction: discord.Interaction, view: discord.ui.View, use_case: JoinGame) -> None:
    await interaction.response.defer()

    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            player=Player(
                id=interaction.user.id
            ),
        )

        if interaction.message is not None:
            await interaction.message.edit(
                content=build_game_created_message(game),
                view=view
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


async def handle_leave_button(
    interaction: discord.Interaction,
    view: discord.ui.View,
    use_case: LeaveGame,
) -> None:
    await interaction.response.defer()

    
    try:
        key = get_game_session_key(interaction)

        game = await use_case.execute(
            key=key,
            player=Player(
                id=interaction.user.id
            ),
        )

        if interaction.message is not None:
            await interaction.message.edit(
                content=build_game_created_message(game),
                view=view
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


class LobbyView(discord.ui.View):
    def __init__(self, disabled: bool = False) -> None:
        super().__init__(timeout=None)

        if disabled:
            self.disable_all_buttons()

    def disable_all_buttons(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    @discord.ui.button(
        label="Join",
        style=discord.ButtonStyle.secondary,
        row=0,
        custom_id="impostor:lobby:join:v1",
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await handle_join_button(
            interaction=interaction,
            view=self,
            use_case=join_game_use_case,
        )

    @discord.ui.button(
        label="Leave",
        style=discord.ButtonStyle.secondary,
        row=0,
        custom_id="impostor:lobby:leave:v1",
    )
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await handle_leave_button(
            interaction=interaction,
            view=self,
            use_case=leave_game_use_case,
        )
