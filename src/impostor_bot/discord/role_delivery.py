import discord

from impostor_bot.constants import IMPOSTOR_ROLE
from impostor_bot.discord.messages import (
    send_impostor_dm,
    send_normal_player_dm,
)


async def deliver_roles(client: discord.Client, roles: dict[int, str]) -> list[int]:
    failed_players: list[int] = []

    for player_id, role in roles.items():
        user = await client.fetch_user(player_id)

        try:
            if role == IMPOSTOR_ROLE:
                await send_impostor_dm(user)
            else:
                await send_normal_player_dm(user, role)

        except discord.Forbidden:
            failed_players.append(player_id)

    return failed_players