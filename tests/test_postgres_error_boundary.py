import pytest

from sqlalchemy.exc import OperationalError
from impostor_bot.errors.infrastructure import (
    DatabaseUnavailableError,
    DatabaseError,
)
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.repositories.postgres_game_repository import PostgresGameRepository

class FailingSessionContext:
    def __init__(
        self,
        error,
    ):
        self.error = error

    async def __aenter__(self):
        raise self.error

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


def failing_session_factory(
    error,
):
    def factory():
        return FailingSessionContext(
            error
        )

    return factory


@pytest.mark.asyncio
async def test_game_repository_translates_database_failure():
    source_error = OperationalError(
        "SELECT 1",
        {},
        Exception(
            "connection refused"
        ),
    )

    repository = PostgresGameRepository(
        failing_session_factory(
            source_error
        )
    )

    key = GameSessionKey(
        guild_id=100,
        channel_id=200,
    )

    with pytest.raises(
        DatabaseUnavailableError
    ) as exc_info:
        await repository.get(
            key
        )

    assert (
        exc_info.value.__cause__
        is source_error
    )