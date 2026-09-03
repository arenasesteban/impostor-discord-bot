import discord
import logging

from typing import Literal, TypeAlias

from impostor_bot.discord.messages import send_error
from impostor_bot.discord.logging_context import interaction_log_context

from impostor_bot.application.exceptions import (
    ApplicationError,
    GameAlreadyExistsError,
    GameNotFoundError,
    NotGameHostError
)

from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    GameRuleError,
    HostCannotLeaveError,
    InvalidGameStateError,
    NotEnoughPlayersError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
    GameInvariantError
)

from impostor_bot.errors import (
    DatabaseError,
    DiscordAPIError,
    InfrastructureError,
    WordProviderError
)

from impostor_bot.observability.logging import log_error


ErrorOperation: TypeAlias = Literal[
    "create",
    "join",
    "leave",
    "start",
    "finish",
    "cancel",
    "status"
]

KnownUserError: TypeAlias = (
    ApplicationError
    | GameRuleError
    | InfrastructureError
)


logger = logging.getLogger(__name__)


def get_user_error_message(error: KnownUserError, *, operation: ErrorOperation) -> str:
    if isinstance(error, InfrastructureError):
        return _get_infrastructure_error_message(
            error
        )

    if isinstance(error, ApplicationError):
        return _get_application_error_message(
            error,
            operation=operation
        )

    return _get_game_rule_error_message(
        error,
        operation=operation
    )

async def handle_known_error(interaction: discord.Interaction, error: KnownUserError, *, operation: ErrorOperation) -> None:
    _log_known_error(interaction, error)

    message = get_user_error_message(error, operation=operation)

    await send_error(interaction, message)


async def handle_unexpected_error(interaction: discord.Interaction, error: BaseException) -> None:
    log_error(
        logger,
        "unexpected_error",
        error,
        **interaction_log_context(
            interaction
        ),
    )

    await send_error(
        interaction,
        (
            "An unexpected problem occurred. "
            "Please try again."
        ),
    )


def _get_infrastructure_error_message(error: InfrastructureError) -> str:
    if isinstance(error, WordProviderError):
        return (
            "I could not prepare a word for the game. "
            "Please try again."
        )

    if isinstance(error, DatabaseError):
        return (
            "The game service is temporarily unavailable. "
            "Please try again."
        )

    if isinstance(error, DiscordAPIError):
        return (
            "Discord could not complete that action. "
            "Please try again."
        )

    return (
        "A technical problem occurred. "
        "Please try again."
    )


def _get_application_error_message(error: ApplicationError, *, operation: ErrorOperation) -> str:
    if isinstance(error, GameAlreadyExistsError):
        return (
            "There is already an open game in this channel. "
            "Use `/impostor status` to check it."
        )

    if isinstance(error, GameNotFoundError):
        if operation == "status":
            return (
                "There is no active game in this channel. "
                "Use `/impostor create` to create one."
            )

        if operation in {
            "join",
            "leave",
            "start",
        }:
            return (
                "There is no open game in this channel."
            )

        return (
            "There is no active game in this channel."
        )

    if isinstance(error, NotGameHostError):
        action = {
            "start": "start",
            "finish": "finish",
            "cancel": "cancel"
        }.get(operation)

        if action is not None:
            return (
                f"Only the host can {action} the game."
            )

        return (
            "Only the host can perform this action."
        )

    return (
        "The operation could not be completed."
    )


def _get_game_rule_error_message(error: GameRuleError, *, operation: ErrorOperation) -> str:
    if isinstance(error, PlayerAlreadyJoinedError):
        return (
            "You have already joined this game. "
            "Use `/impostor status` to see the player list."
        )

    if isinstance(error, HostCannotLeaveError):
        return (
            "The host cannot leave the game. "
            "If you want to close it, use `/impostor cancel`."
        )

    if isinstance(error, PlayerNotFoundError):
        return (
            "You are not currently joined in this game."
        )

    if isinstance(error, NotEnoughPlayersError):
        return (
            "The game needs at least 3 players to start. "
            "Use `/impostor status` to check the player list."
        )

    if isinstance(error, GameAlreadyStartedError):
        if operation == "join":
            return (
                "You cannot join because the game "
                "has already started."
            )

        if operation == "leave":
            return (
                "You cannot leave because the game "
                "has already started."
            )

        if operation == "start":
            return (
                "This game has already started "
                "or is no longer available."
            )

        return (
            "This operation is not available "
            "after the game has started."
        )

    if isinstance(error, InvalidGameStateError):
        if operation == "finish":
            return (
                "Only a started game can be finished."
            )

        if operation == "cancel":
            return (
                "This game can no longer be cancelled."
            )

        return (
            "This operation is not valid "
            "for the current game state."
        )

    return (
        "The game could not complete this operation."
    )


def _log_known_error(interaction, error: Exception) -> None:
    context = interaction_log_context(interaction)

    if isinstance(error, DatabaseError):
        log_error(
            logger,
            "database_error",
            error,
            **context,
        )
        return

    if isinstance(error, DiscordAPIError):
        log_error(
            logger,
            "discord_api_error",
            error,
            **context,
        )
        return

    if isinstance(error, WordProviderError):
        log_error(
            logger,
            "word_provider_error",
            error,
            **context,
        )
        return

    if isinstance(error, GameInvariantError):
        log_error(
            logger,
            "game_invariant_error",
            error,
            **context,
        )
