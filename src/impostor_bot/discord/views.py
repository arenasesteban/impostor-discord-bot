import discord

from impostor_bot.discord.lobby import join_lobby, leave_lobby
from impostor_bot.discord.messages import (
    build_game_created_message,
    build_player_joined_message,
    build_player_left_message,
    send_error,
)
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    GameError,
    HostCannotLeaveError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
)


class LobbyView(discord.ui.View):
    def __init__(self, channel_id: int, disabled: bool = False):
        super().__init__(timeout=1800)
        self.channel_id = channel_id

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
    )
    async def join_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        try:
            game = join_lobby(
                channel_id=self.channel_id,
                player_id=interaction.user.id,
            )

            await interaction.response.edit_message(
                content=build_game_created_message(game),
                view=self,
            )

            await interaction.followup.send(
                build_player_joined_message(
                    interaction.user.id,
                    len(game.players),
                ),
                ephemeral=True,
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
        row=0,
    )
    async def leave_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        try:
            game = leave_lobby(
                channel_id=self.channel_id,
                player_id=interaction.user.id,
            )

            await interaction.response.edit_message(
                content=build_game_created_message(game),
                view=self,
            )

            await interaction.followup.send(
                build_player_left_message(
                    interaction.user.id,
                    len(game.players),
                ),
                ephemeral=True,
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