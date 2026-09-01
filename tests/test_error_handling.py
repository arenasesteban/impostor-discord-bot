import pytest

from impostor_bot.application.exceptions import (
    GameAlreadyExistsError,
    GameNotFoundError,
    NotGameHostError,
)
from impostor_bot.discord.error_handling import (
    get_user_error_message,
)
from impostor_bot.errors import (
    DatabaseError,
    DiscordAPIError,
    WordProviderError,
)
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    HostCannotLeaveError,
    InvalidGameStateError,
    NotEnoughPlayersError,
    PlayerAlreadyJoinedError,
    PlayerNotFoundError,
)


@pytest.mark.parametrize(
    (
        "error",
        "operation",
        "expected",
    ),
    [
        (
            GameAlreadyExistsError(),
            "create",
            "There is already an open game in this channel. "
            "Use `/impostor status` to check it.",
        ),
        (
            PlayerAlreadyJoinedError(),
            "join",
            "You have already joined this game. "
            "Use `/impostor status` to see the player list.",
        ),
        (
            GameAlreadyStartedError(),
            "join",
            "You cannot join because the game has already started.",
        ),
        (
            HostCannotLeaveError(),
            "leave",
            "The host cannot leave the game. "
            "If you want to close it, use `/impostor cancel`.",
        ),
        (
            PlayerNotFoundError(),
            "leave",
            "You are not currently joined in this game.",
        ),
        (
            NotEnoughPlayersError(),
            "start",
            "The game needs at least 3 players to start. "
            "Use `/impostor status` to check the player list.",
        ),
        (
            NotGameHostError(),
            "finish",
            "Only the host can finish the game.",
        ),
        (
            InvalidGameStateError(),
            "finish",
            "Only a started game can be finished.",
        ),
    ],
)
def test_user_error_messages(
    error,
    operation,
    expected,
):
    assert get_user_error_message(
        error,
        operation=operation,
    ) == expected


@pytest.mark.parametrize(
    "error",
    [
        DatabaseError(
            "postgresql+asyncpg://user:SECRET@localhost/db "
            "SELECT * FROM games"
        ),
        DiscordAPIError(
            "HTTP 500 internal payload"
        ),
        WordProviderError(
            r"C:\Users\Name\project\data\words.json"
        ),
    ],
)
def test_infrastructure_details_are_not_exposed(
    error,
):
    message = get_user_error_message(
        error,
        operation="status",
    )

    assert "SECRET" not in message
    assert "postgresql" not in message
    assert "SELECT" not in message
    assert "C:\\" not in message
    assert "HTTP 500" not in message