import discord

from impostor_bot.errors.infrastructure import (
    InfrastructureError,
    DatabaseError,
    DatabaseUnavailableError,
    DiscordAPIError,
    WordProviderError
)

from impostor_bot.discord.messages import (
    send_error
)


def get_safe_error_message(error: InfrastructureError) -> str:
    if isinstance(error, WordProviderError):
        return (
            "I could not prepare a word "
            "for the game. Please try again."
        )

    if isinstance(error, DatabaseError):
        return (
            "The game service is temporarily "
            "unavailable. Please try again."
        )

    if isinstance(error, DiscordAPIError):
        return (
            "Discord could not complete that "
            "action. Please try again."
        )

    if isinstance(error, DatabaseUnavailableError):
        return (
            "The database is currently "
            "unavailable. Please try again."
        )

    return (
        "A technical problem occurred. "
        "Please try again."
    )


async def send_infrastructure_error(interaction: discord.Interaction, error: InfrastructureError) -> None:
    await send_error(interaction, get_safe_error_message(error))
