import pytest
from sqlalchemy.exc import (
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)

from impostor_bot.errors.infrastructure import (
    DatabaseError,
    DatabaseUnavailableError,
)
from impostor_bot.game.session_key import GameSessionKey
from impostor_bot.infrastructure.database.error_translation import (
    translate_database_error,
)
from impostor_bot.infrastructure.repositories.postgres_game_repository import (
    PostgresGameRepository,
)


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



def test_connection_refused_error_becomes_database_unavailable():
    source = ConnectionRefusedError(
        1225,
        "Connection refused",
    )

    translated = (
        translate_database_error(
            source
        )
    )

    assert isinstance(
        translated,
        DatabaseUnavailableError,
    )


@pytest.mark.parametrize(
    "error",
    [
        OperationalError(
            statement="SELECT 1",
            params={},
            orig=Exception("Connection failed"),
        ),
        InterfaceError(
            statement="SELECT 1",
            params={},
            orig=Exception("Connection refused"),
        ),
    ]
)
def test_connection_errors_become_database_unavailable(error):
    result = translate_database_error(
        error
    )

    assert isinstance(
        result,
        DatabaseUnavailableError,
    )


def test_generic_sqlalchemy_error_becomes_database_error():
    error = SQLAlchemyError(
        "Unexpected database error"
    )

    result = translate_database_error(
        error
    )

    assert isinstance(
        result,
        DatabaseError,
    )


@pytest.mark.asyncio
async def test_game_repository_translates_operational_error_to_database_unavailable():
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
