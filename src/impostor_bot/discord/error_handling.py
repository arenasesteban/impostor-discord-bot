import discord

from impostor_bot.discord.messages import (
    build_service_error_message,
    send_error,
)

from impostor_bot.errors.infrastructure import InfrastructureError


async def handle_infrastructure_error(interaction: discord.Interaction, error: InfrastructureError) -> None:
    del error

    await send_error(
        interaction, 
        build_service_error_message()
    )