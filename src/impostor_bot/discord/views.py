import discord

from impostor_bot.discord.messages import (
    build_game_created_message,
    send_error,
)
from impostor_bot.discord.state import active_games
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    GameError,
    HostCannotLeaveError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
)


class LobbyView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=1800)
        self.channel_id = channel_id

    @discord.ui.button(
        label="Join",
        style=discord.ButtonStyle.success,
        emoji="✅",
    )
    async def join_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        game = active_games.get(self.channel_id)

        if game is None:
            await send_error(
                interaction,
                "This game is no longer available.",
            )
            return

        try:
            game.add_player(interaction.user.id)

            await interaction.response.edit_message(
                content=build_game_created_message(game),
                view=self,
            )

        except PlayerAlreadyJoinedError:
            await send_error(
                interaction,
                "You have already joined this game.",
            )

        except GameAlreadyStartedError:
            await send_error(
                interaction,
                "You cannot join because the game has already started.",
            )

        except GameError as error:
            await send_error(interaction, str(error))

    @discord.ui.button(
        label="Leave",
        style=discord.ButtonStyle.secondary,
        emoji="🚪",
    )
    async def leave_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        game = active_games.get(self.channel_id)

        if game is None:
            await send_error(
                interaction,
                "This game is no longer available.",
            )
            return

        try:
            game.remove_player(interaction.user.id)

            await interaction.response.edit_message(
                content=build_game_created_message(game),
                view=self,
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