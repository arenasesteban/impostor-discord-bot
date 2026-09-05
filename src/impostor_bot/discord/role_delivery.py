import discord

from impostor_bot.constants import IMPOSTOR_ROLE
from impostor_bot.discord.messages import (
    send_impostor_dm,
    send_normal_player_dm,
)
from impostor_bot.errors.infrastructure import DiscordAPIError


async def deliver_roles(client: discord.Client, roles: dict[int, str]) -> list[int]:
    failed_players: list[int] = []

    for player_id, role in roles.items():
        try:
            user = await client.fetch_user(player_id)

            if role == IMPOSTOR_ROLE:
                await send_impostor_dm(user)
            else:
                await send_normal_player_dm(user, role)

        except (discord.Forbidden, discord.NotFound):
            failed_players.append(player_id)

        except discord.HTTPException as error:
            raise DiscordAPIError(
                "Discord role delivery failed."
            ) from error

    return failed_players
