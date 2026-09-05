from impostor_bot.application.exceptions import (
    ApplicationError,
    GameAlreadyExistsError,
    GameNotFoundError,
    NotGameHostError,
)
from impostor_bot.errors import (
    DatabaseError,
    DatabaseUnavailableError,
    DiscordAPIError,
    InfrastructureError,
    WordProviderError,
)
from impostor_bot.game.exceptions import (
    GameAlreadyStartedError,
    GameError,
    GameInvariantError,
    GameRuleError,
    InvalidGameStateError,
)


def test_application_errors_share_base():
    assert issubclass(
        GameAlreadyExistsError,
        ApplicationError,
    )
    assert issubclass(
        GameNotFoundError,
        ApplicationError,
    )
    assert issubclass(
        NotGameHostError,
        ApplicationError,
    )


def test_game_started_is_invalid_state():
    assert issubclass(
        GameAlreadyStartedError,
        InvalidGameStateError,
    )


def test_game_rule_errors_are_game_errors():
    assert issubclass(
        GameRuleError,
        GameError,
    )


def test_game_invariant_is_not_a_rule_error():
    assert issubclass(
        GameInvariantError,
        GameError,
    )

    assert not issubclass(
        GameInvariantError,
        GameRuleError,
    )
